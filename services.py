# !python3
# -*- coding: utf-8 -*-

from requests import get
from requests_futures.sessions import FuturesSession

API_BASE_URL: str = "https://pr0gramm.com/api/items/get"
API_USER_URL: str = "https://pr0gramm.com/user/{}/likes"


def getFirstItems(session: FuturesSession, username: str, ua: str, cookies: dict) -> get:
    """Returns the first 120 posts in a users favorite list"""
    return session.get(API_BASE_URL,
                       params={"flags": "9", "likes": username, "self": "true"},
                       headers={"accept": "application/json", "user-agent": ua,
                                "referer": API_USER_URL.format(username)},
                       cookies={cookies[-1].get("name"): cookies[-1].get("value")}).result()


def getItemsOlderThanX(session: FuturesSession, lastChecked: int, username: str, ua: str, cookies: dict) -> get:
    """Returns next 120 posts older than lastChecked"""
    return session.get(API_BASE_URL,
                       params={"older": lastChecked - 120, "flags": "9", "likes": username, "self": "true"},
                       headers={"accept": "application/json", "user-agent": ua,
                                "referer": API_USER_URL.format(username)},
                       cookies={cookies[-1].get("name"): cookies[-1].get("value")}).result()
