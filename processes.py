# !python3
# -*- coding: utf-8 -*-

from multiprocessing import Process
from requests_futures.sessions import FuturesSession
import asyncio
import requests
import wget
import os


class AuthWorker:
    def __init__(self, page: any, username: str, password: str, captcha: str) -> None:
        self.page = page
        self.username = username
        self.password = password
        self.captcha = captcha
        self.run()

    def run(self) -> None:
        asyncio.get_event_loop().run_until_complete(self.login())
        print('Authentication finished - Thread 1: "AuthWorker()" destroyed.')

    async def login(self) -> None:
        focusInput = await self.page.waitForXPath('//*[@id="overlay-box"]/div[1]/form/div[1]/input')
        await focusInput.type(self.username)
        focusInput = await self.page.waitForXPath('//*[@id="overlay-box"]/div[1]/form/div[2]/input')
        await focusInput.type(self.password)
        focusInput = await self.page.waitForXPath('//*[@id="overlay-box"]/div[1]/form/div[4]/input[1]')
        await focusInput.type(self.captcha)
        focusInput = await self.page.waitForXPath('//*[@id="login-button"]')
        await focusInput.click()
        await asyncio.sleep(1)


class IdScraper:
    def __init__(self, queue: any, browser: any, page: any, username: str) -> None:
        self.queue = queue
        self.browser = browser
        self.page = page
        self.username = username
        self.ua = None
        self.cookies = None
        self.run()

    def run(self) -> None:
        async def setVars():
            self.ua = await self.browser.userAgent()
            self.cookies = await self.page.cookies()
        asyncio.get_event_loop().run_until_complete(setVars())
        if os.path.isfile("logfile.txt"):
            asyncio.get_event_loop().run_until_complete(self.readLogfile())
        else:
            asyncio.get_event_loop().run_until_complete(self.writeLogfile())

    def getFirstItems(self) -> requests.get:
        return requests.get("https://pr0gramm.com/api/items/get",
                            params={"flags": "9", "likes": self.username, "self": "true"},
                            headers={"accept": "application/json",
                                     "user-agent": self.ua,
                                     "referer": "https://pr0gramm.com/user/{}/likes".format(self.username)},
                            cookies={self.cookies[-1].get("name"): self.cookies[-1].get("value")})

    async def writeLogfile(self) -> None:
        with open("logfile.txt", "w+") as fout:

            data = self.getFirstItems()
            if not data.status_code == requests.codes.ok:
                raise Exception('Request rejected by server, please restart the program and try again.')

            ids = ["{}:{}".format(n["id"], n["image"]) for n in data.json()["items"]]
            for item in ids:
                fout.write("{}{}".format(item, "\n"))
                self.queue.put(item.split(":")[1].strip())

            try:
                while len(data.json()["items"]) > 0:
                    with FuturesSession(max_workers=4) as session:

                        data = session.get("https://pr0gramm.com/api/items/get",
                                           params={"older": str(int(ids[-1].split(":")[0]) - 120), "flags": "9",
                                                   "likes": self.username, "self": "true"},
                                           headers={"accept": "application/json", "user-agent": self.ua,
                                                    "referer": "https://pr0gramm.com/user/{}/likes".format(
                                                        self.username)},
                                           cookies={self.cookies[-1].get("name"): self.cookies[-1].get("value")})
                        data = data.result()

                        ids = ["{}:{}".format(n["id"], n["image"]) for n in data.json()["items"]]
                        for item in ids:
                            fout.write("{}{}".format(item, "\n"))
                            self.queue.put(item.split(":")[1].strip())

            finally:
                print('Service "IdScraper" finished. Thread destroyed.')
                return

    async def readLogfile(self) -> None:

        with open("logfile.txt", "r+") as fin:
            data = self.getFirstItems().json()["items"]
            id, img = [[str(n["id"]) for n in data], [str(n["image"]) for n in data]]
            elems = [n.split(":")[1].strip() for n in fin.readlines()]
            for item in [n for n in img if n not in elems]:
                self.queue.put(item)


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
