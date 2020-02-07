# !python3
# -*- coding: utf-8 -*-

from multiprocessing.queues import Queue
from multiprocessing.spawn import freeze_support
import services
import processes
import Gui

if __name__ == "__main__":
    freeze_support()
    tasks = Queue()
    threads = [processes.DownloadWorker(tasks), processes.DownloadWorker(tasks)]
    for thread in threads:
        thread.daemon = True
        thread.start()
    Gui.App(tasks).mainloop()
