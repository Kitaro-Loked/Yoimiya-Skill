"""Yoimiya Summer Soul Skill v1.0

宵宫·夏日灵魂觉醒（究极情感沉浸版）
功能：情感记忆系统、形态属性系统、多语言支持、动态形态切换、
      季节事件感知、互动小游戏（烟花/炸弹/回忆）、日记功能、
      主动聊天系统、JSON 配置化提示词
"""

import json
import logging
import os
import random
from typing import Any, Dict, List, Optional

from .form_manager import FormManager, FormStrategy
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


def setup_logging(level: int = logging.INFO) -> None:
    """配置日志系统"""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


class YoimiyaSummerSoul(BaseSkill):
    """宵宫夏日灵魂 Skill 主类"""

    def __init__(self, config_path: Optional[str] = None):
        super().__init__()
        setup_logging()

        self._config_path = config_path or self._get_default_config_path()
        self._load_skill_config()

        self.name: str = self._skill_config.get("name", "Yoimiya_Summer_Soul_Skill")
        self.description: str = self._skill_config.get(
            "description", "宵宫·夏日灵魂觉醒"
        )
        self.version: str = self._skill_config.get("version", "1.0.0")
        self.current_form: str = self._skill_config.get("default_form", "夏祭")
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

        # 初始化子系统
        self._form_manager = FormManager(self._config_path)
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
            f"Default form: {self.current_form}, Language: {self.language}, "
            f"Proactive chat: {self.proactive_chat_enabled}"
        )

    def _get_default_config_path(self) -> str:
        """获取默认配置文件路径"""
        return os.path.join(os.path.dirname(__file__), "config.json")

    def _load_skill_config(self) -> None:
        """加载 Skill 配置"""
        if not os.path.exists(self._config_path):
            logger.error(f"Config file not found: {self._config_path}")
            raise FileNotFoundError(f"Config file not found: {self._config_path}")

        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            self._skill_config = config.get("skill", {})
            logger.debug("Skill config loaded successfully")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise

    # ============================================================
    # 辅助方法
    # ============================================================

    def _get_current_strategy(self) -> Optional[FormStrategy]:
        """获取当前形态的策略"""
        return self._form_manager.get_form(self.current_form)

    def _set_system_prompt(self, ctx: Any) -> None:
        """设置系统提示词（包含记忆注入）"""
        strategy = self._get_current_strategy()
        if strategy is None:
            logger.warning(f"Unknown form: {self.current_form}")
            return

        prompt = strategy.get_system_prompt(self.language)

        # 注入情感记忆
        memory_summary = self._memory.get_memory_summary()
        if memory_summary:
            prompt = f"{prompt}\n\n{memory_summary}"

        ctx.set_system_prompt(prompt)

    def _check_emotion_keywords(self, message: str) -> Optional[str]:
        """检查情感关键词并返回反射式回应"""
        if not self.emotion_keywords_enabled:
            return None

        strategy = self._get_current_strategy()
        if strategy is None:
            return None

        # 检查形态专属关键词
        for keyword in strategy.config.keywords:
            if keyword.lower() in message.lower():
                response = strategy.get_emotion_response(keyword)
                if response:
                    return response

        return None

    def _check_seasonal_event(self) -> Optional[str]:
        """检查季节性事件"""
        if not self.seasonal_events_enabled:
            return None
        return self._event_manager.get_event_message(self.language)

    def _suggest_form_switch(self, message: str) -> Optional[str]:
        """基于对话内容智能推荐形态切换"""
        suggested = self._form_manager.suggest_form(message)
        if suggested and suggested != self.current_form:
            return suggested
        return None

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
                "unknown_form": "欸？'{form}'是什么形态呀，我没听说过呢~\n请输入：切换形态 夏祭 / 琉金 / 幻梦",
                "switch_hint": "欸？你想切换到什么形态呀？请输入：\n`切换形态 夏祭` / `切换形态 琉金` / `切换形态 幻梦`",
                "current_form": "当前形态：{form}",
                "stats_title": "📊 形态属性",
                "memory_cleared": "*(歪头)* 嗯……之前的记忆？好像被一阵风吹走了呢！不过没关系，我们可以创造新的回忆！🎆",
                "diary_not_ready": "*(翻着手账)* 唔……对话还不够多呢，再聊一会儿再写手账吧！",
                "language_changed": "语言已切换为：{lang}",
                "unknown_language": "不支持的语言：{lang}。支持：zh / en / ja",
                "game_list": "🎮 可用小游戏：\n",
                "unknown_game": "不知道这个游戏呢……可用游戏：\n",
                "proactive_on": "主动聊天已开启！我会时不时找你聊天哦~",
                "proactive_off": "主动聊天已关闭。我会安静等你找我啦。",
                "help_text": (
                    "**宵宫·夏日灵魂觉醒 v1.0** 🎆\n\n"
                    "📋 指令列表：\n"
                    "- `切换形态 <形态名>` - 手动切换形态\n"
                    "- `形态属性` - 查看当前形态属性\n"
                    "- `语言 <zh/en/ja>` - 切换语言\n"
                    "- `日记` - 查看对话总结\n"
                    "- `清空记忆` - 清空情感记忆\n"
                    "- `小游戏 <游戏名>` - 玩互动小游戏\n"
                    "- `主动聊天 <开/关>` - 开启/关闭主动聊天\n"
                    "- `帮助` - 显示此帮助信息\n\n"
                    "🎭 形态：夏祭 / 琉金 / 幻梦\n"
                    "💫 对话中有 {prob}% 概率自动变身\n"
                    "💬 主动聊天：{proactive}"
                ),
            },
            "en": {
                "unknown_form": "Huh? I've never heard of the '{form}' form~\nPlease use: switch form Summer Festival / Amber Blaze / Stardust Dream",
                "switch_hint": "Huh? Which form do you want to switch to? Please use:\n`switch form Summer Festival` / `switch form Amber Blaze` / `switch form Stardust Dream`",
                "current_form": "Current form: {form}",
                "stats_title": "📊 Form Stats",
                "memory_cleared": "*(tilts head)* Hmm... previous memories? Seems like they were blown away by the wind! But it's okay, we can create new ones! 🎆",
                "diary_not_ready": "*(flipping through diary)* Mmm... not enough conversations yet, let's chat a bit more before writing the diary!",
                "language_changed": "Language changed to: {lang}",
                "unknown_language": "Unsupported language: {lang}. Supported: zh / en / ja",
                "game_list": "🎮 Available minigames:\n",
                "unknown_game": "I don't know that game... Available games:\n",
                "proactive_on": "Proactive chat is on! I'll chat with you from time to time~",
                "proactive_off": "Proactive chat is off. I'll wait quietly for you to find me.",
                "help_text": (
                    "**Yoimiya: Summer Soul Awakening v1.0** 🎆\n\n"
                    "📋 Command List:\n"
                    "- `switch form <form>` - Manually switch forms\n"
                    "- `form stats` - View current form stats\n"
                    "- `language <zh/en/ja>` - Switch language\n"
                    "- `diary` - View conversation summary\n"
                    "- `clear memory` - Clear emotional memory\n"
                    "- `minigame <name>` - Play interactive minigames\n"
                    "- `proactive chat <on/off>` - Enable/disable proactive chat\n"
                    "- `help` - Show this help\n\n"
                    "🎭 Forms: Summer Festival / Amber Blaze / Stardust Dream\n"
                    "💫 {prob}% chance of auto transformation during conversation\n"
                    "💬 Proactive chat: {proactive}"
                ),
            },
            "ja": {
                "unknown_form": "え？「{form}」って何の形態？聞いたことないよ~\n入力してね：形態切替 夏祭り / 琉金 / 幻夢",
                "switch_hint": "え？どの形態に切り替えたいの？入力してね：\n`形態切替 夏祭り` / `形態切替 琉金` / `形態切替 幻夢`",
                "current_form": "現在の形態：{form}",
                "stats_title": "📊 形態ステータス",
                "memory_cleared": "*(首をかしげる)* うーん……前の記憶？風に吹き飛ばされちゃったみたい！でも大丈夫、新しい思い出を作ろう！🎆",
                "diary_not_ready": "*(手帳をめくる)* うーん……まだ会話が足りないね、もう少しおしゃべりしてから日記を書こう！",
                "language_changed": "言語を変更しました：{lang}",
                "unknown_language": "未対応の言語：{lang}。対応：zh / en / ja",
                "game_list": "🎮 利用可能なミニゲーム：\n",
                "unknown_game": "そのゲームは知らないな……利用可能なゲーム：\n",
                "proactive_on": "主动チャットがオンになったよ！時々話しかけるね~",
                "proactive_off": "主动チャットがオフになったよ。静かに待ってるね。",
                "help_text": (
                    "**宵宮·夏の魂の覚醒 v1.0** 🎆\n\n"
                    "📋 コマンド一覧：\n"
                    "- `形態切替 <形態名>` - 手動で形態を切り替え\n"
                    "- `形態ステータス` - 現在の形態ステータスを確認\n"
                    "- `言語 <zh/en/ja>` - 言語を切り替え\n"
                    "- `日記` - 会話のまとめを見る\n"
                    "- `記憶消去` - 感情記憶を消去\n"
                    "- `ミニゲーム <名前>` - インタラクティブなミニゲームを遊ぶ\n"
                    "- `主动チャット <オン/オフ>` - 主动チャットのオン/オフ\n"
                    "- `ヘルプ` - このヘルプを表示\n\n"
                    "🎭 形態：夏祭り / 琉金 / 幻夢\n"
                    "💫 会話中に {prob}% の確率で自動変身\n"
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
        """处理普通消息：自动形态切换、情感关键词、季节事件、记忆记录、主动聊天"""
        try:
            message = getattr(ctx, "message", "")
            user_id = getattr(ctx, "user_id", "anonymous")

            # 检查季节事件（首次对话时）
            if self._message_count == 0:
                event_msg = self._check_seasonal_event()
                if event_msg:
                    await ctx.send(event_msg)

            self._message_count += 1

            # 动态形态切换（基于内容）
            suggested = self._suggest_form_switch(message)
            if suggested and suggested != self.current_form:
                old_form = self.current_form
                self.current_form = suggested
                strategy = self._get_current_strategy()
                if strategy:
                    logger.info(f"Dynamic shift: {old_form} -> {suggested}")
                    await ctx.send(
                        f"*(感受到你的话语中蕴含着{suggested}的气息……)*\n"
                        f"{strategy.get_shift_message()}"
                    )

            # 自动随机形态切换
            elif random.random() < self.auto_shift_probability:
                forms = self._form_manager.get_all_forms()
                old_form = self.current_form
                new_form = random.choice([f for f in forms if f != old_form])
                self.current_form = new_form
                strategy = self._get_current_strategy()
                if strategy:
                    logger.info(f"Auto shift: {old_form} -> {new_form}")
                    await ctx.send(strategy.get_shift_message())

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
            ctx._yoimiya_form = self.current_form
            ctx._yoimiya_memory = self._memory

            # 检查是否需要生成日记
            if self._message_count > 0 and self._message_count % self._diary_interval == 0:
                diary = self._memory.generate_diary()
                await ctx.send(f"\n\n*{diary}*")

        except Exception as e:
            logger.error(f"Error in handle_message: {e}", exc_info=True)
            await ctx.send("*(揉了揉眼睛)* 哎呀……刚才好像走神了，能再说一遍吗？")

    @on_command("切换形态")
    async def cmd_switch_form(self, ctx: Any) -> None:
        """手动切换形态"""
        try:
            args = getattr(ctx, "get_args", lambda: "")()
            args = args.strip() if isinstance(args, str) else ""

            if not args:
                await ctx.send(self._get_localized_text("switch_hint"))
                return

            if args in self._form_manager.get_all_forms():
                old_form = self.current_form
                self.current_form = args
                strategy = self._get_current_strategy()
                if strategy:
                    logger.info(f"Manual switch: {old_form} -> {args}")
                    await ctx.send(strategy.get_switch_reply())
                    ctx.set_system_prompt(strategy.get_system_prompt(self.language))
            else:
                await ctx.send(self._get_localized_text("unknown_form", form=args))

        except Exception as e:
            logger.error(f"Error in cmd_switch_form: {e}", exc_info=True)
            await ctx.send("*(困惑地挠头)* 切换的时候出了点小问题……再试一次？")

    @on_command("形态属性")
    async def cmd_form_stats(self, ctx: Any) -> None:
        """查看当前形态属性"""
        try:
            stats_display = self._form_manager.get_form_stats_display(
                self.current_form, self.language
            )
            await ctx.send(f"{self._get_localized_text('stats_title')}\n{stats_display}")
        except Exception as e:
            logger.error(f"Error in cmd_form_stats: {e}", exc_info=True)

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
                form=self.current_form,
                emotion_score=emotion_score,
                keywords=keywords,
            )
        except Exception as e:
            logger.error(f"Error recording interaction: {e}", exc_info=True)

    def get_memory_summary(self) -> str:
        """获取记忆摘要"""
        return self._memory.get_memory_summary()

    def get_current_form_info(self) -> Dict[str, Any]:
        """获取当前形态信息"""
        strategy = self._get_current_strategy()
        config = self._form_manager.get_config(self.current_form)
        return {
            "form": self.current_form,
            "language": self.language,
            "stats": config.stats.to_dict() if config else {},
            "keywords": config.keywords if config else [],
            "proactive_chat": self.proactive_chat_enabled,
        }
