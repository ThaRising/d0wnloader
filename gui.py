# !python3
# -*- coding: utf-8 -*-

import tkinter as tk
from PIL import ImageTk, Image
import processes


class App(tk.Tk):
    def __init__(self, page, browser, queue):
        tk.Tk.__init__(self)
        self.page = page
        self.browser = browser
        self.queue = queue
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.captcha = tk.StringVar()
        self.configure(bg="#282A2D")
        self.title("d0wnloader")
        self.form = tk.Frame(self, bg="#282A2D")
        self.form.pack(side=tk.TOP, anchor=tk.W, padx=10, pady=10)

        self.formHeading = tk.Label(self.form, text="ANMELDEN", bg="#282A2D", fg="#ffffff", font="Sans 21")
        self.formHeading.pack(side=tk.TOP, anchor=tk.W)

        self.usernameHeading = tk.Label(self.form, text="Benutzername:", bg="#282A2D", fg="#ffffff", font="Sans 14")
        self.usernameHeading.pack(side=tk.TOP, anchor=tk.W)
        self.usernameInput = tk.Entry(self.form, textvariable=self.username, bg="#1B1E1F", fg="#ffffff", bd=0,
                                      relief=tk.FLAT, insertbackground="#ffffff")
        self.usernameInput.pack(side=tk.TOP, anchor=tk.W, fill=tk.X, ipady=4)

        self.passwordHeading = tk.Label(self.form, text="Passwort:", bg="#282A2D", fg="#ffffff", font="Sans 14")
        self.passwordHeading.pack(side=tk.TOP, anchor=tk.W)
        self.passwordInput = tk.Entry(self.form, show="*", textvariable=self.password, bg="#1B1E1F", fg="#ffffff", bd=0,
                                      relief=tk.FLAT, insertbackground="#ffffff")
        self.passwordInput.pack(side=tk.TOP, anchor=tk.W, fill=tk.X, ipady=4)

        self.captchaHeading = tk.Label(self.form, text="Captcha:", bg="#282A2D", fg="#ffffff", font="Sans 14")
        self.captchaHeading.pack(side=tk.TOP, anchor=tk.W)
        self.captchaSc = ImageTk.PhotoImage(image=Image.open("captcha.png"))
        self.captchaL = tk.Label(self.form, image=self.captchaSc, bd=0, highlightthickness=0, bg="#282A2D")
        self.captchaL.pack(side=tk.TOP, anchor=tk.W)
        self.captchaInput = tk.Entry(self.form, textvariable=self.captcha, bg="#1B1E1F", fg="#ffffff", bd=0,
                                      relief=tk.FLAT, insertbackground="#ffffff")
        self.captchaInput.pack(side=tk.TOP, anchor=tk.W, fill=tk.X, pady=7, ipady=4)

        self.login = tk.Label(self.form, text="Anmelden", bg="#ee4d2e", fg="#ffffff", font="Sans 10")
        self.login.bind("<Button-1>", lambda e: self.startAuth())
        self.login.bind("<Enter>", lambda e: e.widget.configure(bg="#ffffff", fg="#000000"))
        self.login.bind("<Leave>", lambda e: e.widget.configure(bg="#ee4d2e", fg="#ffffff"))
        self.login.pack(side=tk.TOP, anchor=tk.W, ipady=3, ipadx=2)

    def startAuth(self):
        processes.AuthWorker(self.page, self.username.get(), self.password.get(), self.captcha.get())
        processes.IdScraper(self.queue, self.browser, self.page, self.username.get())
