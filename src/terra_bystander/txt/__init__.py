from datetime import datetime

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

    # metadata
    result += "【游戏数据版本】" + data.metadata.version + "\n"
    result += "【游戏数据日期】" + data.metadata.date + "\n"
    result += "【文件生成日期】" + datetime.now().strftime("%Y-%m-%d") + "\n"
    result += "\n"

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

        if len(operator.operator_stories) > 0:
            result += "「干员档案」\n"
            for line in operator.operator_stories:
                result += line.title + "\n"
                result += line.text + "\n"

        if operator.uniequips is not None and len(operator.uniequips) > 0:
            result += "「模组」\n"
            for uniequip in operator.uniequips:
                result += (
                    "【"
                    + uniequip.name
                    + "（"
                    + uniequip.type_name_1
                    + (
                        ("-" + uniequip.type_name_2)
                        if uniequip.type_name_2 is not None
                        else ""
                    )
                    + "）】\n"
                )
                result += uniequip.description + "\n"

        if len(operator.voices) > 0:
            result += "语音记录\n"
            for voice in operator.voices:
                result += "【" + voice.title + "】" + voice.text + "\n"

        if len(operator.avgs) > 0:
            result += "「干员密录」\n"
            result += _activities_content(operator.avgs, "干员密录")

    return result.replace("\r\n", "\n")


__all__ = [
    "generate_txt",
]
