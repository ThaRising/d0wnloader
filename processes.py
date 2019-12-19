# !python3
# -*- coding: utf-8 -*-

from multiprocessing import Process
from requests_futures.sessions import FuturesSession
import asyncio
import requests
import wget
import os


class AuthWorker():
    def __init__(self, page):
        self.page = page

    async def login(self, username, password, captcha):
        focusInput = await self.page.waitForXPath('//*[@id="overlay-box"]/div[1]/form/div[1]/input')
        await focusInput.type(username)
        focusInput = await self.page.waitForXPath('//*[@id="overlay-box"]/div[1]/form/div[2]/input')
        await focusInput.type(password)
        focusInput = await self.page.waitForXPath('//*[@id="overlay-box"]/div[1]/form/div[4]/input[1]')
        await focusInput.type(captcha)
        focusInput = await self.page.waitForXPath('//*[@id="login-button"]')
        await focusInput.click()
        await asyncio.sleep(1)
        print('Authentication finished - Thread 1: "AuthWorker()" destroyed.')
        return self.page

    def run(self, username, password, captcha):
        asyncio.get_event_loop().run_until_complete(self.login(username, password, captcha))


class IdScraper:
    def __init__(self, queue, browser, page, user):
        self.queue = queue
        self.browser = browser
        self.page = page
        self.username = user

    def run(self) -> None:
        asyncio.get_event_loop().run_until_complete(self.reqIds())

    async def reqIds(self):
        ua = await self.browser.userAgent()
        cookies = await self.page.cookies()
        if not os.path.isfile("logfile.txt"):
            with open("logfile.txt", "w+") as fout:
                data = requests.get("https://pr0gramm.com/api/items/get",
                                    params={"flags": "9", "likes": self.username, "self": "true"},
                                    headers={"accept": "application/json",
                                             "user-agent": ua, "referer": "https://pr0gramm.com/user/{}/likes".format(self.username)},
                                    cookies={cookies[-1].get("name"): cookies[-1].get("value")})
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
                                               headers={"accept": "application/json", "user-agent": ua,
                                                        "referer": "https://pr0gramm.com/user/{}/likes".format(self.username)},
                                               cookies={cookies[-1].get("name"): cookies[-1].get("value")})
                            data = data.result()
                            ids = ["{}:{}".format(n["id"], n["image"]) for n in data.json()["items"]]
                            for item in ids:
                                fout.write("{}{}".format(item, "\n"))
                                self.queue.put(item.split(":")[1].strip())
                finally:
                    print('Service "IdScraper" finished. Thread destroyed.')
                    return 0
        else:
            with open("logfile.txt", "r+") as fin:
                data = requests.get("https://pr0gramm.com/api/items/get",
                                    params={"flags": "9", "likes": self.username, "self": "true"},
                                    headers={"accept": "application/json",
                                             "user-agent": ua, "referer": "https://pr0gramm.com/user/{}/likes".format(self.username)},
                                    cookies={cookies[-1].get("name"): cookies[-1].get("value")})
                if not data.status_code == requests.codes.ok:
                    raise Exception('Request rejected by server, please restart the program and try again.')
                chk = [str(n["id"]) for n in data.json()["items"]]
                img = [n["image"] for n in data.json()["items"]]
                test = []
                # Stage 1:
                def check(data):
                    for lines in fin:
                        if lines.split(":")[0].strip() == data.strip():
                            return data.strip()
                for data in chk:
                    a = check(data)
                    if a:
                        test.append(check(data))
                # Stage 2:
                #test.sort()
                print(len(test))


class DownloadWorker(Process):
    def __init__(self, queue):
        self.tasks = queue
        super(DownloadWorker, self).__init__()

    def run(self) -> None:
        while True:
            if not self.tasks.empty():
                break
        print('Subprocess: "DownloadWorker()" starting up.')
        while not self.tasks.empty():
            task = self.tasks.get()
            print("{}: {}".format("Downloading file", task))
            img = wget.download(
                "{}/{}".format("https://img.pr0gramm.com", task))
