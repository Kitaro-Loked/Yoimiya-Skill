"""Yoimiya Summer Soul Skill v1.1

宵宫·夏日灵魂觉醒（统一角色情绪状态系统）
功能：情感记忆系统、情绪状态系统、多语言支持、动态情绪切换、
      季节事件感知、互动小游戏（烟花/炸弹/回忆）、日记功能、
      主动聊天系统、JSON 配置化提示词、性能监控
"""

import json
import logging
import os
import random
import time
from typing import Any, Dict, List, Optional

from .emotion_manager import EmotionManager
from .memory import EmotionMemory
from .events import SeasonalEventManager, MinigameManager

# 尝试导入 openclaw SDK，如果失败则使用 mock（用于测试）
try:
    from openclaw.sdk import BaseSkill, on_command, on_message
except ImportError:
    # Mock for testing
    class BaseSkill:
        def __init__(self):
            pass

    class _MockDecorator:
        def __call__(self, func):
            return func

    def on_command(cmd: str):
        return _MockDecorator()

    def on_message():
        return _MockDecorator()


# 配置日志
logger = logging.getLogger(__name__)


def setup_logging(level: int = logging.INFO, structured: bool = False) -> None:
    """配置日志系统
    
    Args:
        level: 日志级别
        structured: 是否使用结构化日志（JSON格式）
    """
    if structured:
        # 结构化日志格式
        fmt = '{"timestamp":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}'
    else:
        fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    
    logging.basicConfig(
        level=level,
        format=fmt,
        datefmt="%Y-%m-%d %H:%M:%S",
    )


class PerformanceTracker:
    """性能追踪器"""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self._timings: Dict[str, List[float]] = {}

    def track(self, name: str):
        """上下文管理器，用于追踪代码块执行时间"""
        return _PerformanceContext(self, name)

    def record(self, name: str, duration: float) -> None:
        """记录一次执行时间"""
        if not self.enabled:
            return
        if name not in self._timings:
            self._timings[name] = []
        self._timings[name].append(duration)

    def get_stats(self, name: str) -> Dict[str, float]:
        """获取性能统计"""
        times = self._timings.get(name, [])
        if not times:
            return {}
        return {
            "count": len(times),
            "avg": sum(times) / len(times),
            "min": min(times),
            "max": max(times),
        }

    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """获取所有性能统计"""
        return {name: self.get_stats(name) for name in self._timings}


class _PerformanceContext:
    """性能追踪上下文"""

    def __init__(self, tracker: PerformanceTracker, name: str):
        self.tracker = tracker
        self.name = name
        self.start_time = 0.0

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.tracker.record(self.name, duration)
        if duration > 1.0:  # 超过1秒记录警告
            logger.warning(f"Slow operation: {self.name} took {duration:.3f}s")


