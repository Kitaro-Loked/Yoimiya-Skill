"""宵宫角色提示词加载器

所有提示词文本已从硬编码迁移至 prompts.json，支持热重载和多语言扩展。
"""

import json
import logging
import os
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PromptLoader:
    """提示词加载器：从 JSON 文件加载所有提示词，支持热重载"""

    _instance: Optional["PromptLoader"] = None
    _prompts_data: Optional[Dict] = None
    _file_path: Optional[str] = None
    _last_modified: float = 0.0

    def __new__(cls, file_path: Optional[str] = None) -> "PromptLoader":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, file_path: Optional[str] = None):
        if file_path is not None:
            self._file_path = file_path
        elif self._file_path is None:
            self._file_path = os.path.join(
                os.path.dirname(__file__), "prompts.json"
            )

    def _load(self) -> Dict:
        """从 JSON 文件加载提示词"""
        if not os.path.exists(self._file_path):
            logger.error(f"Prompts file not found: {self._file_path}")
            raise FileNotFoundError(f"Prompts file not found: {self._file_path}")

        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._last_modified = os.path.getmtime(self._file_path)
            logger.info(f"Loaded prompts from {self._file_path}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in prompts file: {e}")
            raise

    def _check_reload(self) -> None:
        """检查文件是否被修改，如果是则重新加载"""
        if self._prompts_data is None:
            self._prompts_data = self._load()
            return

        try:
            current_mtime = os.path.getmtime(self._file_path)
            if current_mtime > self._last_modified:
                logger.info("Prompts file changed, reloading...")
                self._prompts_data = self._load()
        except OSError:
            pass

    @property
    def data(self) -> Dict:
        """获取提示词数据（自动检查热重载）"""
        self._check_reload()
        if self._prompts_data is None:
            self._prompts_data = self._load()
        return self._prompts_data

    def get_system_prompt(self, lang: str = "zh") -> str:
        """获取统一角色系统提示词"""
        return self.data.get("system_prompts", {}).get(lang, "")

    def get_emotion_state_addition(self, state: str, lang: str = "zh") -> str:
        """获取情绪状态追加提示词"""
        states = self.data.get("emotion_states", {})
        state_data = states.get(state)
        if state_data is None:
            return ""
        return state_data.get("system_prompt_addition", {}).get(lang, "")

    def get_emotion_state_keywords(self, state: str) -> List[str]:
        """获取情绪状态触发关键词"""
        states = self.data.get("emotion_states", {})
        state_data = states.get(state)
        if state_data is None:
            return []
        return state_data.get("trigger_keywords", [])

    def get_emotion_state_name(self, state: str, lang: str = "zh") -> str:
        """获取情绪状态显示名称"""
        states = self.data.get("emotion_states", {})
        state_data = states.get(state)
        if state_data is None:
            return state
        return state_data.get("name", {}).get(lang, state)

    def get_all_emotion_states(self) -> List[str]:
        """获取所有情绪状态名称"""
        return list(self.data.get("emotion_states", {}).keys())

    def get_common_message(self, key: str, lang: str = "zh") -> str:
        """获取通用消息"""
        common = self.data.get("common", {})
        return common.get(key, {}).get(lang, "")

    def get_supported_languages(self) -> List[str]:
        """获取支持的语言列表"""
        meta = self.data.get("meta", {})
        return meta.get("supported_languages", ["zh"])

    def get_character_name(self, lang: str = "zh") -> str:
        """获取角色名称"""
        character = self.data.get("character", {})
        return character.get("name", {}).get(lang, "宵宫")

    def reload(self) -> None:
        """强制重新加载提示词"""
        self._prompts_data = self._load()
        logger.info("Prompts reloaded manually")


# 全局加载器实例
_prompt_loader: Optional[PromptLoader] = None


def get_loader() -> PromptLoader:
    """获取全局提示词加载器实例"""
    global _prompt_loader
    if _prompt_loader is None:
        _prompt_loader = PromptLoader()
    return _prompt_loader


def get_system_prompt(lang: str = "zh") -> str:
    """获取统一角色系统提示词"""
    return get_loader().get_system_prompt(lang)


def get_emotion_state_addition(state: str, lang: str = "zh") -> str:
    """获取情绪状态追加提示词"""
    return get_loader().get_emotion_state_addition(state, lang)


def get_emotion_state_keywords(state: str) -> List[str]:
    """获取情绪状态触发关键词"""
    return get_loader().get_emotion_state_keywords(state)


def get_emotion_state_name(state: str, lang: str = "zh") -> str:
    """获取情绪状态显示名称"""
    return get_loader().get_emotion_state_name(state, lang)


def get_all_emotion_states() -> List[str]:
    """获取所有情绪状态名称"""
    return get_loader().get_all_emotion_states()


def get_common_message(key: str, lang: str = "zh") -> str:
    """获取通用消息"""
    return get_loader().get_common_message(key, lang)


def get_supported_languages() -> List[str]:
    """获取所有支持的语言"""
    return get_loader().get_supported_languages()


def get_character_name(lang: str = "zh") -> str:
    """获取角色名称"""
    return get_loader().get_character_name(lang)


def reload_prompts() -> None:
    """强制重新加载所有提示词"""
    get_loader().reload()
