"""情绪状态管理器

宵宫没有多个"形态"，而是根据对话内容自然切换情绪状态。
情绪状态会影响系统提示词的追加内容，让宵宫的表现更加自然。
"""

import json
import logging
import os
import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

from .prompts import (
    get_emotion_state_addition,
    get_emotion_state_keywords,
    get_emotion_state_name,
    get_all_emotion_states,
)

logger = logging.getLogger(__name__)


@dataclass
class EmotionState:
    """情绪状态"""
    name: str
    name_en: str
    name_ja: str
    keywords: List[str]
    emotion_tags: List[str]

    def get_localized_name(self, lang: str = "zh") -> str:
        if lang == "en":
            return self.name_en
        elif lang == "ja":
            return self.name_ja
        return self.name


class EmotionManager:
    """情绪状态管理器"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "config.json"
        )
        self._states: Dict[str, EmotionState] = {}
        self._load_config()

    def _load_config(self) -> None:
        """从配置文件加载情绪状态配置"""
        if not os.path.exists(self.config_path):
            logger.error(f"Config file not found: {self.config_path}")
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise

        states_config = config.get("emotion_states", {})

        for state_name, state_data in states_config.items():
            self._states[state_name] = EmotionState(
                name=state_name,
                name_en=state_data.get("name_en", state_name),
                name_ja=state_data.get("name_ja", state_name),
                keywords=state_data.get("keywords", []),
                emotion_tags=state_data.get("emotion_tags", []),
            )

        logger.info(f"Loaded {len(self._states)} emotion states")

    def get_all_states(self) -> List[str]:
        """获取所有情绪状态名称"""
        return list(self._states.keys())

    def get_state(self, name: str) -> Optional[EmotionState]:
        """获取指定情绪状态"""
        return self._states.get(name)

    def detect_emotion(self, message: str) -> Optional[str]:
        """基于消息内容检测情绪状态
        
        返回得分最高的情绪状态，如果没有匹配则返回 None
        """
        scores: Dict[str, int] = {}
        message_lower = message.lower()

        for state_name, state in self._states.items():
            score = 0
            for kw in state.keywords:
                if kw.lower() in message_lower:
                    score += 1
            if score > 0:
                scores[state_name] = score

        if not scores:
            return None

        best_state = max(scores, key=scores.get)
        logger.debug(f"Detected emotion '{best_state}' for message (score: {scores[best_state]})")
        return best_state

    def get_system_prompt_with_emotion(self, base_prompt: str, emotion: str, lang: str = "zh") -> str:
        """获取包含情绪状态追加内容的系统提示词"""
        if not emotion:
            return base_prompt

        addition = get_emotion_state_addition(emotion, lang)
        if addition:
            return f"{base_prompt}\n\n{addition}"
        return base_prompt

    def get_emotion_response(self, keyword: str, emotion_keywords: Dict[str, str]) -> Optional[str]:
        """获取情感关键词响应"""
        return emotion_keywords.get(keyword)

    def get_state_stats_display(self, state_name: str, lang: str = "zh") -> str:
        """获取情绪状态展示文本"""
        state = self.get_state(state_name)
        if not state:
            return ""

        localized_name = state.get_localized_name(lang)
        tags = ", ".join(state.emotion_tags)
        keywords = ", ".join(state.keywords[:5])

        return (
            f"**{localized_name}**\n"
            f"🏷️ 标签: {tags}\n"
            f"🔑 关键词: {keywords}..."
        )

    def get_random_state(self, exclude: Optional[str] = None) -> str:
        """随机获取一个情绪状态（可排除指定状态）"""
        states = self.get_all_states()
        if exclude and exclude in states:
            states = [s for s in states if s != exclude]
        return random.choice(states) if states else "元气"

    def reload(self) -> None:
        """重新加载配置"""
        self._states.clear()
        self._load_config()
