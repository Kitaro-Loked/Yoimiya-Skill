"""形态管理器：使用策略模式管理多个形态"""

import json
import logging
import os
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Callable

from .prompts import get_form_prompt, get_shift_message, get_switch_reply

logger = logging.getLogger(__name__)


@dataclass
class FormStats:
    """形态属性"""
    defense: int
    hp: int
    speed: int
    attack: int
    crit_rate: int

    def to_dict(self) -> Dict[str, int]:
        return {
            "defense": self.defense,
            "hp": self.hp,
            "speed": self.speed,
            "attack": self.attack,
            "crit_rate": self.crit_rate,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> "FormStats":
        return cls(**data)


@dataclass
class FormConfig:
    """形态配置"""
    name: str
    name_en: str
    name_ja: str
    path: str
    element: str
    stats: FormStats
    keywords: List[str]
    emotion_tags: List[str]

    def get_localized_name(self, lang: str = "zh") -> str:
        if lang == "en":
            return self.name_en
        elif lang == "ja":
            return self.name_ja
        return self.name

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "name_en": self.name_en,
            "name_ja": self.name_ja,
            "path": self.path,
            "element": self.element,
            "stats": self.stats.to_dict(),
            "keywords": self.keywords,
            "emotion_tags": self.emotion_tags,
        }


class FormStrategy(ABC):
    """形态策略基类"""

    @abstractmethod
    def get_system_prompt(self, lang: str = "zh") -> str:
        """获取系统提示词"""
        pass

    @abstractmethod
    def get_shift_message(self) -> str:
        """获取变身台词"""
        pass

    @abstractmethod
    def get_switch_reply(self) -> str:
        """获取切换回复"""
        pass

    @abstractmethod
    def get_emotion_response(self, keyword: str) -> Optional[str]:
        """获取情感关键词响应"""
        pass

    @abstractmethod
    def get_stats(self) -> FormStats:
        """获取形态属性"""
        pass


class BaseFormStrategy(FormStrategy):
    """基础形态策略"""

    def __init__(
        self,
        form_name: str,
        config: FormConfig,
        emotion_keywords: Dict[str, str],
        shift_message: str,
        switch_reply: str,
    ):
        self.form_name = form_name
        self.config = config
        self._emotion_keywords = emotion_keywords
        self._shift_message = shift_message
        self._switch_reply = switch_reply

    def get_system_prompt(self, lang: str = "zh") -> str:
        return get_form_prompt(self.form_name, lang)

    def get_shift_message(self) -> str:
        return self._shift_message

    def get_switch_reply(self) -> str:
        return self._switch_reply

    def get_emotion_response(self, keyword: str) -> Optional[str]:
        return self._emotion_keywords.get(keyword)

    def get_stats(self) -> FormStats:
        return self.config.stats

    def check_keywords(self, message: str) -> int:
        """检查消息中包含的形态关键词数量，用于动态切换"""
        count = 0
        message_lower = message.lower()
        for kw in self.config.keywords:
            if kw.lower() in message_lower:
                count += 1
        return count


class FireworksForm(BaseFormStrategy):
    """夏祭女王形态策略"""

    def __init__(self, config: FormConfig, emotion_keywords: Dict[str, str]):
        super().__init__(
            form_name="夏祭",
            config=config,
            emotion_keywords=emotion_keywords,
            shift_message=get_shift_message("夏祭", "zh"),
            switch_reply=get_switch_reply("夏祭", "zh"),
        )


class BattleForm(BaseFormStrategy):
    """琉金火舞形态策略"""

    def __init__(self, config: FormConfig, emotion_keywords: Dict[str, str]):
        super().__init__(
            form_name="琉金",
            config=config,
            emotion_keywords=emotion_keywords,
            shift_message=get_shift_message("琉金", "zh"),
            switch_reply=get_switch_reply("琉金", "zh"),
        )


