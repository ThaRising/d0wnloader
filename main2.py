# !python3
# -*- coding: utf-8 -*-

import asyncio
import os
from pyppeteer import launch
from threading import Thread
from queue import Queue
from dotenv import load_dotenv

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
        browser = await launch()
        page = await PrepWorker.__prep(browser)
        return browser, page


class authWorker(Thread):
    def __init__(self, queue, page):
        Thread.__init__(self)

    async def login(self):
        pass

    def run(self):
        asyncio.get_event_loop().run_until_complete(self.login())


class Gui():
    def __init__(self):
        print("Dispatching PrepWorker() - Thread: NULL")
        self.browser, self.page = asyncio.get_event_loop().run_until_complete(PrepWorker().dispatcher())
        self.username = os.getenv("USR")
        self.password = os.getenv("PWD")
        self.captcha = input("Enter the Captcha here: ")
        asyncio.get_event_loop().run_until_complete(self.onLogin())
        self.queue = Queue()

    async def onLogin(self):
        focusInput = await self.page.waitForXPath('//*[@id="overlay-box"]/div[1]/form/div[1]/input')
        await focusInput.type(self.username)
        focusInput = await self.page.waitForXPath('//*[@id="overlay-box"]/div[1]/form/div[2]/input')
        await focusInput.type(self.password)
        focusInput = await self.page.waitForXPath('//*[@id="overlay-box"]/div[1]/form/div[4]/input[1]')
        await focusInput.type(self.captcha)
        focusInput = await self.page.waitForXPath('//*[@id="login-button"]')
        await focusInput.click()
        await asyncio.sleep(1)
        imgStream = await self.page.waitForXPath('//*[@id="stream"]')
        await imgStream.screenshot({'path': 'page.png'})


if __name__=="__main__":
    Gui()