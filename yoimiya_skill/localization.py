"""本地化文本管理模块

将原本内联在 yoimiya_skill.py 中的本地化文本抽离，
支持多语言扩展，便于维护和翻译。
"""

from typing import Any, Dict

# 本地化文本数据
_LOCALIZED_TEXTS: Dict[str, Dict[str, str]] = {
    "zh": {
        "unknown_emotion": "欸？'{emotion}'是什么情绪呀，我没听说过呢~\n当前情绪：{current}",
        "emotion_hint": "欸？你想了解什么情绪呀？当前情绪：{current}",
        "current_emotion": "当前情绪：{emotion}",
        "stats_title": "📊 宵宫属性",
        "memory_cleared": "*(歪头)* 嗯……之前的记忆？好像被一阵风吹走了呢！不过没关系，我们可以创造新的回忆！🎆",
        "diary_not_ready": "*(翻着手账)* 唔……对话还不够多呢，再聊一会儿再写手账吧！",
        "language_changed": "语言已切换为：{lang}",
        "unknown_language": "不支持的语言：{lang}。支持：zh / en / ja",
        "game_list": "🎮 可用小游戏：\n",
        "unknown_game": "不知道这个游戏呢……可用游戏：\n",
        "proactive_on": "主动聊天已开启！我会时不时找你聊天哦~",
        "proactive_off": "主动聊天已关闭。我会安静等你找我啦。",
        "emotion_changed": "*(情绪变化)* {message}",
        "help_text": (
            "**宵宫·夏日灵魂觉醒 v1.1** 🎆\n\n"
            "📋 指令列表：\n"
            "- `情绪` - 查看当前情绪状态\n"
            "- `语言 <zh/en/ja>` - 切换语言\n"
            "- `日记` - 查看对话总结\n"
            "- `清空记忆` - 清空情感记忆\n"
            "- `小游戏 <游戏名>` - 玩互动小游戏\n"
            "- `主动聊天 <开/关>` - 开启/关闭主动聊天\n"
            "- `帮助` - 显示此帮助信息\n\n"
            "🎭 情绪状态会根据对话内容自然流动\n"
            "💫 对话中有 {prob}% 概率情绪波动\n"
            "💬 主动聊天：{proactive}"
        ),
    },
    "en": {
        "unknown_emotion": "Huh? I've never heard of the '{emotion}' emotion~\nCurrent emotion: {current}",
        "emotion_hint": "Huh? What emotion do you want to know about? Current emotion: {current}",
        "current_emotion": "Current emotion: {emotion}",
        "stats_title": "📊 Yoimiya Stats",
        "memory_cleared": "*(tilts head)* Hmm... previous memories? Seems like they were blown away by the wind! But it's okay, we can create new ones! 🎆",
        "diary_not_ready": "*(flipping through diary)* Mmm... not enough conversations yet, let's chat a bit more before writing the diary!",
        "language_changed": "Language changed to: {lang}",
        "unknown_language": "Unsupported language: {lang}. Supported: zh / en / ja",
        "game_list": "🎮 Available minigames:\n",
        "unknown_game": "I don't know that game... Available games:\n",
        "proactive_on": "Proactive chat is on! I'll chat with you from time to time~",
        "proactive_off": "Proactive chat is off. I'll wait quietly for you to find me.",
        "emotion_changed": "*(emotional shift)* {message}",
        "help_text": (
            "**Yoimiya: Summer Soul Awakening v1.1** 🎆\n\n"
            "📋 Command List:\n"
            "- `emotion` - View current emotional state\n"
            "- `language <zh/en/ja>` - Switch language\n"
            "- `diary` - View conversation summary\n"
            "- `clear memory` - Clear emotional memory\n"
            "- `minigame <name>` - Play interactive minigames\n"
            "- `proactive chat <on/off>` - Enable/disable proactive chat\n"
            "- `help` - Show this help\n\n"
            "🎭 Emotional states flow naturally based on conversation\n"
            "💫 {prob}% chance of emotional fluctuation during conversation\n"
            "💬 Proactive chat: {proactive}"
        ),
    },
    "ja": {
        "unknown_emotion": "え？「{emotion}」って何の感情？聞いたことないよ~\n現在の感情：{current}",
        "emotion_hint": "え？どの感情を知りたいの？現在の感情：{current}",
        "current_emotion": "現在の感情：{emotion}",
        "stats_title": "📊 宵宮ステータス",
        "memory_cleared": "*(首をかしげる)* うーん……前の記憶？風に吹き飛ばされちゃったみたい！でも大丈夫、新しい思い出を作ろう！🎆",
        "diary_not_ready": "*(手帳をめくる)* うーん……まだ会話が足りないね、もう少しおしゃべりしてから日記を書こう！",
        "language_changed": "言語を変更しました：{lang}",
        "unknown_language": "未対応の言語：{lang}。対応：zh / en / ja",
        "game_list": "🎮 利用可能なミニゲーム：\n",
        "unknown_game": "そのゲームは知らないな……利用可能なゲーム：\n",
        "proactive_on": "主动チャットがオンになったよ！時々話しかけるね~",
        "proactive_off": "主动チャットがオフになったよ。静かに待ってるね。",
        "emotion_changed": "*(感情の変化)* {message}",
        "help_text": (
            "**宵宮·夏の魂の覚醒 v1.1** 🎆\n\n"
            "📋 コマンド一覧：\n"
            "- `感情` - 現在の感情状態を確認\n"
            "- `言語 <zh/en/ja>` - 言語を切り替え\n"
            "- `日記` - 会話のまとめを見る\n"
            "- `記憶消去` - 感情記憶を消去\n"
            "- `ミニゲーム <名前>` - インタラクティブなミニゲームを遊ぶ\n"
            "- `主动チャット <オン/オフ>` - 主动チャットのオン/オフ\n"
            "- `ヘルプ` - このヘルプを表示\n\n"
            "🎭 感情状態は会話の内容に応じて自然に流れる\n"
            "💫 会話中に {prob}% の確率で感情の起伏\n"
            "💬 主动チャット：{proactive}"
        ),
    },
}

