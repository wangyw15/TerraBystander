from pathlib import Path
from xml.etree import ElementTree as ET

from ..gamedata import (
    Activity,
    AvgStory,
    GameDataForBook,
    GameDataMetadata,
    Operator,
)
from .model import ACTIVITY_TYPE_LABEL


class EpubGenerator:
    def __init__(self, data: GameDataForBook, target_path: str | Path) -> None:
        self.data = data
        if isinstance(target_path, str):
            self.path = Path(target_path)
        else:
            self.path = target_path

        self._working_path = Path("__EPUB_TEMP__")
        self._working_path.mkdir()

        self._content_path = self._working_path / "content"
        self._content_path.mkdir()

    # helpers
    def _tostring(self, element: ET.Element) -> str:
        return ET.tostring(element, encoding="unicode")  # type: ignore

    def _get_head(self, html: ET.Element) -> ET.Element:
        head = html.find("head")
        if head is None:
            head = ET.SubElement(html, "head")
        return head

    def _get_body(self, html: ET.Element) -> ET.Element:
        body = html.find("body")
        if body is None:
            body = ET.SubElement(html, "body")
        return body

    def _set_title(self, html: ET.Element, title: str) -> None:
        head = self._get_head(html)

        title_element = head.find("title")
        if title_element is None:
            title_element = ET.SubElement(head, "title")
        title_element.text = title

    def _basic_page(self) -> ET.Element:
        html = ET.Element("html")

        head = ET.SubElement(html, "head")
        link = ET.SubElement(head, "link")
        link.attrib["rel"] = "stylesheet"
        link.attrib["href"] = "../../style.css"
        link.attrib["type"] = "text/css"

        body = ET.SubElement(html, "body")
        return html

    def _story_page(self, story: AvgStory) -> ET.Element:
        html = self._basic_page()
        self._set_title(html, story.name)

        body = self._get_body(html)

        # title
        title_container = ET.SubElement(body, "h1")
        title_container.attrib["class"] = "avg title"
        code = ET.SubElement(title_container, "span")
        code.attrib["class"] = "code"
        code.text = story.code
        story_name = ET.SubElement(title_container, "span")
        story_name.attrib["class"] = "name"
        story_name.text = story.name

        # avg tag
        avg_tag = ET.SubElement(body, "h2")
        avg_tag.attrib["class"] = "avg avg-tag"
        avg_tag.text = story.avg_tag

        # description
        description = ET.SubElement(body, "p")
        description.attrib["class"] = "avg description"
        description.text = story.description

        # story content
        container = ET.SubElement(body, "section")
        container.attrib["class"] = "avg container"
        # line
        for line in story.texts:
            story_line = ET.SubElement(container, "p")
            story_line.attrib["class"] = "avg line"
            if line.name == "":
                story_line.attrib["class"] += " narrator"

            # speaker
            speaker = ET.SubElement(story_line, "span")
            speaker.attrib["class"] = "speaker"
            strong = ET.SubElement(speaker, "strong")
            strong.text = line.name

            # name spacing
            name_spacing = ET.SubElement(story_line, "span")
            name_spacing.attrib["class"] = "spacing"
            name_spacing.text = " "

            # text
            text = ET.SubElement(story_line, "span")
            text.attrib["class"] = "text"
            text.text = line.text

        return html

    def _activity_outline_page(self, activity: Activity) -> ET.Element:
        html = self._basic_page()
        self._set_title(html, activity.name)

        body = self._get_body(html)

        # activity type
        activity_type = ET.SubElement(body, "h2")
        activity_type.attrib["class"] = "activity type"
        activity_type.text = ACTIVITY_TYPE_LABEL[activity.activity_type.value]

        # title
        title = ET.SubElement(body, "h1")
        title.attrib["class"] = "activity title"
        title.text = activity.name

        # secondary title
        secondary_title = ET.SubElement(body, "h2")
        secondary_title.attrib["class"] = "activity secondary title"
        secondary_title.text = activity.name

        # outline
        outline_ul = ET.SubElement(body, "ul")
        outline_ul.attrib["class"] = "activity outline"
        for story in activity.stories:
            story_li = ET.SubElement(outline_ul, "li")
            story_li.attrib["class"] = "activity outline line"

            story_a = ET.SubElement(story_li, "a")
            story_a.attrib["href"] = f"{story.id}.html"
            story_a.text = story.name + " " + story.avg_tag

        return html

    def _activity(self, activity: Activity, working_path: Path | None = None) -> None:
        if working_path is None:
            working_path = (
                self._content_path / activity.activity_type.value / activity.id
            )
        working_path.mkdir(exist_ok=True, parents=True)

        # outline page
        with (working_path / self.OUTLINE_PAGE_NAME).open("w", encoding="utf-8") as f:
            f.write(self._tostring(self._activity_outline_page(activity)))

        # story pages
        for story in activity.stories:
            with (working_path / (story.id + ".html")).open("w", encoding="utf-8") as f:
                f.write(self._tostring(self._story_page(story)))

    def _outline_page(
        self,
        chapters: list[Activity] | list[Operator],
        title: str,
        href_target: str = "",
    ) -> ET.Element:
        html = self._basic_page()
        self._set_title(html, title)

        body = self._get_body(html)

        # title
        title_h1 = ET.SubElement(body, "h1")
        title_h1.attrib["class"] = "outline title"
        title_h1.text = title

        # outline
        outline_ul = ET.SubElement(body, "ul")
        outline_ul.attrib["class"] = "outline container"
        for chapter in chapters:
            story_li = ET.SubElement(outline_ul, "li")
            story_li.attrib["class"] = "line"

            story_a = ET.SubElement(story_li, "a")
            story_a.attrib["href"] = (
                chapter.id + "/" + (href_target or self.OUTLINE_PAGE_NAME)
            )
            story_a.text = chapter.name

        return html

    def _operator_info_page(self, operator: Operator) -> ET.Element:
        html = self._basic_page()
        self._set_title(html, operator.name)

        body = self._get_body(html)

        # name
        name = ET.SubElement(body, "h1")
        name.attrib["class"] = "operator title"
        name.text = operator.name

        # appellation
        secondary_name = ET.SubElement(body, "h2")
        secondary_name.attrib["class"] = "operator secondary title"
        secondary_name.text = operator.appellation

        # usage
        secondary_name = ET.SubElement(body, "p")
        secondary_name.attrib["class"] = "operator usage"
        secondary_name.text = operator.usage

        # description
        secondary_name = ET.SubElement(body, "p")
        secondary_name.attrib["class"] = "operator description"
        secondary_name.text = operator.description

        # profession
        profession_container = ET.SubElement(body, "p")
        profession_container.attrib["class"] = "operator profession"
        profession = ET.SubElement(profession_container, "span")
        profession.attrib["class"] = "profession"
        profession.text = operator.profession.value
        profession_spacing = ET.SubElement(profession_container, "span")
        profession_spacing.attrib["class"] = "spacing"
        profession_spacing.text = " "
        profession_spacing = ET.SubElement(profession_container, "span")
        profession_spacing.attrib["class"] = "secondary profession"
        profession_spacing.text = operator.sub_profession

        return html

    def _operator_stories_page(self, operator: Operator) -> ET.Element:
        html = self._basic_page()
        self._set_title(html, operator.name)

        body = self._get_body(html)

        # title
        title = ET.SubElement(html, "h1")
        title.attrib["class"] = "operator story title"
        title.text = "干员档案"

        container = ET.SubElement(body, "section")
        container.attrib["class"] = "operator story container"
        for story in operator.operator_stories:
            title = ET.SubElement(container, "h2")
            title.attrib["class"] = "title"
            title.text = story.title
            text = ET.SubElement(container, "p")
            text.attrib["class"] = "text"
            text.text = story.text.replace("\n", "<br/>")

        return html

    def _operator(self, operator: Operator) -> None:
        working_path = self._content_path / self.OPERATOR_VOLUME_NAME / operator.id
        working_path.mkdir(exist_ok=True, parents=True)

        with (working_path / self.OPERATOR_INFO_PAGE_NAME).open(
            "w", encoding="utf-8"
        ) as f:
            f.write(self._tostring(self._operator_info_page(operator)))

        with (working_path / self.OPERATOR_STORIES_PAGE_NAME).open(
            "w", encoding="utf-8"
        ) as f:
            f.write(self._tostring(self._operator_stories_page(operator)))

        avg_path = working_path / self.OPERATOR_AVG_NAME
        avg_path.mkdir(exist_ok=True, parents=True)
        with (avg_path / self.OUTLINE_PAGE_NAME).open("w", encoding="utf-8") as f:
            f.write(self._tostring(self._outline_page(operator.avgs, "干员密录")))
        for activity in operator.avgs:
            self._activity(activity, avg_path / activity.id)

    def metadata_page(self, metadata: GameDataMetadata) -> ET.Element:
        html = self._basic_page()

        head = html.find("/html/head")
        if head is None:
            raise ValueError("Unable to find head element")

        body = ET.SubElement(html, "body")
        container = ET.SubElement(body, "div")
        container.attrib["class"] = "script-container"

        return html

    def _ncx_file(self) -> None:
        toc_root = ET.Element("ncx")
        ET.SubElement(ET.SubElement(toc_root, "docTitle"), "text").text = "泰拉观者"
        ET.SubElement(ET.SubElement(toc_root, "docAuthor"), "text").text = "鹰角网络"

        toc_map = ET.SubElement(toc_root, "navMap")

        raise NotImplementedError("ncx file not implemented")

    def generate(self) -> None:
        volumes: dict[str, list[Activity]] = {}

        # activities data
        for activity in self.data.activities:
            if activity.activity_type.value not in volumes:
                volumes[activity.activity_type.value] = []
            volumes[activity.activity_type.value].append(activity)

            self._activity(activity)

        # activities outline
        for volume_type, chapters in volumes.items():
            with (self._content_path / volume_type / self.OUTLINE_PAGE_NAME).open(
                "w", encoding="utf-8"
            ) as f:
                f.write(
                    self._tostring(
                        self._outline_page(chapters, ACTIVITY_TYPE_LABEL[volume_type])
                    )
                )

        # operators data
        for operator in self.data.operators:
            self._operator(operator)

        # operators outline
        with (
            self._content_path / self.OPERATOR_VOLUME_NAME / self.OUTLINE_PAGE_NAME
        ).open("w", encoding="utf-8") as f:
            f.write(
                self._tostring(
                    self._outline_page(
                        self.data.operators, "Operator", self.OPERATOR_INFO_PAGE_NAME
                    )
                )
            )

    OUTLINE_PAGE_NAME = "_outline.html"
    OPERATOR_VOLUME_NAME = "OPERATOR"
    OPERATOR_INFO_PAGE_NAME = "_info.html"
    OPERATOR_STORIES_PAGE_NAME = "_story.html"
    OPERATOR_AVG_NAME = "avg"
    CSS = r"""
html {
    font-size: 16px;
    --name-spacing: 1rem;
    --speaker-width: 8rem;
}

p.story text {
    min-height: 1rem;
    /* text-indent: -9rem;
    text-indent: calc(0rem - var(--name-spacing) - var(--speaker-width));
    padding-left: calc(var(--name-spacing) + var(--speaker-width)); */
}

.name-spacing {
    /* display: inline-block; */
    width: var(--name-spacing);
}

.speaker {
    /* display: inline-block;
    width: var(--speaker-width);
    text-align: right; */
    /* font-weight: bolder; */
}

.text {}

.narrator {
    color: gray;
    font-style: italic;
}

div.title.activity {
    font-weight: bold;
}
""".strip()
