# Yoimiya Summer Soul API 文档

## 概述

本文档描述了 `YoimiyaSummerSoul` Skill 的公共 API 接口。

## 主类

### `YoimiyaSummerSoul`

```python
from yoimiya_skill import YoimiyaSummerSoul

skill = YoimiyaSummerSoul()
```

#### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | Skill 名称 |
| `description` | `str` | Skill 描述 |
| `version` | `str` | 版本号 |
| `current_form` | `str` | 当前形态（夏祭/琉金/幻梦） |
| `language` | `str` | 当前语言（zh/en/ja） |
| `auto_shift_probability` | `float` | 自动形态切换概率 |
| `proactive_chat_enabled` | `bool` | 主动聊天是否开启 |

#### 方法

##### `record_interaction(user_message, bot_response, emotion_score=0.0, keywords=None)`

记录一次交互到情感记忆系统。

```python
skill.record_interaction(
    user_message="你好宵宫",
    bot_response="你好呀旅行者！",
    emotion_score=0.8,
    keywords=["问候", "友好"]
)
```

##### `get_memory_summary()`

获取记忆摘要，用于注入系统提示词。

```python
summary = skill.get_memory_summary()
```

##### `get_current_form_info()`

获取当前形态的完整信息。

```python
info = skill.get_current_form_info()
# {
#     "form": "夏祭",
#     "language": "zh",
#     "stats": {"defense": 50, "hp": 80, ...},
#     "keywords": ["烟花", "祭典", ...],
#     "proactive_chat": True
# }
```

## 命令接口

Skill 支持以下命令：

| 命令 | 说明 | 示例 |
|------|------|------|
| `切换形态 <形态>` | 手动切换形态 | `切换形态 琉金` |
| `形态属性` | 查看当前形态属性 | `形态属性` |
| `语言 <语言>` | 切换语言 | `语言 en` |
| `日记` | 生成对话日记 | `日记` |
| `清空记忆` | 清空情感记忆 | `清空记忆` |
| `小游戏 <游戏>` | 玩互动小游戏 | `小游戏 烟花` |
| `主动聊天 <开/关>` | 开启/关闭主动聊天 | `主动聊天 关` |
| `帮助` | 显示帮助信息 | `帮助` |

## 子系统

### 形态管理器 (`FormManager`)

```python
from yoimiya_skill.form_manager import FormManager

manager = FormManager()

# 获取所有形态
forms = manager.get_all_forms()  # ["夏祭", "琉金", "幻梦"]

# 获取形态策略
strategy = manager.get_form("夏祭")
prompt = strategy.get_system_prompt("zh")

# 智能推荐形态
suggested = manager.suggest_form("我想看烟花")
```

### 情感记忆 (`EmotionMemory`)

```python
from yoimiya_skill.memory import EmotionMemory

memory = EmotionMemory(max_entries=50)

# 添加记忆
memory.add("你好", "你好呀！", "夏祭", 0.5)

# 获取最近记忆
recent = memory.get_recent(5)

# 获取相关记忆
relevant = memory.get_relevant_memories("烟花", top_k=3)

# 生成日记
diary = memory.generate_diary()
```

### 事件管理器 (`SeasonalEventManager`)

```python
from yoimiya_skill.events import SeasonalEventManager

manager = SeasonalEventManager()

# 获取今天的事件消息
msg = manager.get_event_message("zh")
```

### 小游戏管理器 (`MinigameManager`)

```python
from yoimiya_skill.events import MinigameManager

manager = MinigameManager()

# 烟花小游戏
result = manager.play_fireworks_game("zh")

# 炸弹小游戏
result = manager.play_bomb_game("zh")

# 回忆小游戏
result = manager.play_memory_game("zh")
```

## 配置文件

### `config.json`

包含 Skill 配置、形态属性、情感关键词、季节事件和小游戏配置。

### `prompts.json`

包含所有系统提示词、变身台词和切换回复，支持 zh/en/ja 三种语言。

## 设计模式

- **策略模式**：`FormStrategy` 定义形态接口，`BaseFormStrategy` 实现通用逻辑，各形态继承实现
- **工厂模式**：`FormManager._FORM_STRATEGIES` 映射形态名到策略类
- **单例模式**：`PromptLoader` 确保提示词只加载一次，支持热重载
