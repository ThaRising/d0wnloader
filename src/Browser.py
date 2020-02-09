# !python3
# -*- coding: utf-8 -*-

from pyppeteer import launch, browser, page
from asyncio import get_event_loop


class Browser:
    """
    Contains easily accessible attributes of the browser object.
    self.browser: the headless Browser running in the Background
    self.page: the main page of the browser
    self.ua: the user agent of the browser
    self.cookies: the page cookies after login, contain the personal identification token of the user
    self.user: contain the username of the logged in user, used by services
    """
    def __init__(self) -> None:
        self.cookies: dict = {}
        self.user: str = ""
        get_event_loop().run_until_complete(self._init())

    async def _init(self) -> None:
        self.browser: browser = await launch({"headless": True})
        self.page: page = await self.browser.newPage()
        self.ua: str = await self.browser.userAgent()
        await self.page.goto("https://pr0gramm.com/user", {"waitUntil": "networkidle2"})
        loginButton = await self.page.J(".head-link")
        await loginButton.click()
        captcha = await self.page.waitForXPath('//*[@id="overlay-box"]/div[1]/form/div[4]/div[1]/img')
        await captcha.screenshot({'path': 'captcha.png'})

    async def login(self, username: str, password: str, captcha: str) -> dict:
        """Puts in authentication information into the login-form fields and returns cookies once login is completed"""
        usernameField = await self.page.waitForXPath('//*[@id="overlay-box"]/div[1]/form/div[1]/input')
        await usernameField.type(username)
        passwordField = await self.page.waitForXPath('//*[@id="overlay-box"]/div[1]/form/div[2]/input')
        await passwordField.type(password)
        captchaField = await self.page.waitForXPath('//*[@id="overlay-box"]/div[1]/form/div[4]/input[1]')
        await captchaField.type(captcha)
        loginButton = await self.page.waitForXPath('//*[@id="login-button"]')
        await loginButton.click()
        self.cookies = await self.page.cookies()
