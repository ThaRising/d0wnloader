# !python3
# -*- coding: utf-8 -*-

import asyncio
from pyppeteer import launch
from multiprocessing.queues import Queue
from multiprocessing.spawn import freeze_support
import processes
import gui


async def prep():
    browser = await launch({"headless": True})
    page = await browser.newPage()
    await page.goto("https://pr0gramm.com/user/x/likes", {"waitUntil": "networkidle2"})
    loginHandle = await page.J(".head-link")
    await loginHandle.click()
    captcha = await page.waitForXPath('//*[@id="overlay-box"]/div[1]/form/div[4]/div[1]/img')
    await captcha.screenshot({'path': 'captcha.png'})
    return browser, page

if __name__ == "__main__":
    freeze_support()
    browser, page = asyncio.get_event_loop().run_until_complete(prep())
    tasks = Queue()
    threads = [processes.DownloadWorker(tasks), processes.DownloadWorker(tasks)]
    for thread in threads:
        thread.daemon = True
        thread.start()
    gui.App(page, browser, tasks).mainloop()