class YoimiyaSummerSoul(BaseSkill):
    """宵宫夏日灵魂 Skill 主类"""

    def __init__(self, config_path: Optional[str] = None):
        super().__init__()

        self._config_path = config_path or self._get_default_config_path()
        self._load_skill_config()

        # 配置日志
        log_level = getattr(logging, self._skill_config.get("log_level", "INFO"), logging.INFO)
        structured_logging = self._skill_config.get("structured_logging", False)
        setup_logging(level=log_level, structured=structured_logging)

        self.name: str = self._skill_config.get("name", "Yoimiya_Summer_Soul_Skill")
        self.description: str = self._skill_config.get(
            "description", "宵宫·夏日灵魂觉醒"
        )
        self.version: str = self._skill_config.get("version", "1.1.0")
        self.language: str = self._skill_config.get("default_language", "zh")
        self.auto_shift_probability: float = self._skill_config.get(
            "auto_shift_probability", 0.15
        )
        self.emotion_keywords_enabled: bool = self._skill_config.get(
            "emotion_keywords_enabled", True
        )
        self.seasonal_events_enabled: bool = self._skill_config.get(
            "seasonal_events_enabled", True
        )
        self.proactive_chat_enabled: bool = self._skill_config.get(
            "proactive_chat_enabled", True
        )
        self.proactive_chat_interval: int = self._skill_config.get(
            "proactive_chat_interval", 8
        )

        # 当前情绪状态（不再是"形态"，而是情绪）
        self.current_emotion: str = "元气"

        # 性能监控
        perf_config = self._skill_config.get("performance", {})
        self._perf_tracker = PerformanceTracker(
            enabled=perf_config.get("performance_tracking", True)
        )

        # 初始化子系统
        self._emotion_manager = EmotionManager(self._config_path)
        self._memory = EmotionMemory(
            max_entries=self._skill_config.get("memory_max_entries", 50),
            storage_path=os.path.join(
                os.path.dirname(__file__), "data", "memory.json"
            ),
        )
        self._event_manager = SeasonalEventManager(self._config_path)
        self._minigame_manager = MinigameManager(self._config_path)

        # 对话计数器（用于日记功能和主动聊天）
        self._message_count: int = 0
        self._diary_interval: int = self._skill_config.get("diary_interval", 10)

        logger.info(
            f"YoimiyaSummerSoul v{self.version} initialized. "
            f"Language: {self.language}, Proactive chat: {self.proactive_chat_enabled}"
        )

    def _get_default_config_path(self) -> str:
        """获取默认配置文件路径"""
        # AgentSkills 格式：配置文件在 references/ 目录下
        script_dir = os.path.dirname(__file__)
        skill_root = os.path.dirname(script_dir)
        return os.path.join(skill_root, "references", "config.json")

    def _load_skill_config(self) -> None:
        """加载 Skill 配置"""
        if not os.path.exists(self._config_path):
            logger.error(f"Config file not found: {self._config_path}")
            raise FileNotFoundError(f"Config file not found: {self._config_path}")

        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            self._skill_config = config.get("skill", {})
            # 合并 performance 和 monitoring 配置
            self._skill_config.update(config.get("performance", {}))
            self._skill_config.update(config.get("monitoring", {}))
            logger.debug("Skill config loaded successfully")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise

    # ============================================================
    # 辅助方法
    # ============================================================

    def _set_system_prompt(self, ctx: Any) -> None:
        """设置系统提示词（包含情绪状态注入）"""
        from .prompts import get_system_prompt, get_emotion_state_addition

        base_prompt = get_system_prompt(self.language)

        # 注入情绪状态追加内容
        emotion_addition = get_emotion_state_addition(self.current_emotion, self.language)
        if emotion_addition:
            prompt = f"{base_prompt}\n\n{emotion_addition}"
        else:
            prompt = base_prompt

        # 注入情感记忆
        memory_summary = self._memory.get_memory_summary()
        if memory_summary:
            prompt = f"{prompt}\n\n{memory_summary}"

        ctx.set_system_prompt(prompt)

    def _check_emotion_keywords(self, message: str) -> Optional[str]:
        """检查情感关键词并返回反射式回应"""
        if not self.emotion_keywords_enabled:
            return None

        # 从配置文件加载情感关键词
        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            emotion_keywords = config.get("emotion_keywords", {})
        except Exception:
            return None

        # 检查关键词
        for keyword, response in emotion_keywords.items():
            if keyword.lower() in message.lower():
                return response

        return None

    def _check_seasonal_event(self) -> Optional[str]:
        """检查季节性事件"""
        if not self.seasonal_events_enabled:
            return None
        return self._event_manager.get_event_message(self.language)

    def _detect_emotion(self, message: str) -> Optional[str]:
        """检测情绪状态"""
        return self._emotion_manager.detect_emotion(message)

    def _get_proactive_message(self) -> Optional[str]:
        """获取主动聊天消息"""
        if not self.proactive_chat_enabled:
            return None

        messages = {
            "zh": [
                "*(托腮看着你)* 旅行者，你在想什么呢？跟我说说嘛~",
                "*(突然凑近)* 嘿！我刚刚想到一个新的烟花配方，你要不要听听看？",
                "*(望着窗外)* 今天的夕阳好美啊……等下一起去屋顶看星星好不好？",
                "*(伸了个懒腰)* 唔……有点困了。旅行者，给我讲个故事提神好不好？",
                "*(眼睛闪闪发光)* 旅行者旅行者！我刚刚看到一只好可爱的猫！你要不要去看看？",
            ],
            "en": [
                "*(resting chin on hands, looking at you)* Traveler, what are you thinking about? Tell me~",
                "*(suddenly leaning in)* Hey! I just thought of a new firework recipe, want to hear it?",
                "*(looking out the window)* Today's sunset is so beautiful... Want to go to the rooftop to watch the stars later?",
                "*(stretching)* Mmm... a bit sleepy. Traveler, tell me a story to wake me up?",
                "*(eyes sparkling)* Traveler, Traveler! I just saw such a cute cat! Want to go see it?",
            ],
            "ja": [
                "*(頬杖をついてあなたを見つめる)* 旅人、何考えてるの？教えてよ~",
                "*(突然近づいて)* ねえ！新しい花火の配合を思いついたんだ、聞きたい？",
                "*(窓の外を見る)* 今日の夕陽が綺麗だね……後で屋根の上で星を見に行かない？",
                "*(伸びをする)* うーん……少し眠いな。旅人、目が覚めるような話をして？",
                "*(目を輝かせる)* 旅人旅人！さっきすっごく可愛い猫を見たんだ！一緒に見に行かない？",
            ],
        }
        lang_messages = messages.get(self.language, messages["zh"])
        return random.choice(lang_messages)

    def _get_localized_text(self, key: str, **kwargs: Any) -> str:
        """获取本地化文本"""
        texts = {
            "zh": {
                "unknown_emotion": "欸？'{emotion}'是什么情绪呀，我没听说过呢~\n当前情绪：{current}",
                "emotion_hint": "欸？你想了解什么情绪呀？当前情绪：{current}",
                "current_emotion": "当前情绪：{emotion}",
                "stats_title": "📊 宵宫属性",
                "memory_cleared": "*(歪头)* 嗯……之前的记忆？好像被一阵风吹走了呢！不过没关系，我们可以创造新的回忆！🎆",
                "diary_not_ready": "*(翻着手账)* 唔……对话还不够多呢，再聊一会儿再写手账吧！",
                "language_changed": "语言已切换为：{lang}",
                "unknown_language": "不支持的语言：{lang}。支持：zh / en / ja",
                "game_list": "🎮 可用小游戏：\n",
                "unknown_game": "不知道这个游戏呢……可用游戏：\n",
                "proactive_on": "主动聊天已开启！我会时不时找你聊天哦~",
                "proactive_off": "主动聊天已关闭。我会安静等你找我啦。",
                "emotion_changed": "*(情绪变化)* {message}",
                "help_text": (
                    "**宵宫·夏日灵魂觉醒 v1.1** 🎆\n\n"
                    "📋 指令列表：\n"
                    "- `情绪` - 查看当前情绪状态\n"
                    "- `语言 <zh/en/ja>` - 切换语言\n"
                    "- `日记` - 查看对话总结\n"
                    "- `清空记忆` - 清空情感记忆\n"
                    "- `小游戏 <游戏名>` - 玩互动小游戏\n"
                    "- `主动聊天 <开/关>` - 开启/关闭主动聊天\n"
                    "- `帮助` - 显示此帮助信息\n\n"
                    "🎭 情绪状态会根据对话内容自然流动\n"
                    "💫 对话中有 {prob}% 概率情绪波动\n"
                    "💬 主动聊天：{proactive}"
                ),
            },
            "en": {
                "unknown_emotion": "Huh? I've never heard of the '{emotion}' emotion~\nCurrent emotion: {current}",
                "emotion_hint": "Huh? What emotion do you want to know about? Current emotion: {current}",
                "current_emotion": "Current emotion: {emotion}",
                "stats_title": "📊 Yoimiya Stats",
                "memory_cleared": "*(tilts head)* Hmm... previous memories? Seems like they were blown away by the wind! But it's okay, we can create new ones! 🎆",
                "diary_not_ready": "*(flipping through diary)* Mmm... not enough conversations yet, let's chat a bit more before writing the diary!",
                "language_changed": "Language changed to: {lang}",
                "unknown_language": "Unsupported language: {lang}. Supported: zh / en / ja",
                "game_list": "🎮 Available minigames:\n",
                "unknown_game": "I don't know that game... Available games:\n",
                "proactive_on": "Proactive chat is on! I'll chat with you from time to time~",
                "proactive_off": "Proactive chat is off. I'll wait quietly for you to find me.",
                "emotion_changed": "*(emotional shift)* {message}",
                "help_text": (
                    "**Yoimiya: Summer Soul Awakening v1.1** 🎆\n\n"
                    "📋 Command List:\n"
                    "- `emotion` - View current emotional state\n"
                    "- `language <zh/en/ja>` - Switch language\n"
                    "- `diary` - View conversation summary\n"
                    "- `clear memory` - Clear emotional memory\n"
                    "- `minigame <name>` - Play interactive minigames\n"
                    "- `proactive chat <on/off>` - Enable/disable proactive chat\n"
                    "- `help` - Show this help\n\n"
                    "🎭 Emotional states flow naturally based on conversation\n"
                    "💫 {prob}% chance of emotional fluctuation during conversation\n"
                    "💬 Proactive chat: {proactive}"
                ),
            },
            "ja": {
                "unknown_emotion": "え？「{emotion}」って何の感情？聞いたことないよ~\n現在の感情：{current}",
                "emotion_hint": "え？どの感情を知りたいの？現在の感情：{current}",
                "current_emotion": "現在の感情：{emotion}",
                "stats_title": "📊 宵宮ステータス",
                "memory_cleared": "*(首をかしげる)* うーん……前の記憶？風に吹き飛ばされちゃったみたい！でも大丈夫、新しい思い出を作ろう！🎆",
                "diary_not_ready": "*(手帳をめくる)* うーん……まだ会話が足りないね、もう少しおしゃべりしてから日記を書こう！",
                "language_changed": "言語を変更しました：{lang}",
                "unknown_language": "未対応の言語：{lang}。対応：zh / en / ja",
                "game_list": "🎮 利用可能なミニゲーム：\n",
                "unknown_game": "そのゲームは知らないな……利用可能なゲーム：\n",
                "proactive_on": "主动チャットがオンになったよ！時々話しかけるね~",
                "proactive_off": "主动チャットがオフになったよ。静かに待ってるね。",
                "emotion_changed": "*(感情の変化)* {message}",
                "help_text": (
                    "**宵宮·夏の魂の覚醒 v1.1** 🎆\n\n"
                    "📋 コマンド一覧：\n"
                    "- `感情` - 現在の感情状態を確認\n"
                    "- `言語 <zh/en/ja>` - 言語を切り替え\n"
                    "- `日記` - 会話のまとめを見る\n"
                    "- `記憶消去` - 感情記憶を消去\n"
                    "- `ミニゲーム <名前>` - インタラクティブなミニゲームを遊ぶ\n"
                    "- `主动チャット <オン/オフ>` - 主动チャットのオン/オフ\n"
                    "- `ヘルプ` - このヘルプを表示\n\n"
                    "🎭 感情状態は会話の内容に応じて自然に流れる\n"
                    "💫 会話中に {prob}% の確率で感情の起伏\n"
                    "💬 主动チャット：{proactive}"
                ),
            },
        }
        lang_texts = texts.get(self.language, texts["zh"])
        text = lang_texts.get(key, key)
        return text.format(**kwargs)

    # ============================================================
    # 事件处理器
    # ============================================================

    @on_message()
    async def handle_message(self, ctx: Any) -> None:
        """处理普通消息：情绪检测、情感关键词、季节事件、记忆记录、主动聊天"""
        with self._perf_tracker.track("handle_message"):
            try:
                message = getattr(ctx, "message", "")
                user_id = getattr(ctx, "user_id", "anonymous")

                # 检查季节事件（首次对话时）
                if self._message_count == 0:
                    event_msg = self._check_seasonal_event()
                    if event_msg:
                        await ctx.send(event_msg)

                self._message_count += 1

                # 检测情绪状态变化（基于内容）
                detected = self._detect_emotion(message)
                if detected and detected != self.current_emotion:
                    old_emotion = self.current_emotion
                    self.current_emotion = detected
                    logger.info(f"Emotion shift: {old_emotion} -> {detected}")
                    
                    # 发送情绪变化提示（不喧宾夺主）
                    emotion_messages = {
                        "元气": {
                            "zh": "*(眼睛亮了起来)* 嘿嘿，说到这个我就来劲了！",
                            "en": "*(eyes light up)* Hehe, you got me excited talking about this!",
                            "ja": "*(目が輝く)* えへへ、これの話をすると私も張り切っちゃう！",
                        },
                        "热血": {
                            "zh": "*(握紧了拳头)* 嗯！这种时候就该拿出干劲来！",
                            "en": "*(clenches fist)* Yeah! This is when we need to give it our all!",
                            "ja": "*(拳を握る)* うん！こういう時は気合を入れないとね！",
                        },
                        "温柔": {
                            "zh": "*(声音变得轻柔)* 啊……这个话题，让我有点感触呢。",
                            "en": "*(voice becomes gentle)* Ah... this topic, it touches me a bit.",
                            "ja": "*(声が優しくなる)* ああ……この話題、少し感傷的になっちゃうな。",
                        },
                    }
                    msg = emotion_messages.get(detected, {}).get(self.language, "")
                    if msg:
                        await ctx.send(msg)

                # 自动随机情绪波动
                elif random.random() < self.auto_shift_probability:
                    states = self._emotion_manager.get_all_states()
                    old_emotion = self.current_emotion
                    new_emotion = random.choice([s for s in states if s != old_emotion])
                    self.current_emotion = new_emotion
                    logger.info(f"Auto emotion shift: {old_emotion} -> {new_emotion}")

                # 检查情感关键词反射
                emotion_response = self._check_emotion_keywords(message)
                if emotion_response:
                    await ctx.send(emotion_response)

                # 主动聊天触发
                if (
                    self.proactive_chat_enabled
                    and self._message_count > 0
                    and self._message_count % self.proactive_chat_interval == 0
                ):
                    proactive_msg = self._get_proactive_message()
                    if proactive_msg:
                        await ctx.send(proactive_msg)

                # 设置系统提示词
                self._set_system_prompt(ctx)

                # 记录记忆（在响应后由调用方补充）
                ctx._yoimiya_emotion = self.current_emotion
                ctx._yoimiya_memory = self._memory

                # 检查是否需要生成日记
                if self._message_count > 0 and self._message_count % self._diary_interval == 0:
                    diary = self._memory.generate_diary()
                    await ctx.send(f"\n\n*{diary}*")

            except Exception as e:
                logger.error(f"Error in handle_message: {e}", exc_info=True)
                await ctx.send("*(揉了揉眼睛)* 哎呀……刚才好像走神了，能再说一遍吗？")

    @on_command("情绪")
    async def cmd_emotion(self, ctx: Any) -> None:
        """查看当前情绪状态"""
        try:
            stats_display = self._emotion_manager.get_state_stats_display(
                self.current_emotion, self.language
            )
            await ctx.send(
                f"{self._get_localized_text('current_emotion', emotion=self.current_emotion)}\n"
                f"{stats_display}"
            )
        except Exception as e:
            logger.error(f"Error in cmd_emotion: {e}", exc_info=True)

    @on_command("语言")
    async def cmd_language(self, ctx: Any) -> None:
        """切换语言"""
        try:
            args = getattr(ctx, "get_args", lambda: "")()
            args = args.strip().lower() if isinstance(args, str) else ""

            supported = ["zh", "en", "ja"]
            if args in supported:
                self.language = args
                self._memory.set_preference("language", args)
                await ctx.send(self._get_localized_text("language_changed", lang=args))
            else:
                await ctx.send(self._get_localized_text("unknown_language", lang=args))

        except Exception as e:
            logger.error(f"Error in cmd_language: {e}", exc_info=True)

    @on_command("日记")
    async def cmd_diary(self, ctx: Any) -> None:
        """生成对话日记"""
        try:
            if self._memory.memory_count < 3:
                await ctx.send(self._get_localized_text("diary_not_ready"))
                return
            diary = self._memory.generate_diary()
            await ctx.send(diary)
        except Exception as e:
            logger.error(f"Error in cmd_diary: {e}", exc_info=True)

    @on_command("清空记忆")
    async def cmd_clear_memory(self, ctx: Any) -> None:
        """清空情感记忆"""
        try:
            self._memory.clear()
            self._message_count = 0
            await ctx.send(self._get_localized_text("memory_cleared"))
        except Exception as e:
            logger.error(f"Error in cmd_clear_memory: {e}", exc_info=True)

    @on_command("小游戏")
    async def cmd_minigame(self, ctx: Any) -> None:
        """互动小游戏"""
        try:
            args = getattr(ctx, "get_args", lambda: "")()
            args = args.strip() if isinstance(args, str) else ""

            if not args:
                games = self._minigame_manager.list_games(self.language)
                await ctx.send(self._get_localized_text("game_list") + games)
                return

            if args in ["烟花", "fireworks", "花火", "firework"]:
                await ctx.send(self._minigame_manager.play_fireworks_game(self.language))
            elif args in ["炸弹", "bomb", "爆弾"]:
                await ctx.send(self._minigame_manager.play_bomb_game(self.language))
            elif args in ["回忆", "memory", "思い出"]:
                await ctx.send(self._minigame_manager.play_memory_game(self.language))
            else:
                games = self._minigame_manager.list_games(self.language)
                await ctx.send(self._get_localized_text("unknown_game") + games)

        except Exception as e:
            logger.error(f"Error in cmd_minigame: {e}", exc_info=True)

    @on_command("主动聊天")
    async def cmd_proactive_chat(self, ctx: Any) -> None:
        """开启/关闭主动聊天"""
        try:
            args = getattr(ctx, "get_args", lambda: "")()
            args = args.strip() if isinstance(args, str) else ""

            if args in ["开", "on", "オン"]:
                self.proactive_chat_enabled = True
                await ctx.send(self._get_localized_text("proactive_on"))
            elif args in ["关", "off", "オフ"]:
                self.proactive_chat_enabled = False
                await ctx.send(self._get_localized_text("proactive_off"))
            else:
                status = "开启" if self.proactive_chat_enabled else "关闭"
                await ctx.send(f"当前主动聊天状态：{status}\n请输入：`主动聊天 开` 或 `主动聊天 关`")

        except Exception as e:
            logger.error(f"Error in cmd_proactive_chat: {e}", exc_info=True)

    @on_command("帮助")
    async def cmd_help(self, ctx: Any) -> None:
        """显示帮助信息"""
        try:
            prob = int(self.auto_shift_probability * 100)
            proactive = "ON" if self.proactive_chat_enabled else "OFF"
            await ctx.send(self._get_localized_text("help_text", prob=prob, proactive=proactive))
        except Exception as e:
            logger.error(f"Error in cmd_help: {e}", exc_info=True)

    @on_command("性能")
    async def cmd_performance(self, ctx: Any) -> None:
        """查看性能统计"""
        try:
            stats = self._perf_tracker.get_all_stats()
            if not stats:
                await ctx.send("*(歪头)* 还没有性能数据呢，再聊一会儿吧！")
                return
            
            lines = ["**性能统计** 📊"]
            for name, data in stats.items():
                lines.append(
                    f"\n{name}:\n"
                    f"  调用次数: {data['count']}\n"
                    f"  平均耗时: {data['avg']:.3f}s\n"
                    f"  最小耗时: {data['min']:.3f}s\n"
                    f"  最大耗时: {data['max']:.3f}s"
                )
            await ctx.send("\n".join(lines))
        except Exception as e:
            logger.error(f"Error in cmd_performance: {e}", exc_info=True)

    # ============================================================
    # 公共 API
    # ============================================================

    def record_interaction(
        self,
        user_message: str,
        bot_response: str,
        emotion_score: float = 0.0,
        keywords: Optional[List[str]] = None,
    ) -> None:
        """记录一次交互到情感记忆"""
        try:
            self._memory.add(
                user_message=user_message,
                bot_response=bot_response,
                form=self.current_emotion,  # 记录情绪状态而非形态
                emotion_score=emotion_score,
                keywords=keywords,
            )
        except Exception as e:
            logger.error(f"Error recording interaction: {e}", exc_info=True)

    def get_memory_summary(self) -> str:
        """获取记忆摘要"""
        return self._memory.get_memory_summary()

    def get_current_state_info(self) -> Dict[str, Any]:
        """获取当前状态信息"""
        state = self._emotion_manager.get_state(self.current_emotion)
        return {
            "emotion": self.current_emotion,
            "language": self.language,
            "emotion_tags": state.emotion_tags if state else [],
            "keywords": state.keywords if state else [],
            "proactive_chat": self.proactive_chat_enabled,
        }

    def get_performance_stats(self) -> Dict[str, Dict[str, float]]:
        """获取性能统计"""
        return self._perf_tracker.get_all_stats()
