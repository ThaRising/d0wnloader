# !python3
# -*- coding: utf-8 -*-

import asyncio
import os
from pyppeteer import launch
from dotenv import load_dotenv
from multiprocessing import Process, Queue
import processes
import gui

load_dotenv()


class Gui(gui.App):
    def __init__(self):
        global page, browser, tasks
        gui.App.__init__(self, page, browser, tasks)
        self.mainloop()


async def prep():
    browser = await launch({"headless": False})
    page = await browser.newPage()
    await page.goto(os.getenv("MAIN_PAGE"), {"waitUntil": "networkidle2"})
    loginHandle = await page.J(".head-link")
    await loginHandle.click()
    captcha = await page.waitForXPath('//*[@id="overlay-box"]/div[1]/form/div[4]/div[1]/img')
    await captcha.screenshot({'path': 'captcha.png'})
    return browser, page

if __name__ == "__main__":
    browser, page = asyncio.get_event_loop().run_until_complete(prep())
    tasks = Queue()
    threads = [processes.DownloadWorker(tasks), processes.DownloadWorker(tasks)]
    for thread in threads:
        thread.daemon = True
        thread.start()
        #thread.join()
    Gui()
