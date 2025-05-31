from pathlib import Path

from ebooklib import epub
from jinja2 import Environment, PackageLoader, select_autoescape

from ..gamedata import (
    Activity,
    AvgStory,
    GameDataForBook,
    GameDataMetadata,
    Operator,
)
from .model import ACTIVITY_TYPE_LABEL


class EpubGenerator:
    def __init__(self, data: GameDataForBook, save_path: str | Path) -> None:
        self.data = data
        if isinstance(save_path, str):
            self.save_path = Path(save_path)
        else:
            self.save_path = save_path

        self._volumes: dict[str, list[Activity]] = {}

        package_name = __package__ or "terra_bystander.epub"
        self.jinja_env = Environment(
            loader=PackageLoader(package_name),
            autoescape=select_autoescape(
                enabled_extensions=("html", "css", "jinja", "jinja2")
            ),
        )

    def _story_page(self, story: AvgStory) -> str:
        """
        Generate page from story

        :params story: story data

        :return: html content
        """
        template = self.jinja_env.get_template("avg.jinja")
        return template.render(avg=story)

    def _activity_page(self, activity: Activity) -> str:
        """
        Generate cover page from activity

        :params story: story data

        :return: html content
        """
        template = self.jinja_env.get_template("activity.jinja")
        return template.render(activity=activity)

    def _outline_page(
        self,
        entries: list[Activity] | list[Operator],
        title: str,
        index_file: str = "",
    ) -> str:
        """
        Generate outline page for entries

        :params entries: entries
        :params title: page title
        :params index_file: href target

        :return: html content
        """
        template = self.jinja_env.get_template("outline.jinja")
        return template.render(
            entries=entries,
            title=title,
            index_file=(index_file or self.INDEX_PAGE_NAME),
        )

    def _operator_info_page(self, operator: Operator) -> str:
        """
        Generate info page for operator

        :params operator: operator data

        :return: html content
        """
        template = self.jinja_env.get_template("operator_info.jinja")
        return template.render(operator=operator)

    def _operator_stories_page(self, operator: Operator) -> str:
        """
        Generate story page for operator

        :params operator: operator data

        :return: html content
        """
        template = self.jinja_env.get_template("operator_story.jinja")
        return template.render(operator=operator)

    def _metadata_page(self, metadata: GameDataMetadata) -> str:
        """
        Generate metadata page

        :params operator: metadata

        :return: html content
        """
        template = self.jinja_env.get_template("metadata.jinja")
        return template.render(metadata=metadata)

    def _read_volumes(self) -> None:
        """
        Separate activities by type
        """
        if self._volumes:
            return

        for activity in self.data.activities:
            if activity.activity_type.value not in self._volumes:
                self._volumes[activity.activity_type.value] = []
            self._volumes[activity.activity_type.value].append(activity)

    def generate(self) -> None:
        """
        Generate epub from game data
        """
        self._read_volumes()
        book = epub.EpubBook()

        # style
        # style_css = epub.EpubItem(
        #     uid="style",
        #     file_name="style.css",
        #     media_type="text/css",
        #     content=self.jinja_env.get_template("style.css").render().encode("utf-8"),
        # )
        # book.add_item(style_css)

        # metadata page
        metadata_item = epub.EpubHtml(
            uid="metadata",
            title="版本信息",
            file_name=f"content/{self.METADATA_PAGE_NAME}",
        )
        metadata_item.set_content(self._metadata_page(self.data.metadata))
        # metadata_item.add_item(style_css)
        book.add_item(metadata_item)
        book.spine.append(metadata_item)
        book.toc.append(metadata_item)

        # volumes
        for volume_type, volume_entries in self._volumes.items():
            volume_outline_item = epub.EpubHtml(
                uid=volume_type,
                title=ACTIVITY_TYPE_LABEL[volume_type],
                file_name=f"content/{volume_type}/{self.INDEX_PAGE_NAME}",
            )
            volume_outline_item.set_content(
                self._outline_page(volume_entries, ACTIVITY_TYPE_LABEL[volume_type])
            )
            # volume_outline_item.add_item(style_css)
            book.add_item(volume_outline_item)
            book.spine.append(volume_outline_item)

            activity_items = []
            for activity in volume_entries:
                activity_outline_item = epub.EpubHtml(
                    uid=activity.id,
                    title=activity.name,
                    file_name=f"content/{volume_type}/{activity.id}/{self.INDEX_PAGE_NAME}",
                )
                activity_outline_item.set_content(self._activity_page(activity))
                # activity_outline_item.add_item(style_css)
                book.add_item(activity_outline_item)
                book.spine.append(activity_outline_item)

                # toc
                story_items = []
                leading_story_item: epub.EpubHtml | None = None
                last_story_name: str = ""
                story_stages: list[epub.EpubHtml] = []

                for story in activity.stories:
                    story_item = epub.EpubHtml(
                        uid=story.id,
                        title=story.avg_tag,
                        file_name=f"content/{volume_type}/{activity.id}/{story.id}.xhtml",
                    )
                    story_item.set_content(self._story_page(story))
                    # story_item.add_item(style_css)
                    book.add_item(story_item)
                    book.spine.append(story_item)

                    # toc
                    if last_story_name != story.name:
                        if leading_story_item is not None and len(story_stages) > 0:
                            story_items.append((epub.Link(href=leading_story_item.file_name, title=last_story_name), story_stages))
                            story_stages = []
                        leading_story_item = story_item
                    
                    story_stages.append(story_item)
                    last_story_name = story.name

                # last toc item
                if leading_story_item is not None and len(story_stages) > 0:
                    story_items.append((epub.Link(href=leading_story_item.file_name, title=last_story_name), story_stages))

                activity_items.append((activity_outline_item, story_items))
            book.toc.append((volume_outline_item, activity_items))

        # operators
        operators_outline_item = epub.EpubHtml(
            uid="OPERATORS",
            title="Operators",
            file_name=f"content/{self.OPERATOR_VOLUME_NAME}/{self.INDEX_PAGE_NAME}",
        )
        operators_outline_item.set_content(
            self._outline_page(entries=self.data.operators, title="Operators")
        )
        # operators_outline_item.add_item(style_css)
        book.add_item(operators_outline_item)
        book.spine.append(operators_outline_item)

        for operator in self.data.operators:
            operator_info_item = epub.EpubHtml(
                uid=operator.id + "_info",
                title=operator.name,
                file_name=f"content/{self.OPERATOR_VOLUME_NAME}/{operator.id}/{self.INDEX_PAGE_NAME}",
            )
            operator_info_item.set_content(self._operator_info_page(operator))
            # operator_info_item.add_item(style_css)
            book.add_item(operator_info_item)
            book.spine.append(operator_info_item)

            operator_stories_item = epub.EpubHtml(
                uid=operator.id + "_story",
                title=operator.name,
                file_name=f"content/{self.OPERATOR_VOLUME_NAME}/{operator.id}/{self.OPERATOR_STORIES_PAGE_NAME}",
            )
            operator_stories_item.set_content(self._operator_stories_page(operator))
            # operator_stories_item.add_item(style_css)
            book.add_item(operator_stories_item)
            book.spine.append(operator_stories_item)

            operator_avgs_outline_item = epub.EpubHtml(
                uid=operator.id + "_avgs",
                title="干员密录",
                file_name=f"content/{self.OPERATOR_VOLUME_NAME}/{operator.id}/{self.OPERATOR_AVG_NAME}/{self.INDEX_PAGE_NAME}",
            )
            operator_avgs_outline_item.set_content(
                self._outline_page(operator.avgs, "干员密录")
            )
            # operator_avgs_outline_item.add_item(style_css)
            book.add_item(operator_avgs_outline_item)
            book.spine.append(operator_avgs_outline_item)

            for activity in operator.avgs:
                activity_outline_item = epub.EpubHtml(
                    uid=activity.id,
                    title=activity.name,
                    file_name=f"content/{self.OPERATOR_VOLUME_NAME}/{operator.id}/{self.OPERATOR_AVG_NAME}/{activity.id}/{self.INDEX_PAGE_NAME}",
                )
                activity_outline_item.set_content(self._activity_page(activity))
                # activity_outline_item.add_item(style_css)
                book.add_item(activity_outline_item)
                book.spine.append(activity_outline_item)

                for story in activity.stories:
                    story_item = epub.EpubHtml(
                        uid=story.id,
                        title=story.name,
                        file_name=f"content/{self.OPERATOR_VOLUME_NAME}/{operator.id}/{self.OPERATOR_AVG_NAME}/{activity.id}/{story.id}.xhtml",
                    )
                    story_item.set_content(self._story_page(story))
                    # story_item.add_item(style_css)
                    book.add_item(story_item)
                    book.spine.append(story_item)

        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        epub.write_epub(self.save_path, book)

    METADATA_PAGE_NAME = "_metadata.xhtml"
    INDEX_PAGE_NAME = "_index.xhtml"
    OPERATOR_VOLUME_NAME = "OPERATOR"
    OPERATOR_INFO_PAGE_NAME = "_info.xhtml"
    OPERATOR_STORIES_PAGE_NAME = "_story.xhtml"
    OPERATOR_AVG_NAME = "avg"
