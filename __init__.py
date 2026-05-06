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
- 记忆系统自动清理机制
"""

from .yoimiya_skill import YoimiyaSummerSoul

__all__ = ["YoimiyaSummerSoul"]
__version__ = "1.2.0"
