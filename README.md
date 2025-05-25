# TerraBystander

> 想看剧情不想玩

泰拉观者，将明日方舟剧情生成PDF

# 编译

安装[uv](https://docs.astral.sh/uv/getting-started/installation/)

安装[typst](https://github.com/typst/typst/releases)

下载游戏数据[Kengxxiao/ArknightsGameData](https://github.com/Kengxxiao/ArknightsGameData)

运行以下命令以提取剧情数据

```shell
uv sync
# path_to_secondary_gamedata 主要是为了英文名，可以不提供
uv run main path_to_gamedata path_to_secondary_gamedata
```

将生成的`data.json`复制到`template`文件夹下，运行命令

```shell
typst compile TerraBystander.typ --input nickname=博士名字 --input data=data.json的路径
```

`TerraBystander.pdf`即为生成结果
