# !python3
# -*- coding: utf-8 -*-

import multiprocessing
import processes
from Browser import Browser
import Gui

if __name__ == "__main__":
    multiprocessing.freeze_support()
    tasks = multiprocessing.Queue()
    threads = [processes.DownloadWorker(tasks), processes.DownloadWorker(tasks)]
    for thread in threads:
        thread.daemon = True
        thread.start()
    browser = Browser()
    Gui.Gui(browser, tasks).mainloop()
