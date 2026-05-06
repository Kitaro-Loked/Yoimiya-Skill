"""宵宫各形态的系统提示词模板加载器

所有提示词文本已从硬编码迁移至 prompts.json，支持热重载和多语言扩展。
"""

import json
import logging
import os
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PromptTemplate:
    """提示词模板类，支持多语言渲染"""

    def __init__(self, templates: Dict[str, str]):
        self._templates = templates

    def render(self, lang: str = "zh") -> str:
        """根据语言渲染提示词"""
        return self._templates.get(lang, self._templates.get("zh", ""))

    def get_supported_languages(self) -> list[str]:
        """获取支持的语言列表"""
        return list(self._templates.keys())


class PromptLoader:
    """提示词加载器：从 JSON 文件加载所有提示词"""

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

    def get_form_prompt(self, form_name: str, lang: str = "zh") -> str:
        """获取指定形态和语言的系统提示词"""
        forms = self.data.get("forms", {})
        form_data = forms.get(form_name)
        if form_data is None:
            logger.warning(f"Form '{form_name}' not found in prompts")
            return ""
        return form_data.get("system_prompts", {}).get(lang, "")

    def get_shift_message(self, form_name: str, lang: str = "zh") -> str:
        """获取指定形态的变身台词"""
        forms = self.data.get("forms", {})
        form_data = forms.get(form_name)
        if form_data is None:
            return ""
        return form_data.get("shift_message", {}).get(lang, "")

    def get_switch_reply(self, form_name: str, lang: str = "zh") -> str:
        """获取指定形态的切换回复"""
        forms = self.data.get("forms", {})
        form_data = forms.get(form_name)
        if form_data is None:
            return ""
        return form_data.get("switch_reply", {}).get(lang, "")

    def get_common_message(self, key: str, lang: str = "zh") -> str:
        """获取通用消息"""
        common = self.data.get("common", {})
        return common.get(key, {}).get(lang, "")

    def get_supported_languages(self) -> List[str]:
        """获取支持的语言列表"""
        meta = self.data.get("meta", {})
        return meta.get("supported_languages", ["zh"])

    def get_form_names(self) -> List[str]:
        """获取所有形态名称"""
        return list(self.data.get("forms", {}).keys())

    def get_form_display_name(self, form_name: str, lang: str = "zh") -> str:
        """获取形态的显示名称"""
        forms = self.data.get("forms", {})
        form_data = forms.get(form_name)
        if form_data is None:
            return form_name
        return form_data.get("name", {}).get(lang, form_name)

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


def get_form_prompt(form_name: str, lang: str = "zh") -> str:
    """获取指定形态和语言的系统提示词"""
    return get_loader().get_form_prompt(form_name, lang)


def get_shift_message(form_name: str, lang: str = "zh") -> str:
    """获取指定形态的变身台词"""
    return get_loader().get_shift_message(form_name, lang)


def get_switch_reply(form_name: str, lang: str = "zh") -> str:
    """获取指定形态的切换回复"""
    return get_loader().get_switch_reply(form_name, lang)


def get_common_message(key: str, lang: str = "zh") -> str:
    """获取通用消息"""
    return get_loader().get_common_message(key, lang)


def get_supported_languages() -> List[str]:
    """获取所有支持的语言"""
    return get_loader().get_supported_languages()


def get_form_display_name(form_name: str, lang: str = "zh") -> str:
    """获取形态的显示名称"""
    return get_loader().get_form_display_name(form_name, lang)


def reload_prompts() -> None:
    """强制重新加载所有提示词"""
    get_loader().reload()
