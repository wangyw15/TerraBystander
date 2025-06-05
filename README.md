# TerraBystander

> 想看剧情不想玩

泰拉观者，将明日方舟剧情生成PDF

# 安装环境

安装[uv](https://docs.astral.sh/uv/getting-started/installation/)

安装[typst](https://github.com/typst/typst/releases)

```shell
uv sync
```

# 准备数据

下载游戏数据[Kengxxiao/ArknightsGameData](https://github.com/Kengxxiao/ArknightsGameData)

# 运行

## PDF

### 导出JSON

运行以下命令以提取剧情数据

```shell
uv run main path_to_gamedata -s path_to_secondary_gamedata
# -s path_to_secondary_gamedata主要是为了英文名，可以不提供
```

### 生成PDF

将生成的`data.json`复制到`template`文件夹下，运行命令

```shell
# input均为可选项
typst compile TerraBystander.typ --input nickname=博士名字 --input data=data.json的路径 --input resource=ArknightsGameResource
```

`TerraBystander.pdf`即为生成结果

## Epub

> Experimental

```shell
uv run main path_to_gamedata -s path_to_secondary_gamedata -t epub
```

## TXT

```shell
uv run main path_to_gamedata -s path_to_secondary_gamedata -t txt
```
