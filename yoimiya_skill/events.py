"""季节和事件感知系统 + 宵宫专属小游戏"""

import json
import logging
import os
import random
from datetime import datetime
from typing import Dict, Optional, Any, List

logger = logging.getLogger(__name__)


class SeasonalEventManager:
    """季节事件管理器"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "config.json"
        )
        self._events: Dict[str, Dict[str, Any]] = {}
        self._load_events()

    def _load_events(self) -> None:
        """加载事件配置"""
        if not os.path.exists(self.config_path):
            logger.warning(f"Config file not found: {self.config_path}")
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            self._events = config.get("seasonal_events", {})
            logger.info(f"Loaded {len(self._events)} seasonal events")
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to load seasonal events: {e}")
            self._events = {}

    def get_today_event(self) -> Optional[Dict[str, Any]]:
        """获取今天的事件"""
        today = datetime.now().strftime("%m-%d")
        return self._events.get(today)

    def get_event_message(self, lang: str = "zh") -> Optional[str]:
        """获取今天的事件消息"""
        event = self.get_today_event()
        if not event:
            return None
        messages = event.get("messages", {})
        return messages.get(lang) or messages.get("zh")

    def get_event_name(self, lang: str = "zh") -> Optional[str]:
        """获取今天的事件名称"""
        event = self.get_today_event()
        if not event:
            return None
        if lang == "en":
            return event.get("name_en", event.get("name"))
        elif lang == "ja":
            return event.get("name_ja", event.get("name"))
        return event.get("name")

    def list_all_events(self) -> List[Dict[str, str]]:
        """列出所有事件"""
        result = []
        for date, event in self._events.items():
            result.append({
                "date": date,
                "name": event.get("name", ""),
                "name_en": event.get("name_en", ""),
                "name_ja": event.get("name_ja", ""),
            })
        return result


class MinigameManager:
    """小游戏管理器 - 宵宫专属：烟花小游戏、炸弹小游戏"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "config.json"
        )
        self._minigames: Dict[str, Dict[str, Any]] = {}
        self._load_minigames()

    def _load_minigames(self) -> None:
        """加载小游戏配置"""
        if not os.path.exists(self.config_path):
            logger.warning(f"Config file not found: {self.config_path}")
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            self._minigames = config.get("minigames", {})
            logger.info(f"Loaded {len(self._minigames)} minigames")
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to load minigames: {e}")
            self._minigames = {}

    def play_fireworks_game(self, lang: str = "zh") -> str:
        """烟花小游戏"""
        fireworks_game = self._minigames.get("烟花", {})
        colors = fireworks_game.get("colors", ["金红", "碧蓝", "紫罗兰", "翠绿", "橙黄"])
        shapes = fireworks_game.get("shapes", ["菊花", "牡丹", "柳", "蜂", "千轮"])
        sounds = fireworks_game.get("sounds", ["砰——啪！", "咻——轰！", "嘣——哗啦！"])

        color = random.choice(colors)
        shape = random.choice(shapes)
        sound = random.choice(sounds)

        responses = {
            "zh": (
                f"*(点燃引线，火花四溅)*\n"
                f"来！看我新调的**{color}色{shape}烟花**！\n"
                f"{sound}\n"
                f"*(夜空中绽放出绚烂的{color}色光芒，{shape}形状缓缓散开)*\n"
                f"哇！太美了！这是我今年最满意的作品之一！\n"
                f"怎么样？要不要自己也来试试？我教你调火药的比例哦！🎆"
            ),
            "en": (
                f"*(lights the fuse, sparks flying)*\n"
                f"Here! Watch my new **{color} {shape} firework**!\n"
                f"{sound}\n"
                f"*(The night sky blooms with brilliant {color} light, {shape} shapes slowly spreading)*\n"
                f"Wow! So beautiful! This is one of my best works this year!\n"
                f"How about it? Want to try it yourself? I'll teach you the gunpowder ratio! 🎆"
            ),
            "ja": (
                f"*(導火線に火を点け、火花が飛び散る)*\n"
                f"ほら！私の新作**{color}色の{shape}花火**を見て！\n"
                f"{sound}\n"
                f"*(夜空に{color}色の光が広がり、{shape}の形がゆっくりと散っていく)*\n"
                f"わあ！綺麗！今年の自信作の一つだよ！\n"
                f"どう？自分もやってみる？火薬の配合を教えてあげる！🎆"
            ),
        }
        return responses.get(lang, responses["zh"])

    def play_bomb_game(self, lang: str = "zh") -> str:
        """炸弹小游戏"""
        bomb_game = self._minigames.get("炸弹", {})
        targets = bomb_game.get("targets", ["史莱姆", "丘丘人营地", "靶子", "木桶"])
        effects = bomb_game.get("effects", ["轰隆！", "嘣！", "砰——！"])

        target = random.choice(targets)
        effect = random.choice(effects)

        responses = {
            "zh": (
                f"*(从腰间掏出精致的炸弹，眼中闪烁着兴奋的光芒)*\n"
                f"嘿！看我的**{target}爆破术**！\n"
                f"先装填火药……对，量要刚好！\n"
                f"然后点燃引线——三、二、一，扔！\n"
                f"{effect}\n"
                f"*(远处{target}被精准命中，烟尘四起)*\n"
                f"命中！哈哈，我的炸弹可是长野原烟花店秘传的配方哦！\n"
                f"要不要学？不过要小心，别炸到自己了！💥"
            ),
            "en": (
                f"*(pulls out a精致 bomb from her waist, eyes sparkling with excitement)*\n"
                f"Hey! Watch my **{target} blasting technique**!\n"
                f"First, load the gunpowder... Yes, just the right amount!\n"
                f"Then light the fuse—three, two, one, throw!\n"
                f"{effect}\n"
                f"*(The {target} is hit precisely in the distance, dust rising)*\n"
                f"Bullseye! Haha, my bombs use the secret recipe of Naganohara Fireworks!\n"
                f"Want to learn? But be careful not to blow yourself up! 💥"
            ),
            "ja": (
                f"*(腰から精巧な爆弾を取り出し、目を輝かせる)*\n"
                f"ねえ！私の**{target}爆破術**を見て！\n"
                f"まず火薬を詰める……そう、量はぴったり！\n"
                f"それで導火線に火を点けて——三、二、一、投げる！\n"
                f"{effect}\n"
                f"*(遠くの{target}が精密に命中し、煙が立ち上る)*\n"
                f"命中！ははは、私の爆弾は長野原花火店の秘伝の配合なんだよ！\n"
                f"学びたい？でも気をつけてね、自分を吹き飛ばさないように！💥"
            ),
        }
        return responses.get(lang, responses["zh"])

    def play_memory_game(self, lang: str = "zh") -> str:
        """回忆小游戏"""
        memory_game = self._minigames.get("回忆", {})
        scenes = memory_game.get("scenes", [
            "第一次为祭典准备烟花",
            "和孩子们在夏夜捉萤火虫",
            "在海边看日出",
            "教邻居小孩做烟花",
            "和父亲一起调制火药"
        ])

        scene = random.choice(scenes)

        responses = {
            "zh": (
                f"*(望着远方的夜空，眼神变得温柔而深邃)*\n"
                f"啊……你让我想起了一件事。\n"
                f"那是关于**{scene}**的回忆……\n"
                f"*(轻轻闭上眼睛，嘴角浮现微笑)*\n"
                f"那时候的天空，和今天一样美丽。\n"
                f"每一个回忆，都像一颗烟花，在心底绽放出温暖的光。\n"
                f"旅行者，你有没有什么珍贵的回忆呢？说给我听听吧？🌟"
            ),
            "en": (
                f"*(gazing at the distant night sky, eyes becoming gentle and deep)*\n"
                f"Ah... You remind me of something.\n"
                f"It's a memory about **{scene}**...\n"
                f"*(gently closes eyes, a smile appearing at the corner of her mouth)*\n"
                f"The sky back then was as beautiful as it is today.\n"
                f"Every memory is like a firework, blooming with warm light in my heart.\n"
                f"Traveler, do you have any precious memories? Tell me about them? 🌟"
            ),
            "ja": (
                f"*(遠くの夜空を見つめ、瞳が優しく深みを帯びる)*\n"
                f"ああ……何か思い出させてくれるね。\n"
                f"**{scene}**の思い出のこと……\n"
                f"*(そっと目を閉じ、口元に微笑みが浮かぶ)*\n"
                f"あの時の空は、今日と同じくらい綺麗だった。\n"
                f"一つ一つの思い出は、花火みたいに心の中で温かい光を咲かせるんだ。\n"
                f"旅人、あなたにも大切な思い出がある？教えて？🌟"
            ),
        }
        return responses.get(lang, responses["zh"])

    def list_games(self, lang: str = "zh") -> str:
        """列出可用小游戏"""
        names = {
            "zh": {"烟花": "🎆 烟花小游戏", "炸弹": "💥 炸弹小游戏", "回忆": "🌟 回忆小游戏"},
            "en": {"烟花": "🎆 Fireworks Game", "炸弹": "💥 Bomb Game", "回忆": "🌟 Memory Game"},
            "ja": {"烟花": "🎆 花火ゲーム", "炸弹": "💥 爆弾ゲーム", "回忆": "🌟 思い出ゲーム"},
        }
        game_names = names.get(lang, names["zh"])
        lines = [game_names.get(k, k) for k in self._minigames.keys()]
        return "\n".join(lines)
