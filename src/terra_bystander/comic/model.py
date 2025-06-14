from enum import Enum
from typing import Any, TypedDict


class BaseResponse(TypedDict):
    code: int
    msg: str
    data: Any


class ComicType(Enum):
    COMIC = 1
    ALBUM = 2
    COMIC2 = 3


class ComicItem(TypedDict):
    cid: str
    type: ComicType
    cover: str
    title: str
    subtitle: str
    authors: list[str]


class ComicListResponse(BaseResponse):
    data: list[ComicItem]


class Direction(Enum):
    LEFT = "left"
    RIGHT = "right"


class EpisodeType(Enum):
    NORMAL = 1


class EpisodeItem(TypedDict):
    cid: str
    type: EpisodeType
    shortTitle: str
    title: str
    displayTime: int


class ComicData(TypedDict):
    cid: str
    type: ComicType
    cover: str
    title: str
    subtitle: str
    authors: list[str]
    keywords: list[str]
    introduction: str
    direction: Direction
    readConfig: Any  # unknown
    episodes: list[EpisodeItem]


class ComicResponse(BaseResponse):
    data: ComicData


class PageInfo(TypedDict):
    width: int
    height: int
    doublePage: bool


class Episode(TypedDict):
    title: str
    shortTitle: str
    type: EpisodeType
    likes: int
    pageInfos: list[PageInfo]


class EpisodeResponse(BaseResponse):
    data: Episode


class Page(TypedDict):
    pageNum: int
    url: str


class PageResponse(BaseResponse):
    data: Page
