# 贡献指南

感谢你对 Yoimiya-Skill 项目的关注！我们欢迎各种形式的贡献。

## 📝 如何贡献

### 报告问题

如果你发现了 bug 或有新功能建议，请通过 [GitHub Issues](https://github.com/Kitaro-Loked/Yoimiya-Skill/issues) 提交。

提交 Issue 时，请尽量包含以下信息：
- 问题的详细描述
- 复现步骤
- 期望行为 vs 实际行为
- 环境信息（Python 版本、OpenClaw 版本等）

### 提交代码

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

### 代码规范

- 遵循 PEP 8 代码风格
- 使用类型提示（Type Hints）
- 添加适当的文档字符串（docstrings）
- 确保所有测试通过：`python -m unittest discover -s tests -v`
- 确保 JSON 配置文件有效

### 项目结构

```
yoimiya_skill/
├── __init__.py           # 包入口
├── yoimiya_skill.py      # Skill 主类
├── config.json           # 配置文件（属性、事件、小游戏）
├── prompts.json          # 提示词配置（多语言系统提示词、变身台词）
├── prompts.py            # 提示词加载器（支持热重载）
├── form_manager.py       # 形态管理器（策略模式）
├── memory.py             # 情感记忆系统
├── events.py             # 季节事件 & 小游戏
└── data/
    └── memory.json       # 记忆持久化文件
```

### 添加新形态

1. 在 `prompts.json` 的 `forms` 中添加新形态的提示词（zh/en/ja）
2. 在 `config.json` 的 `forms` 中添加新形态的属性配置
3. 在 `form_manager.py` 中创建新的形态策略类
4. 在 `FormManager._FORM_STRATEGIES` 中注册新形态
5. 添加对应的单元测试

### 添加新语言

1. 在 `prompts.json` 中为每个形态的 `system_prompts`、`shift_message`、`switch_reply` 添加新语言
2. 在 `prompts.json` 的 `meta.supported_languages` 中添加语言代码
3. 在 `config.json` 的季节事件消息中添加新语言
4. 在 `yoimiya_skill.py` 的 `_get_localized_text` 中添加新语言文本

## 📜 行为准则

请保持友善和尊重，让我们共同维护一个积极的社区环境。

## 📧 联系方式

如有任何问题，欢迎通过 GitHub Issues 与我们联系。
