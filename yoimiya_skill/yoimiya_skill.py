"""Yoimiya Summer Soul Skill v1.2

宵宫·夏日灵魂觉醒（统一角色情绪状态系统）
功能：情感记忆系统、情绪状态系统、多语言支持、动态情绪切换、
      季节事件感知、互动小游戏（烟花/炸弹/回忆）、日记功能、
      主动聊天系统、JSON 配置化提示词、性能监控

v1.2 优化：
- 引入 ConfigManager 配置缓存，避免重复文件 I/O
- 本地化文本抽离至独立模块
- 性能追踪增强（慢操作告警、上下文记录）
- 自定义异常体系
"""

import json
import logging
import os
import random
from typing import Any, Dict, List, Optional

from .config_manager import ConfigManager
from .emotion_manager import EmotionManager
from .events import MinigameManager, SeasonalEventManager
from .localization import (
    get_emotion_shift_message,
    get_localized_text,
    get_proactive_messages,
)
from .memory import EmotionMemory
from .performance import PerformanceTracker

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


class YoimiyaSummerSoul(BaseSkill):
    """宵宫夏日灵魂 Skill 主类"""

    def __init__(self, config_path: Optional[str] = None):
        super().__init__()

        self._config_path = config_path or self._get_default_config_path()

        # 使用 ConfigManager 管理配置（带缓存）
        self._config_manager = ConfigManager(
            config_path=self._config_path,
            ttl=self._get_config_ttl(),
        )

        # 加载 skill 配置（合并 performance 和 monitoring）
        self._skill_config = self._config_manager.get_skill_config()

        # 配置日志
        log_level = getattr(
            logging, self._skill_config.get("log_level", "INFO"), logging.INFO
        )
        structured_logging = self._skill_config.get("structured_logging", False)
        setup_logging(level=log_level, structured=structured_logging)

        self.name: str = self._skill_config.get("name", "Yoimiya_Summer_Soul_Skill")
        self.description: str = self._skill_config.get(
            "description", "宵宫·夏日灵魂觉醒"
        )
        self.version: str = self._skill_config.get("version", "1.2.0")
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

        # 性能监控（增强版）
        perf_config = self._skill_config.get("performance", {})
        slow_threshold = perf_config.get("slow_threshold", 1.0)
        self._perf_tracker = PerformanceTracker(
            enabled=perf_config.get("performance_tracking", True),
            slow_threshold=slow_threshold,
        )

        # 初始化子系统
        self._emotion_manager = EmotionManager(self._config_path)
        self._memory = EmotionMemory(
            max_entries=self._skill_config.get("memory_max_entries", 50),
            storage_path=os.path.join(
                os.path.dirname(__file__), "data", "memory.json"
            ),
            auto_cleanup=self._skill_config.get("memory_auto_cleanup", True),
            cleanup_interval=self._skill_config.get(
                "memory_cleanup_interval", 86400
            ),
            max_age_days=self._skill_config.get("memory_max_age_days", 7),
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
        return os.path.join(os.path.dirname(__file__), "config.json")

    def _get_config_ttl(self) -> int:
        """从环境变量或配置获取缓存 TTL"""
        # 优先从环境变量获取
        env_ttl = os.environ.get("YOIMIYA_CONFIG_TTL")
        if env_ttl:
            try:
                return int(env_ttl)
            except ValueError:
                pass
        # 默认 1 小时
        return 3600

    # ============================================================
    # 辅助方法
    # ============================================================

    def _set_system_prompt(self, ctx: Any) -> None:
        """设置系统提示词（包含情绪状态注入）"""
        from .prompts import get_emotion_state_addition, get_system_prompt

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

        # 从 ConfigManager 获取情感关键词（带缓存）
        try:
            emotion_keywords = self._config_manager.get_emotion_keywords()
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

        messages = get_proactive_messages(self.language)
        return random.choice(messages)

    def _get_localized_text(self, key: str, **kwargs: Any) -> str:
        """获取本地化文本"""
        return get_localized_text(key, self.language, **kwargs)

    # ============================================================
    # 事件处理器
    # ============================================================

    @on_message()
    async def handle_message(self, ctx: Any) -> None:
        """处理普通消息：情绪检测、情感关键词、季节事件、记忆记录、主动聊天"""
        user_id = getattr(ctx, "user_id", "anonymous")
        with self._perf_tracker.track("handle_message", user_id=user_id):
            try:
                message = getattr(ctx, "message", "")

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
                    msg = get_emotion_shift_message(detected, self.language)
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
                await ctx.send(
                    f"当前主动聊天状态：{status}\n请输入：`主动聊天 开` 或 `主动聊天 关`"
                )

        except Exception as e:
            logger.error(f"Error in cmd_proactive_chat: {e}", exc_info=True)

    @on_command("帮助")
    async def cmd_help(self, ctx: Any) -> None:
        """显示帮助信息"""
        try:
            prob = int(self.auto_shift_probability * 100)
            proactive = "ON" if self.proactive_chat_enabled else "OFF"
            await ctx.send(
                self._get_localized_text("help_text", prob=prob, proactive=proactive)
            )
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
                    f"  最大耗时: {data['max']:.3f}s\n"
                    f"  P95 耗时: {data.get('p95', 0):.3f}s\n"
                    f"  慢操作数: {data.get('slow_count', 0)}"
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

    def get_performance_stats(self) -> Dict[str, Dict[str, Any]]:
        """获取性能统计"""
        return self._perf_tracker.get_all_stats()

    def reload_config(self) -> None:
        """强制重新加载配置"""
        self._config_manager.reload()
        logger.info("Config reloaded manually")
