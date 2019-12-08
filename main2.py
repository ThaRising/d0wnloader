# !python3
# -*- coding: utf-8 -*-

import asyncio
import os
from pyppeteer import launch
from threading import Thread
from queue import Queue
from dotenv import load_dotenv
import requests

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

    async def dispatcher(self):
        browser = await launch({"headless": False})
        page = await PrepWorker.__prep(browser)
        return browser, page


class AuthWorker(Thread):
    def __init__(self, queue, page):
        Thread.__init__(self)
        self.queue = queue
        self.page = page
        self.username = os.getenv("USR")
        self.password = os.getenv("PWD")
        self.captcha = None

    async def login(self):
        self.captcha = input("Enter the Captcha here: ")
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
        nPage = asyncio.get_event_loop().run_until_complete(self.login())
        self.queue.put(nPage)


class QueueCrawler(Thread):
    def __init__(self, queue, page):
        Thread.__init__(self)

    def run(self):
        pass

    async def log(self):
        async with open ("logfile.txt", "w+") as fin:
            async for lines in fin:
                pass


class DonwloadWorker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)

    def run(self):
        pass

    def download(self):
        pass


class Gui():
    def __init__(self):
        self.authQueue = Queue()
        print("Dispatching PrepWorker() - Thread: NULL")
        self.browser, self.page = asyncio.get_event_loop().run_until_complete(PrepWorker().dispatcher())
        print("Dispatching AuthWorker() - Thread: 1")
        AuthWorker(self.authQueue, self.page).run()
        while True:
            try:
                self.page = self.authQueue.get(0)
                print('Authentication finished - Thread 1: "AuthWorker()" destroyed.')
                break
            except Queue.Empty:
                continue
        asyncio.get_event_loop().run_until_complete(self.sc())

    async def sc(self):
        ua = await self.browser.userAgent()
        cookies = await self.page.cookies()
        cookies = cookies[-1]
        stream = requests.get("https://pr0gramm.com/api/items/get",
                              params={"older": "3525673", "flags": "9", "likes": os.getenv("USR"), "self": "true"},
                              headers={"accept": "application/json",
                                       "user-agent": ua, "referer": os.getenv("MAIN_PAGE")},
                              cookies={cookies.get("name"): cookies.get("value")})
        if not stream.status_code == requests.codes.ok:
            raise Exception('Request rejected by server, please restart the program and try again.')
        ids = [n["id"] for n in stream.json()["items"]]
        with open("logfile.txt","w+") as fout:
            for items in ids:
                fout.write("{}{}".format(items, "\n"))
        await self.page.evaluate("""{window.scrollBy(0, document.body.scrollHeight);}""")
        await asyncio.sleep(10)
        imgStream = await self.page.waitForXPath('//*[@id="stream"]')
        await imgStream.screenshot({'path': 'page.png'})


if __name__=="__main__":
    Gui()