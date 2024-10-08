import asyncio
from asyncio import TimerHandle

from nonebot import require
from nonebot.exception import FinishedException
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

from .data_source import ColorGame

require("nonebot_plugin_uninfo")
require("nonebot_plugin_alconna")
from nonebot_plugin_uninfo import Uninfo
from nonebot_plugin_alconna import (
    Args,
    Match,
    Option,
    Alconna,
    UniMessage,
    CommandMeta,
    on_alconna,
)

__plugin_meta__ = PluginMetadata(
    name="给我点颜色瞧瞧",
    description="给你点颜色瞧瞧？给我点颜色瞧瞧（让我康康！",
    usage=(
        "发送 color/给我点颜色看看 开始游戏\n"
        "可使用 -t/--time/time 秒数 自定义超时结束时间\n"
        "可使用 -s/--stop/stop 手动停止当前游戏\n"
        "发送 无尽猜色块 开始无超时的无尽模式游戏\n"
        "发送 b/块+数字 猜出颜色不同的色块\n"
    ),
    type="application",
    homepage="https://github.com/FrostN0v0/nonebot-plugin-color-see-see",
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_alconna", "nonebot_plugin_uninfo"
    ),
    extra={
        "author": "FrostN0v0 <1614591760@qq.com>",
        "version": "0.2.0",
    },
)

color_game = on_alconna(
    Alconna(
        "color",
        Option("-t|--time|time", Args["time", int], help_text="设定超时时间"),
        Option("-s|--stop|stop", help_text="停止游戏"),
        meta=CommandMeta(
            description=__plugin_meta__.description,
            usage=__plugin_meta__.usage,
            example="color -t 15",
            fuzzy_match=True,
        ),
    ),
    use_cmd_start=True,
    aliases=("猜色块", "给我点颜色看看", "给我点颜色瞧瞧"),
)
color_game.shortcut(
    "停止猜色块|停止给我点颜色看看|停止给我点颜色瞧瞧",
    {"prefix": True, "args": ["--stop"]},
)
color_game.shortcut("无尽猜色块", {"prefix": True, "args": ["--time 0"]})

block_color = on_alconna(
    Alconna(
        "block",
        Args["block", int],
        meta=CommandMeta(
            description="猜色块",
            usage=__plugin_meta__.usage,
            example="块1",
            fuzzy_match=True,
        ),
    ),
    use_cmd_start=True,
    aliases=("块", "b", "B"),
)

games: dict[str, ColorGame] = {}
timers: dict[str, tuple[TimerHandle | None, int | None]] = {}
players: dict[str, dict[str, int]] = {}
default_difficulty = 2


@color_game.assign("$main")
async def _(user_session: Uninfo):
    user_name = user_session.user.name
    group_id = str(user_session.scene.id)
    if games.get(group_id):
        await UniMessage("给我点颜色看看正在进行中，请勿重复开局\n").finish()
    game = ColorGame(default_difficulty)
    games[group_id] = game
    msg = UniMessage.text(
        f"{user_name} 发起了小游戏 给我点颜色看看！请发送“块+数字”，挑出颜色不同的色块\n"
    )
    msg += UniMessage.image(raw=game.get_color_img())
    await UniMessage.send(msg)
    set_timeout(group_id)


@color_game.assign("time")
async def _(user_session: Uninfo, time: Match[int]):
    user_name = user_session.user.name
    group_id = str(user_session.scene.id)
    timeout: int | None = None
    if games.get(group_id):
        await UniMessage("给我点颜色看看正在进行中，请勿重复开局\n").finish()
    if time.available:
        if time.result == 0:
            timeout = None
        elif time.result > 300:
            await UniMessage(
                "您输入的时间超过300秒，是否开启无尽模式？无尽模式下，"
                "只有通过 color stop 才能停止游戏。若要开启无尽模式，请输入 无尽猜色块"
            ).finish()
        else:
            timeout = time.result
    else:
        timeout = 20

    game = ColorGame(default_difficulty)
    games[group_id] = game
    msg = UniMessage.text(
        f"{user_name} 发起了小游戏 给我点颜色看看！请发送“块+数字”，挑出颜色不同的色块\n"
    )
    msg += UniMessage.image(raw=game.get_color_img())
    await UniMessage.send(msg)
    set_timeout(group_id, timeout)


@color_game.assign("stop")
async def _(user_session: Uninfo):
    group_id = str(user_session.scene.id)
    if not games.get(group_id):
        await UniMessage(
            "当前没有进行中的给我点颜色看看小游戏，请发送 给我点颜色看看 开一局吧"
        ).finish()
    else:
        await stop_game_timeout(group_id)


@block_color.handle()
async def _(user_session: Uninfo, block: Match[int]):
    group_id = str(user_session.scene.id)
    user_id = str(user_session.user.id)
    user_name = user_session.user.name if user_session.user.name is not None else user_id
    if not games.get(group_id):
        await UniMessage(
            "当前没有进行中的给我点颜色看看小游戏，请发送 给我点颜色看看 开一局吧"
        ).finish()
    game = games[str(user_session.scene.id)]
    if timeout := timers.get(group_id):
        timeout = timeout[1]
        set_timeout(group_id, timeout)
    if game.diff_block == block.result:
        game.add_score(user_id, user_name)
        await UniMessage.text(
            f"猜对啦，获得积分{game.block_column}分，现有积分{game.get_scores(user_id)}分"
        ).send()
        await UniMessage.image(raw=game.get_next_img()).finish()


def stop_game(group_id: str):
    if timer := timers.pop(group_id, None):
        if timer[0]:
            timer[0].cancel()
    games.pop(group_id, None)


async def stop_game_timeout(group_id: str):
    game = games.get(group_id, None)
    stop_game(group_id)
    if game:
        await UniMessage.text(f"本次答案为 块[{game.get_diff_block()}] 哦").send()
        sorted_scores = dict(
            sorted(game.scores.items(), key=lambda item: item[1].score, reverse=True)
        )
        if not sorted_scores:
            try:
                await UniMessage("游戏结束，没有玩家得分").finish()
            except FinishedException:
                return
        msg = UniMessage.text("游戏结束，积分排行榜：\n")
        for step, (_, scores) in enumerate(sorted_scores.items()):
            msg += UniMessage.text(f"{step + 1}. {scores.user_name}，{scores.score}分\n")
        await UniMessage(msg).send()


def set_timeout(group_id: str, timeout: int | None = 20):
    if timer := timers.get(group_id, None):
        if timer[0]:
            timer[0].cancel()
    if timeout is not None and timeout > 0:
        loop = asyncio.get_running_loop()
        timer_handle = loop.call_later(
            timeout, lambda: asyncio.ensure_future(stop_game_timeout(group_id))
        )
        timers[group_id] = (timer_handle, timeout)
    else:
        # 无尽模式
        timers[group_id] = (None, None)
