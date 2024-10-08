<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="./docs/NoneBotPlugin.svg" width="300" height="300" alt="NoneBotPluginLogo"></a>
  <br>
</div>

<div align="center">

# nonebot-plugin-color-see-see

_✨ 给我点颜色看看，猜色块小游戏 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/FrostN0v0/nonebot-plugin-color-see-see.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-color-see-see">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-color-see-see.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="python">

</div>

## 📖 介绍

给我点颜色看看，猜色块小游戏

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-color-see-see

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-color-see-see
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-color-see-see
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-color-see-see
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-color-see-see
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_color_see_see"]

</details>


## 🎉 使用

> 记得使用命令前缀哦

### 指令表
| 指令 | 权限 | 参数 | 说明 |
|:-----:|:----:|:----:|:----:|
| color/给我点颜色看看 | 所有 | `-t` 或 `stop` | 开始猜色块游戏。传入`stop`时，效果同`停止猜色块`。参数`-t`可指定游戏超时时间（不超过300秒）。如`color -t 15` |
| 块+数字 | 所有 | 无 | 选择颜色不同的色块，如 `块1` 或 `块 1` |
| 停止猜色块/停止给我点颜色看看 | 所有 | 无 | 手动停止当前正在进行的猜色块游戏 |
| 无尽猜色块 | 所有 | 无 | 开始一场没有时间限制的猜色块游戏，仅可通过停止猜色块来停止 |

> 当参数 `-t` `--time` 传入 `0`，视为开启无尽猜色块游戏。开启后，只可通过指令停止游戏。

### 效果图
![示例图1](docs/example-1.png)
![示例图2](docs/example-2.png)