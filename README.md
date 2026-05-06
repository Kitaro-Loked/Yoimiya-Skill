# Yoimiya-Skill 🎆 v1.0

![宵宫夏日灵魂](yoimiya_banner.jpg)

> 宵宫·夏日灵魂觉醒（究极情感沉浸版）：夏祭·元气 / 琉金·热血 / 幻梦·温柔

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/Kitaro-Loked/Yoimiya-Skill/actions/workflows/ci.yml/badge.svg)](https://github.com/Kitaro-Loked/Yoimiya-Skill/actions)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

## ✨ 简介

这是一个为 [OpenClaw](https://github.com/openclaw) 框架设计的 Skill，让你的 AI 助手化身《原神》中的宵宫，并在三种不同形态间自由切换！

**v1.0 首发**：全面配置化提示词，所有系统提示词、变身台词、切换回复从代码剥离至 `prompts.json`，支持热重载和多语言扩展，无需修改代码即可自定义角色。

| 形态 | 特点 | 风格 | 属性倾向 |
|------|------|------|----------|
| 🎆 **夏祭** | 元气活泼的烟花女王，稻妻孩子们心目中的英雄 | 热情开朗，大量使用表情符号 🎆✨ | 高速度、高暴击 |
| 🔥 **琉金** | 英姿飒爽的弓箭战士，用火焰与勇气守护珍视的一切 | 干练有力，充满自信和正义感 | 高速度、高攻击 |
| 🌟 **幻梦** | 温柔深情的星空哲人，在寂静夜晚思考烟花与人生 | 富有哲理和诗意，温柔而深情 🌟🌙 | 均衡型、高温柔 |

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

### 自动形态涨落

在对话过程中，有 **15%** 的概率触发形态自动切换，宵宫会发送对应的变身台词！

**动态形态切换**

当对话内容包含特定关键词时，宵宫会智能切换到对应形态：
- 提到「烟花、祭典、孩子、笑容」→ 自动切换为 **夏祭**
- 提到「战斗、弓箭、保护、勇气」→ 自动切换为 **琉金**
- 提到「回忆、梦想、星空、温柔」→ 自动切换为 **幻梦**

### 手动切换形态

使用以下命令手动切换形态：

```
切换形态 夏祭
切换形态 琉金
切换形态 幻梦
```

### 查看形态属性

```
形态属性
```

显示当前形态的属性面板：
```
📊 形态属性
**夏祭** (夏祭 · 火)
🛡️ 防御: 50 | ❤️ 生命: 80
⚡ 速度: 85 | ⚔️ 攻击: 70
🎯 暴击: 20%
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
> 今天和旅行者聊了 5 次天。大多数时候我是「夏祭」形态。
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
│   ├── config.json                   # 配置文件（属性、事件、小游戏）
│   ├── prompts.json                  # 提示词配置（系统提示词、变身台词、多语言）⭐
│   ├── prompts.py                    # 提示词加载器（支持热重载）
│   ├── form_manager.py               # 形态管理器（策略模式）
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
  "forms": {
    "夏祭": {
      "system_prompts": {
        "zh": "你的自定义提示词...",
        "en": "Your custom prompt...",
        "ja": "あなたのカスタムプロンプト..."
      },
      "shift_message": {
        "zh": "你的自定义变身台词..."
      }
    }
  }
}
```

修改后自动生效（或重启 Skill）！

### 修改配置

编辑 `yoimiya_skill/config.json` 即可自定义：

- **形态属性**：修改 `forms` 下的 `stats`
- **变身概率**：修改 `skill.auto_shift_probability`
- **主动聊天间隔**：修改 `skill.proactive_chat_interval`
- **情感关键词**：修改 `emotion_keywords`
- **季节事件**：修改 `seasonal_events`
- **小游戏内容**：修改 `minigames`

### 添加新语言

1. 在 `prompts.json` 的 `meta.supported_languages` 中添加语言代码
2. 为每个形态的 `system_prompts`、`shift_message`、`switch_reply` 添加新语言
3. 在 `config.json` 的季节事件消息中添加新语言

### 添加新形态

1. 在 `prompts.json` 的 `forms` 中添加新形态的提示词
2. 在 `config.json` 的 `forms` 中添加新形态的属性配置
3. 在 `form_manager.py` 中创建新的形态策略类
4. 在 `FormManager._FORM_STRATEGIES` 中注册新形态

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
- 项目结构和设计参考了 [March7th-Skill](https://github.com/Kitaro-Loked/March7th-Skill)

---

> *"烟花虽然只在夜空中绽放一瞬，但在看到它的人心中，那份感动会永远留存。这就是我喜欢烟花的原因。"* —— 宵宫（夏祭形态）
