import asyncio
from asyncio import TimerHandle

from nonebot import require
from nonebot.exception import FinishedException
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

from .data_source import ColorGame

require("nonebot_plugin_uninfo")
require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import (
    Args,
    Match,
    Option,
    Alconna,
    CommandMeta,
    UniMessage,
    on_alconna
    )
from nonebot_plugin_uninfo import Uninfo

__plugin_meta__ = PluginMetadata(
    name="给我点颜色瞧瞧",
    description="给你点颜色瞧瞧？给我点颜色瞧瞧（让我康康！",
    usage=(
        "发送 color/给我点颜色看看 开始游戏\n"
        "可使用 -t/--time/time 秒数 自定义超时结束时间\n"
        "发送 b/块+数字 猜出颜色不同的色块\n"
           ),
    type="application",
    homepage="https://github.com/FrostN0v0/nonebot-plugin-color-see-see",
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_alconna", "nonebot_plugin_uninfo"
    ),
    extra={
        "author": "FrostN0v0 <1614591760@qq.com>",
        "version": "0.1.1",
    },
)

color_game = on_alconna(
    Alconna("color",
            Option("-t|--time|time", Args["time", int], help_text="设定超时时间"),
            meta=CommandMeta(
                description=__plugin_meta__.description,
                usage=__plugin_meta__.usage,
                example="color -t 15",
                fuzzy_match=True,
            ),),
    aliases=("猜色块", "给我点颜色看看", "给我点颜色瞧瞧"),
)

block_color = on_alconna(
    Alconna("block", Args["block", int],
            meta=CommandMeta(
                description="猜色块",
                usage=__plugin_meta__.usage,
                example="块1",
                fuzzy_match=True,
            )),
    aliases=("块", "b"),
)

games: dict[str, ColorGame] = {}
timers: dict[str, tuple[TimerHandle, int]] = {}
players: dict[str, dict[str, int]] = {}
default_difficulty = 2


@color_game.handle()
async def _(user_session: Uninfo, time: Match[int]):
    user_name = user_session.user.name
    group_id = str(user_session.scene.id)
    if games.get(group_id):
        await color_game.finish("给我点颜色看看正在游戏中，请对局结束后再开局\n")
    game = ColorGame(default_difficulty)
    games[group_id] = game
    if time.available:
        set_timeout(group_id, time.result)
    else:
        set_timeout(group_id)
    msg = UniMessage.text(f"{user_name}"
                          "发起了小游戏 给我点颜色看看！请发送“块+数字”，"
                          "挑出颜色不同的色块\n")
    msg += UniMessage.image(raw=game.get_color_img())
    await color_game.send(msg)


@block_color.handle()
async def _(user_session: Uninfo, block: Match[int]):
    group_id = str(user_session.scene.id)
    user_id = str(user_session.user.id)
    if user_session.user.name is not None:
        user_name = user_session.user.name
    else:
        user_name = user_id
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
        timer[0].cancel()
    games.pop(group_id, None)


async def stop_game_timeout(group_id: str):
    game = games.get(group_id, None)
    stop_game(group_id)
    if game:
        sorted_scores = dict(
            sorted(game.scores.items(), key=lambda item: item[1].score, reverse=True)
            )
        if not sorted_scores:
            try:
                await UniMessage(
                    f"游戏已结束，没有玩家得分,本次答案为块[{game.get_diff_block()}]哦"
                    ).finish()
            except FinishedException:
                return
        await UniMessage.text(f"本次答案为块[{game.get_diff_block()}]哦").send()
        msg = UniMessage.text("游戏结束，积分排行榜：\n")
        for step, (_, scores) in enumerate(sorted_scores.items()):
            msg += UniMessage.text(f"{step + 1}.{scores.user_name}，{scores.score}分\n")
        await msg.send()


def set_timeout(group_id: str, timeout: int = 20):
    if timer := timers.get(group_id, None):
        timer[0].cancel()
    loop = asyncio.get_running_loop()
    timer = loop.call_later(
        timeout, lambda: asyncio.ensure_future(stop_game_timeout(group_id))
    )
    timers[group_id] = (timer, timeout)
