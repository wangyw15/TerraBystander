from ..gamedata import (
    Activity,
    ActivityType,
    GameDataForBook,
)

ACTIVITY_TYPE_LABEL: dict[str, str] = {
    "ACTIVITY_STORY": "SideStory",
    "MAIN_STORY": "MainLine",
    "MINI_STORY": "MiniStory",
    "NONE": "",
}


def generate_txt(data: GameDataForBook) -> str:
    """
    Generate txt content from game data

    :params data: game data

    :return: txt content
    """

    def _activities_content(activities: list[Activity], volume_title: str) -> str:
        _result = ""
        for activity in activities:
            _result += f"『{volume_title}』{activity.name}\n"
            for story in activity.stories:
                _result += f"「{story.name}」{story.avg_tag}\n"
                _result += story.description
                for line in story.texts:
                    if line.name != "":
                        _result += f"【{line.name}】"
                    _result += f"{line.text}\n"
            _result += "\n"
        return _result

    result = ""

    volumes: dict[str, list[Activity]] = {
        ActivityType.MAIN_STORY.value: [],
        ActivityType.ACTIVITY_STORY.value: [],
        ActivityType.MINI_STORY.value: [],
    }
    for activity in data.activities:
        volumes[activity.activity_type.value].append(activity)

    for volume_type, activities in volumes.items():
        result += _activities_content(activities, ACTIVITY_TYPE_LABEL[volume_type])

    for operator in data.operators:
        result += f"『干员』{operator.name}\n"
        result += f"{operator.profession.name} {operator.sub_profession}\n"
        result += operator.usage + "\n"
        result += operator.description + "\n"

        result += "「干员档案」\n"
        for line in operator.operator_stories:
            result += line.title + "\n"
            result += line.text + "\n"

        result += "「干员密录」\n"
        result += _activities_content(operator.avgs, "干员密录")

    return result.replace("\r\n", "\n")


__all__ = [
    "generate_txt",
]
