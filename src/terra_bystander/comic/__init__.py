from typing import Any

import httpx

from .model import (
    BaseResponse,
    ComicData,
    ComicItem,
    Episode,
    Page,
)


class Comic:
    COMIC_LIST_URL = "https://terra-historicus.hypergryph.com/api/comic"
    COMIC_DATA_URL = "https://terra-historicus.hypergryph.com/api/comic/{comic_id}"
    EPISODE_DATA = "https://terra-historicus.hypergryph.com/api/comic/{comic_id}/episode/{episode_id}"
    PAGE_DATA = "https://terra-historicus.hypergryph.com/api/comic/{comic_id}/episode/{episode_id}/page?pageNum={page_num}"
    OOC_PAGE = "https://res01.hycdn.cn/d4d4b64dea47e772826532d71127b2f1/68382A9A/comic/pic/20211231/854a427c66545b47772388b42631d666.jpg"

    def __init__(self) -> None:
        self.client = httpx.Client()

    def _fetch(self, url: str) -> Any | None:
        resp = self.client.get(url)
        if not resp.is_success:
            return None

        data: BaseResponse = resp.json()
        if data["code"] != 0:
            return None

        return data["data"]

    def list_comics(self) -> list[ComicItem] | None:
        """
        Get comic list

        :return: comic items, None if failed
        """
        return self._fetch(self.COMIC_LIST_URL)

    def comic_data(self, comic_id: str) -> ComicData | None:
        """
        Get comic data

        :params comic_id: comic id

        :return: data, None if failed
        """
        return self._fetch(self.COMIC_DATA_URL.format(comic_id=comic_id))

    def episode_data(self, comic_id: str, episode_id: str) -> Episode | None:
        """
        Get episode data

        :params comic_id: comic id
        :params episode_id: episode id

        :return: episode items, None if failed
        """
        return self._fetch(
            self.EPISODE_DATA.format(comic_id=comic_id, episode_id=episode_id)
        )

    def page_data(self, comic_id: str, episode_id: str, page_num: int) -> Page | None:
        """
        Get page data

        :params comic_id: comic id
        :params episode_id: episode id
        :params page_num: page number, start from 1

        :return: page data, None if failed
        """
        return self._fetch(
            self.PAGE_DATA.format(
                comic_id=comic_id, episode_id=episode_id, page_num=page_num
            )
        )

    def download(self, url: str) -> bytes | None:
        """
        Download file

        :params url: url

        :return: data, None if failed
        """
        resp = self.client.get(url)
        if not resp.is_success:
            return None
        return resp.read()


__all__ = [
    "Comic",
]
