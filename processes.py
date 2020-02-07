# !python3
# -*- coding: utf-8 -*-

from multiprocessing.context import Process
from requests_futures.sessions import FuturesSession
from pathlib import Path
import asyncio
import requests
import wget
import os
import services


class IdScraper:
    def __init__(self, queue: any) -> None:
        self.queue = queue
        self.run()

    def run(self) -> None:
        asyncio.get_event_loop().run_until_complete(self.setVars())
        if os.path.isfile("logfile.txt"):
            asyncio.get_event_loop().run_until_complete(self.getItemsNotInLog())
        else:
            Path('logfile.txt').touch()
            asyncio.get_event_loop().run_until_complete(self.getAllItems())

    def filterData(self, data: requests.get) -> int:
        ids, imageNames = [[str(n["id"]) for n in data.json()["items"]], [n["image"] for n in data.json()["items"]]]
        for images in imageNames:
            self.queue.put(images)
        with open("logfile.txt", "a") as fout:
            for thisId in ids:
                fout.write("{}{}".format(thisId, "\n"))
        return int(ids[-1])

    async def getAllItems(self) -> None:
        lastId = self.filterData(self.getFirstItems())
        try:
            while len(data.json()["items"]) > 0:
                with FuturesSession(max_workers=4) as session:
                    data = self.getItemsOlderThanX(session, lastId)
                    if not data.status_code == requests.codes.ok:
                        raise Exception('Request rejected by server, please restart the program and try again.')
                    lastId = self.filterData(data)
        finally:
            print('Service "IdScraper" finished. Thread destroyed.')
            return

    def checkDifferentials(self, requestedData: requests.get, fileIn: any) -> int:
        ids, imageNames = [[str(n["id"]) for n in requestedData], [str(n["image"]) for n in requestedData]]
        logfileIds = [n.strip() for n in fileIn.readlines()]
        differentialIds, differentialImgs = [[n for n, m in zip(ids, imageNames) if n not in logfileIds],
                                             [m for n, m in zip(ids, imageNames) if n not in logfileIds]]
        for imgNames in differentialImgs:
            self.queue.put(imgNames)
        with open("logfile.txt", "a") as fout:
            for ids in differentialIds:
                fout.write("{}{}".format(ids, "\n"))
        return int(logfileIds[-1])

    async def getItemsNotInLog(self) -> None:
        with open("logfile.txt", "r+") as fin:
            data = self.getFirstItems().json()["items"]
            lastId = self.checkDifferentials(data, fin)
            try:
                with FuturesSession(max_workers=4) as session:
                    while len(data.json()["items"]) > 0:
                        data = self.getItemsOlderThanX(session, lastId)
                        lastId = self.checkDifferentials(data, fin)
            finally:
                print('Service "IdScraper" finished. Thread destroyed.')
                return


class DownloadWorker(Process):
    def __init__(self, queue: any) -> None:
        self.queue = queue
        super(DownloadWorker, self).__init__()

    def run(self) -> None:
        while True:
            if not self.queue.empty():
                break
        while not self.queue.empty():
            wget.download("{}/{}".format("https://img.pr0gramm.com", self.queue.get()))
