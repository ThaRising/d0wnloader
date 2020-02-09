# !python3
# -*- coding: utf-8 -*-

import multiprocessing
from requests_futures.sessions import FuturesSession
from pathlib import Path
from asyncio import get_event_loop
import requests
import wget
import os
import services
import threading


class IdScraper:
    def __init__(self, queue: multiprocessing.Queue, browser: any, username: str) -> None:
        self.queue = queue
        self.browser = browser
        self.username = username
        self.running: bool = True
        self.thread = threading.Thread(target=self.run)

    def run(self) -> None:
        """Either creates a new logfile or reads an existing one"""
        if os.path.isfile("logfile.txt"):
            get_event_loop().run_until_complete(self.getItemsNotInLog())
        else:
            Path('logfile.txt').touch()
            get_event_loop().run_until_complete(self.getAllItems())

    async def getAllItems(self) -> None:
        """Asynchronously requests all user favorite posts from the API"""
        with FuturesSession(max_workers=1) as session:
            lastId = self.filterData(
                services.getFirstItems(session, self.username, self.browser.ua, self.browser.cookies))
        try:
            while len(data.json()["items"]) > 0:
                with FuturesSession(max_workers=1) as session:
                    data = services.getItemsOlderThanX(
                        session, lastId, self.username, self.browser.ua, self.browser.cookies)
                    if not data.status_code == requests.codes.ok:
                        raise Exception('Request rejected by server, please restart the program and try again.')
                    lastId = self.filterData(data)
        finally:
            print('Service "IdScraper" finished. Thread destroyed.')
            return

    async def getItemsNotInLog(self) -> None:
        """Asynchronously requests all user favorite posts not already in the logfile"""
        with open("logfile.txt", "r+") as fin:
            with FuturesSession(max_workers=1) as session:
                data = services.getFirstItems(
                    session, self.username, self.browser.ua, self.browser.cookies).json()["items"]
            lastId = self.checkDifferentials(data, fin)
            try:
                with FuturesSession(max_workers=1) as session:
                    while len(data.json()["items"]) > 0:
                        data = services.getItemsOlderThanX(
                            session, lastId, self.username, self.browser.ua, self.browser.cookies)
                        lastId = self.checkDifferentials(data, fin)
            finally:
                print('Service "IdScraper" finished. Thread destroyed.')
                return

    def filterData(self, data: requests.get) -> int:
        """Filters data from requests into image names and ids and writes them into logfile"""
        ids, imageNames = [[str(n["id"]) for n in data.json()["items"]],
                           [n["image"] for n in data.json()["items"]]]
        for images in imageNames:
            self.queue.put(images)
        self.writeLogfile(ids, imageNames)
        return int(ids[-1])

    def checkDifferentials(self, requestedData: requests.get, fileIn: any) -> int:
        """Compares requested data to data from existing logfile to find posts that still need to downloaded"""
        ids, imageNames = [[str(n["id"]) for n in requestedData],
                           [str(n["image"]) for n in requestedData]]
        logfileIds = [n.split(":")[0].strip() for n in fileIn.readlines()]
        differentialIds, differentialImgs = [[n for n, m in zip(ids, imageNames) if n not in logfileIds],
                                             [m for n, m in zip(ids, imageNames) if n not in logfileIds]]
        for imgNames in differentialImgs:
            self.queue.put(imgNames)
        self.writeLogfile(differentialIds, differentialImgs)
        return int(logfileIds[-1])

    @staticmethod
    def writeLogfile(ids: list, imageNames: list) -> None:
        """Write data to logfile"""
        with open("logfile.txt", "a") as fout:
            for thisId, thisImage in zip(ids, imageNames):
                fout.write("{}:{}{}".format(thisId, thisImage, "\n"))


class DownloadWorker(multiprocessing.Process):
    def __init__(self, queue: multiprocessing.Queue) -> None:
        self.queue = queue
        super(DownloadWorker, self).__init__()

    def run(self) -> None:
        while True:
            if not self.queue.empty():
                break
        while not self.queue.empty():
            wget.download("{}/{}".format("https://img.pr0gramm.com", self.queue.get()))
