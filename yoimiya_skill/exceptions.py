"""自定义异常模块

为 Yoimiya Skill 提供结构化的异常体系，
便于错误分类、处理和恢复。
"""


class YoimiyaSkillError(Exception):
    """Yoimiya Skill 基础异常类"""

    def __init__(self, message: str = "", *, code: str = "UNKNOWN"):
        self.code = code
        super().__init__(message)


class ConfigError(YoimiyaSkillError):
    """配置错误"""

    def __init__(self, message: str = ""):
        super().__init__(message, code="CONFIG_ERROR")


class ConfigNotFoundError(ConfigError):
    """配置文件未找到"""

    def __init__(self, path: str = ""):
        super().__init__(f"配置文件未找到: {path}", code="CONFIG_NOT_FOUND")


class ConfigParseError(ConfigError):
    """配置文件解析错误"""

    def __init__(self, path: str = "", detail: str = ""):
        super().__init__(f"配置文件解析失败 [{path}]: {detail}", code="CONFIG_PARSE_ERROR")


class MemoryError(YoimiyaSkillError):
    """记忆系统错误"""

    def __init__(self, message: str = ""):
        super().__init__(message, code="MEMORY_ERROR")


class MemoryStorageError(MemoryError):
    """记忆存储错误"""

    def __init__(self, path: str = "", detail: str = ""):
        super().__init__(f"记忆存储失败 [{path}]: {detail}", code="MEMORY_STORAGE_ERROR")


class EmotionError(YoimiyaSkillError):
    """情绪系统错误"""

    def __init__(self, message: str = ""):
        super().__init__(message, code="EMOTION_ERROR")


class PromptError(YoimiyaSkillError):
    """提示词系统错误"""

    def __init__(self, message: str = ""):
        super().__init__(message, code="PROMPT_ERROR")


class LocalizationError(YoimiyaSkillError):
    """本地化错误"""

    def __init__(self, message: str = "", lang: str = ""):
        self.lang = lang
        super().__init__(message, code="LOCALIZATION_ERROR")
