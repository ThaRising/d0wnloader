# !python3
# -*- coding: utf-8 -*-

import asyncio
import os
from pyppeteer import launch
from threading import Thread
from dotenv import load_dotenv
import requests
from requests_futures.sessions import FuturesSession
import wget
from queue import Empty
from multiprocessing import Process, Queue

load_dotenv()


class PrepWorker():
    def __init__(self):
        pass

    @staticmethod
    async def __prep(sessMgr):
        page = await sessMgr.newPage()
        await page.goto(os.getenv("MAIN_PAGE"), {"waitUntil": "networkidle2"})
        loginHandle = await page.J(".head-link")
        await loginHandle.click()
        captcha = await page.waitForXPath('//*[@id="overlay-box"]/div[1]/form/div[4]/div[1]/img')
        await captcha.screenshot({'path': 'captcha.png'})
        return page

    @staticmethod
    async def dispatcher():
        browser = await launch({"headless": False})
        page = await PrepWorker.__prep(browser)
        return browser, page


class AuthWorker(Thread):
    def __init__(self, page):
        Thread.__init__(self)
        self.page = page
        self.username = os.getenv("USR")
        self.password = os.getenv("PWD")
        self.captcha = None

    async def login(self):
        while True:
            try:
                self.captcha = input("Enter the Captcha here: ")
                assert len(self.captcha) >= 5
                break
            except AssertionError:
                continue
        focusInput = await self.page.waitForXPath('//*[@id="overlay-box"]/div[1]/form/div[1]/input')
        await focusInput.type(self.username)
        focusInput = await self.page.waitForXPath('//*[@id="overlay-box"]/div[1]/form/div[2]/input')
        await focusInput.type(self.password)
        focusInput = await self.page.waitForXPath('//*[@id="overlay-box"]/div[1]/form/div[4]/input[1]')
        await focusInput.type(self.captcha)
        focusInput = await self.page.waitForXPath('//*[@id="login-button"]')
        await focusInput.click()
        await asyncio.sleep(1)
        return self.page

    def run(self):
        return asyncio.get_event_loop().run_until_complete(self.login())


class IdScraper(Thread):
    def __init__(self, browser, page, queue):
        Thread.__init__(self)
        self.browser = browser
        self.page = page
        self.queue = queue

    def run(self):
        asyncio.get_event_loop().run_until_complete(self.log())
        return 0

    async def log(self):
        ua = await self.browser.userAgent()
        cookies = await self.page.cookies()
        if not os.path.isfile("logfile.txt"):
            with open("logfile.txt", "w+") as fout:
                data = requests.get("https://pr0gramm.com/api/items/get",
                                    params={"flags": "9", "likes": os.getenv("USR"), "self": "true"},
                                    headers={"accept": "application/json",
                                             "user-agent": ua, "referer": os.getenv("MAIN_PAGE")},
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
                                                       "likes": os.getenv("USR"), "self": "true"},
                                               headers={"accept": "application/json", "user-agent": ua,
                                                        "referer": os.getenv("MAIN_PAGE")},
                                               cookies={cookies[-1].get("name"): cookies[-1].get("value")})
                            data = data.result()
                            ids = ["{}:{}".format(n["id"], n["image"]) for n in data.json()["items"]]
                            for item in ids:
                                fout.write("{}{}".format(item, "\n"))
                                self.queue.put(item.split(":")[1].strip())
                finally:
                    print('Service "IdScraper" finished. Thread destroyed.')
                    return 0


class DownloadWorker():
    def __init__(self):
        pass

    @staticmethod
    def run(tasks) -> None:
        while not tasks.empty():
            task = tasks.get()
            print("{}: {}".format("Downloading file", task))
            img = wget.download(
                "{}/{}".format("https://img.pr0gramm.com", task))


class Gui():
    def __init__(self, queue):
        global thread1, thread2, thread3, thread4
        self.queue = queue
        print("Dispatching PrepWorker() - Thread: NULL")
        self.browser, self.page = asyncio.get_event_loop().run_until_complete(PrepWorker.dispatcher())
        print("Dispatching AuthWorker() - Thread: 1")
        self.page = AuthWorker(self.page).run()
        print('Authentication finished - Thread 1: "AuthWorker()" destroyed.')
        print('Dispatching IdScraper() - Thread: 1')
        IdScraper(self.browser, self.page, self.queue).run()
        print("Dispatching DownloadWorker() Threads 1 - 4")
        thread1.start()
        thread2.start()
        thread3.start()
        thread4.start()


if __name__ == "__main__":
    tasks = Queue()
    thread1 = Process(target=DownloadWorker.run, args=((tasks),))
    thread1.daemon = True
    thread2 = Process(target=DownloadWorker.run, args=((tasks),))
    thread2.daemon = True
    thread3 = Process(target=DownloadWorker.run, args=((tasks),))
    thread3.daemon = True
    thread4 = Process(target=DownloadWorker.run, args=((tasks),))
    thread4.daemon = True
    Gui(tasks)