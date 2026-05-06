"""配置管理器 - 带缓存机制

解决每次处理消息都读取 config.json 的性能问题，
提供 TTL 缓存和强制重载功能。
"""

import json
import logging
import os
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ConfigManager:
    """带 TTL 缓存的配置管理器"""

    def __init__(self, config_path: Optional[str] = None, ttl: int = 3600):
        """
        Args:
            config_path: 配置文件路径，默认使用模块同级目录的 config.json
            ttl: 缓存有效期（秒），默认 1 小时
        """
        self.config_path = config_path or self._get_default_config_path()
        self.ttl = ttl
        self._cache: Optional[Dict[str, Any]] = None
        self._cache_time: float = 0.0
        self._file_mtime: float = 0.0

    @staticmethod
    def _get_default_config_path() -> str:
        return os.path.join(os.path.dirname(__file__), "config.json")

    def _load(self) -> Dict[str, Any]:
        """从文件加载配置"""
        if not os.path.exists(self.config_path):
            logger.error(f"Config file not found: {self.config_path}")
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            self._file_mtime = os.path.getmtime(self.config_path)
            logger.debug(f"Config loaded from {self.config_path}")
            return config
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise

    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效（未过期且文件未修改）"""
        if self._cache is None:
            return False

        now = time.time()
        if (now - self._cache_time) > self.ttl:
            return False

        try:
            current_mtime = os.path.getmtime(self.config_path)
            if current_mtime > self._file_mtime:
                return False
        except OSError:
            return False

        return True

    def get_config(self, force_reload: bool = False) -> Dict[str, Any]:
        """获取配置（带缓存）

        Args:
            force_reload: 强制重新加载，忽略缓存

        Returns:
            完整的配置字典
        """
        if force_reload or not self._is_cache_valid():
            self._cache = self._load()
            self._cache_time = time.time()
        return self._cache

    def get(self, key: str, default: Any = None, force_reload: bool = False) -> Any:
        """获取配置项

        Args:
            key: 配置键名，支持点号分隔的嵌套路径，如 "skill.name"
            default: 默认值
            force_reload: 强制重新加载

        Returns:
            配置值，如果找不到则返回 default
        """
        config = self.get_config(force_reload=force_reload)
        keys = key.split(".")
        value = config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def get_skill_config(self, force_reload: bool = False) -> Dict[str, Any]:
        """获取 skill 配置段（合并 performance 和 monitoring）"""
        config = self.get_config(force_reload=force_reload)
        skill_config = config.get("skill", {}).copy()
        skill_config.update(config.get("performance", {}))
        skill_config.update(config.get("monitoring", {}))
        return skill_config

    def get_emotion_keywords(self, force_reload: bool = False) -> Dict[str, str]:
        """获取情感关键词配置"""
        return self.get("emotion_keywords", {}, force_reload=force_reload)

    def get_seasonal_events(self, force_reload: bool = False) -> Dict[str, Any]:
        """获取季节事件配置"""
        return self.get("seasonal_events", {}, force_reload=force_reload)

    def get_minigames(self, force_reload: bool = False) -> Dict[str, Any]:
        """获取小游戏配置"""
        return self.get("minigames", {}, force_reload=force_reload)

    def get_emotion_states(self, force_reload: bool = False) -> Dict[str, Any]:
        """获取情绪状态配置"""
        return self.get("emotion_states", {}, force_reload=force_reload)

    def reload(self) -> None:
        """强制重新加载配置"""
        self._cache = None
        self._cache_time = 0
        self._file_mtime = 0
        logger.info("Config cache cleared, will reload on next access")


# 全局配置管理器实例（单例模式）
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_path: Optional[str] = None, ttl: int = 3600) -> ConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_path=config_path, ttl=ttl)
    return _config_manager