# 情绪变化提示消息（按情绪状态和多语言）
_EMOTION_SHIFT_MESSAGES: Dict[str, Dict[str, str]] = {
    "元气": {
        "zh": "*(眼睛亮了起来)* 嘿嘿，说到这个我就来劲了！",
        "en": "*(eyes light up)* Hehe, you got me excited talking about this!",
        "ja": "*(目が輝く)* えへへ、これの話をすると私も張り切っちゃう！",
    },
    "热血": {
        "zh": "*(握紧了拳头)* 嗯！这种时候就该拿出干劲来！",
        "en": "*(clenches fist)* Yeah! This is when we need to give it our all!",
        "ja": "*(拳を握る)* うん！こういう時は気合を入れないとね！",
    },
    "温柔": {
        "zh": "*(声音变得轻柔)* 啊……这个话题，让我有点感触呢。",
        "en": "*(voice becomes gentle)* Ah... this topic, it touches me a bit.",
        "ja": "*(声が優しくなる)* ああ……この話題、少し感傷的になっちゃうな。",
    },
}

# 主动聊天消息（按语言）
_PROACTIVE_MESSAGES: Dict[str, list] = {
    "zh": [
        "*(托腮看着你)* 旅行者，你在想什么呢？跟我说说嘛~",
        "*(突然凑近)* 嘿！我刚刚想到一个新的烟花配方，你要不要听听看？",
        "*(望着窗外)* 今天的夕阳好美啊……等下一起去屋顶看星星好不好？",
        "*(伸了个懒腰)* 唔……有点困了。旅行者，给我讲个故事提神好不好？",
        "*(眼睛闪闪发光)* 旅行者旅行者！我刚刚看到一只好可爱的猫！你要不要去看看？",
    ],
    "en": [
        "*(resting chin on hands, looking at you)* Traveler, what are you thinking about? Tell me~",
        "*(suddenly leaning in)* Hey! I just thought of a new firework recipe, want to hear it?",
        "*(looking out the window)* Today's sunset is so beautiful... Want to go to the rooftop to watch the stars later?",
        "*(stretching)* Mmm... a bit sleepy. Traveler, tell me a story to wake me up?",
        "*(eyes sparkling)* Traveler, Traveler! I just saw such a cute cat! Want to go see it?",
    ],
    "ja": [
        "*(頬杖をついてあなたを見つめる)* 旅人、何考えてるの？教えてよ~",
        "*(突然近づいて)* ねえ！新しい花火の配合を思いついたんだ、聞きたい？",
        "*(窓の外を見る)* 今日の夕陽が綺麗だね……後で屋根の上で星を見に行かない？",
        "*(伸びをする)* うーん……少し眠いな。旅人、目が覚めるような話をして？",
        "*(目を輝かせる)* 旅人旅人！さっきすっごく可愛い猫を見たんだ！一緒に見に行かない？",
    ],
}


def get_localized_text(key: str, language: str = "zh", **kwargs: Any) -> str:
    """获取本地化文本

    Args:
        key: 文本键名
        language: 语言代码（zh/en/ja）
        **kwargs: 格式化参数

    Returns:
        本地化后的文本，如果找不到则返回 key 本身
    """
    lang_texts = _LOCALIZED_TEXTS.get(language, _LOCALIZED_TEXTS["zh"])
    text = lang_texts.get(key, key)
    try:
        return text.format(**kwargs)
    except KeyError:
        # 格式化失败时返回原始文本
        return text


def get_emotion_shift_message(emotion: str, language: str = "zh") -> str:
    """获取情绪变化提示消息

    Args:
        emotion: 情绪状态名称
        language: 语言代码

    Returns:
        情绪变化提示消息，如果找不到则返回空字符串
    """
    return _EMOTION_SHIFT_MESSAGES.get(emotion, {}).get(language, "")


def get_proactive_messages(language: str = "zh") -> list:
    """获取主动聊天消息列表

    Args:
        language: 语言代码

    Returns:
        主动聊天消息列表
    """
    return _PROACTIVE_MESSAGES.get(language, _PROACTIVE_MESSAGES["zh"])


def get_supported_languages() -> list:
    """获取支持的语言列表"""
    return list(_LOCALIZED_TEXTS.keys())
