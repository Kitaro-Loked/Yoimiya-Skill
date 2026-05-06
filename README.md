# Yoimiya-Skill 🎆 v1.1

![宵宫夏日灵魂](yoimiya_banner.jpg)

> 宵宫·夏日灵魂觉醒（统一角色情绪状态系统）：元气 / 热血 / 温柔

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/Kitaro-Loked/Yoimiya-Skill/actions/workflows/ci.yml/badge.svg)](https://github.com/Kitaro-Loked/Yoimiya-Skill/actions)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

## ✨ 简介

这是一个为 [OpenClaw](https://github.com/openclaw) 框架设计的 Skill，让你的 AI 助手化身《原神》中的宵宫！

**v1.1 重大更新**：从"多形态变身"重构为"统一角色情绪状态系统"——宵宫不再像三月七那样有多个"形态"，而是作为一个完整的角色，根据对话内容自然流动情绪（元气/热血/温柔）。这更符合宵宫的角色设定！

| 情绪状态 | 触发场景 | 表现 |
|----------|----------|------|
| 🎆 **元气** | 聊到烟花、祭典、孩子、笑容 | 更加活泼热情，充满夏日祭典的欢快 |
| 🔥 **热血** | 聊到战斗、保护、勇气 | 更加飒爽干练，展现守护者的决心 |
| 🌟 **温柔** | 聊到回忆、星空、梦想 | 更加温柔深情，带着哲思和诗意 |

## 🚀 安装

### 方式一：通过 OpenClaw 安装（推荐）

```bash
openclaw skill install https://github.com/Kitaro-Loked/Yoimiya-Skill
```

### 方式二：手动安装

```bash
git clone https://github.com/Kitaro-Loked/Yoimiya-Skill.git
cd Yoimiya-Skill
pip install -r requirements.txt
```

然后将 `yoimiya_skill/` 目录复制到你的 OpenClaw skills 目录中。

## 📖 使用方法

### 情绪状态流动

宵宫的情绪会根据对话内容**自然流动**，不需要手动切换：
- 提到「烟花、祭典、孩子、笑容」→ 宵宫变得更加**元气活泼**
- 提到「战斗、保护、勇气」→ 宵宫变得更加**飒爽热血**
- 提到「回忆、星空、梦想」→ 宵宫变得更加**温柔深情**

**15%** 的概率会自然情绪波动，宵宫会发送情绪变化的提示！

### 查看当前情绪

```
情绪
```

显示当前情绪状态和相关信息：
```
当前情绪：元气
**元气** 
🏷️ 标签: 元气, 活泼, 热情, 开朗
🔑 关键词: 烟花, 祭典, 夏天, 孩子, 笑容...
```

### 查看宵宫属性

```
属性
```

显示宵宫的角色属性面板：
```
📊 宵宫属性
**宵宫** (长野原烟花店店主 · 火)
🛡️ 防御: 60 | ❤️ 生命: 80
⚡ 速度: 85 | ⚔️ 攻击: 80
🎯 暴击: 25%
```

### 多语言切换

```
语言 zh    # 中文
语言 en    # English
语言 ja    # 日本語
```

### 情感记忆与日记

宵宫会自动记录你们的对话历史，并定期生成夏日手账：

```
日记
```

**示例日记：**
> *(坐在长野原烟花店的屋顶，轻轻翻开手账，笔尖在纸上沙沙作响)*
>
> **宵宫的夏日手账** 🎆
> 日期：2026年05月06日
> 天气：晴朗
>
> 今天和旅行者聊了 5 次天。大多数时候我很「元气」。
> 我们聊了很多关于「烟花、祭典」的话题。
> 今天真的很开心！和旅行者在一起的每一刻都像烟花一样绚烂！✨
>
> *(合上本子，露出灿烂的笑容)* 明天也要一起放烟花哦！🎇

### 互动小游戏

```
小游戏 烟花    # 烟花小游戏
小游戏 炸弹    # 炸弹小游戏
小游戏 回忆    # 回忆小游戏
```

### 主动聊天系统

宵宫会主动找你聊天哦！可以控制开关：

```
主动聊天 开    # 开启主动聊天
主动聊天 关    # 关闭主动聊天
```

### 性能监控

```
性能
```

查看各操作的性能统计（调用次数、平均耗时等）。

### 季节事件

在特定日期，宵宫会自动发送特殊台词：
- **6月21日** — 夏至 🌞
- **7月7日** — 七夕 🎋
- **8月1日** — 宵宫的生日 🎂
- **12月31日** — 跨年 🎆
- **1月1日** — 新年 🎊

### 帮助

```
帮助
```

## 📁 文件结构

```
Yoimiya-Skill/
├── SKILL.md                          # Skill 说明文档
├── README.md                         # 本文件
├── CHANGELOG.md                      # 版本更新日志
├── LICENSE                           # MIT 许可证
├── requirements.txt                  # 依赖列表
├── docs/
│   └── API.md                        # API 文档
├── __init__.py                       # 包入口
├── yoimiya_skill/                    # Skill 主包
│   ├── __init__.py
│   ├── yoimiya_skill.py              # Skill 主类
│   ├── config.json                   # 配置文件
│   ├── prompts.json                  # 提示词配置（系统提示词、情绪状态）⭐
│   ├── prompts.py                    # 提示词加载器（支持热重载）
│   ├── emotion_manager.py            # 情绪状态管理器
│   ├── memory.py                     # 情感记忆系统
│   ├── events.py                     # 季节事件 & 小游戏
│   └── data/
│       └── memory.json               # 记忆持久化文件
├── tests/                            # 测试目录
│   ├── __init__.py
│   └── test_skill.py                 # 完整测试套件
└── .github/                          # GitHub 配置
    ├── ISSUE_TEMPLATE/
    ├── workflows/
    │   └── ci.yml                    # CI 自动化测试
    └── PULL_REQUEST_TEMPLATE.md
```

## 🔧 自定义配置

### 修改提示词（无需改代码！）

编辑 `yoimiya_skill/prompts.json` 即可自定义：

```json
{
  "system_prompts": {
    "zh": "你的自定义宵宫提示词...",
    "en": "Your custom Yoimiya prompt...",
    "ja": "あなたのカスタム宵宮プロンプト..."
  },
  "emotion_states": {
    "元气": {
      "trigger_keywords": ["烟花", "祭典", "夏天"],
      "system_prompt_addition": {
        "zh": "你现在特别元气！"
      }
    }
  }
}
```

修改后自动生效（或重启 Skill）！

### 修改配置

编辑 `yoimiya_skill/config.json` 即可自定义：

- **角色属性**：修改 `character.stats`
- **情绪波动概率**：修改 `skill.auto_shift_probability`
- **主动聊天间隔**：修改 `skill.proactive_chat_interval`
- **情感关键词**：修改 `emotion_keywords`
- **季节事件**：修改 `seasonal_events`
- **小游戏内容**：修改 `minigames`
- **性能监控**：修改 `performance` 和 `monitoring`

### 添加新语言

1. 在 `prompts.json` 的 `meta.supported_languages` 中添加语言代码
2. 为 `system_prompts` 和每个情绪状态的 `system_prompt_addition` 添加新语言
3. 在 `config.json` 的季节事件消息中添加新语言

### 添加新情绪状态

1. 在 `prompts.json` 的 `emotion_states` 中添加新情绪状态的提示词
2. 在 `config.json` 的 `emotion_states` 中添加新情绪的配置（关键词、标签）

详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 📚 文档

- [SKILL.md](SKILL.md) - Skill 使用说明
- [docs/API.md](docs/API.md) - 详细 API 文档
- [CHANGELOG.md](CHANGELOG.md) - 版本更新日志
- [CONTRIBUTING.md](CONTRIBUTING.md) - 贡献指南

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 📜 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

## 🙏 致谢

- 灵感来源于《原神》中的角色 **宵宫（长野原宵宫）**
- 基于 [OpenClaw](https://github.com/openclaw) 框架开发
- v1.0 项目结构和设计参考了 [March7th-Skill](https://github.com/Kitaro-Loked/March7th-Skill)

---

> *"烟花虽然只在夜空中绽放一瞬，但在看到它的人心中，那份感动会永远留存。这就是我喜欢烟花的原因。"* —— 宵宫