class DreamForm(BaseFormStrategy):
    """流星幻梦形态策略"""

    def __init__(self, config: FormConfig, emotion_keywords: Dict[str, str]):
        super().__init__(
            form_name="幻梦",
            config=config,
            emotion_keywords=emotion_keywords,
            shift_message=get_shift_message("幻梦", "zh"),
            switch_reply=get_switch_reply("幻梦", "zh"),
        )


class FormManager:
    """形态管理器：策略模式 + 工厂模式"""

    # 形态策略工厂映射
    _FORM_STRATEGIES: Dict[str, Callable[[FormConfig, Dict[str, str]], FormStrategy]] = {
        "夏祭": FireworksForm,
        "琉金": BattleForm,
        "幻梦": DreamForm,
    }

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "config.json"
        )
        self._forms: Dict[str, FormStrategy] = {}
        self._configs: Dict[str, FormConfig] = {}
        self._load_config()

    def _load_config(self) -> None:
        """从配置文件加载形态配置"""
        if not os.path.exists(self.config_path):
            logger.error(f"Config file not found: {self.config_path}")
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise

        forms_config = config.get("forms", {})
        emotion_keywords = config.get("emotion_keywords", {})

        for form_name, form_data in forms_config.items():
            stats = FormStats.from_dict(form_data.get("stats", {}))
            form_config = FormConfig(
                name=form_name,
                name_en=form_data.get("name_en", form_name),
                name_ja=form_data.get("name_ja", form_name),
                path=form_data.get("path", ""),
                element=form_data.get("element", ""),
                stats=stats,
                keywords=form_data.get("keywords", []),
                emotion_tags=form_data.get("emotion_tags", []),
            )
            self._configs[form_name] = form_config

            # 创建策略实例
            strategy_class = self._FORM_STRATEGIES.get(form_name)
            if strategy_class:
                self._forms[form_name] = strategy_class(
                    form_config, emotion_keywords.get(form_name, {})
                )
            else:
                logger.warning(f"Unknown form: {form_name}")

        logger.info(f"Loaded {len(self._forms)} form strategies")

    def get_form(self, name: str) -> Optional[FormStrategy]:
        """获取指定形态的策略"""
        return self._forms.get(name)

    def get_all_forms(self) -> List[str]:
        """获取所有形态名称"""
        return list(self._forms.keys())

    def get_config(self, name: str) -> Optional[FormConfig]:
        """获取形态配置"""
        return self._configs.get(name)

    def get_random_form(self, exclude: Optional[str] = None) -> str:
        """随机获取一个形态（可排除指定形态）"""
        forms = self.get_all_forms()
        if exclude and exclude in forms:
            forms = [f for f in forms if f != exclude]
        return random.choice(forms) if forms else "夏祭"

    def suggest_form(self, message: str) -> Optional[str]:
        """基于消息内容智能推荐形态"""
        scores: Dict[str, int] = {}
        for name, strategy in self._forms.items():
            if isinstance(strategy, BaseFormStrategy):
                scores[name] = strategy.check_keywords(message)

        if not scores or max(scores.values()) == 0:
            return None

        best_form = max(scores, key=scores.get)
        logger.debug(f"Suggested form '{best_form}' for message (score: {scores[best_form]})")
        return best_form

    def get_form_stats_display(self, form_name: str, lang: str = "zh") -> str:
        """获取形态属性展示文本"""
        config = self.get_config(form_name)
        if not config:
            return ""

        localized_name = config.get_localized_name(lang)
        stats = config.stats
        return (
            f"**{localized_name}** ({config.path} · {config.element})\n"
            f"🛡️ 防御: {stats.defense} | ❤️ 生命: {stats.hp}\n"
            f"⚡ 速度: {stats.speed} | ⚔️ 攻击: {stats.attack}\n"
            f"🎯 暴击: {stats.crit_rate}%"
        )

    def reload(self) -> None:
        """重新加载配置"""
        self._forms.clear()
        self._configs.clear()
        self._load_config()
