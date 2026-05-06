"""情感记忆系统：记录与用户的互动历史"""

import json
import logging
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """单条记忆条目"""
    timestamp: str
    user_message: str
    bot_response: str
    form: str
    emotion_score: float = 0.0  # 情感分数 (-1.0 ~ 1.0)
    keywords: List[str] = field(default_factory=list)
    context_summary: str = ""  # 上下文摘要

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
        return cls(**data)


class EmotionMemory:
    """情感记忆管理器"""

    def __init__(self, max_entries: int = 50, storage_path: Optional[str] = None):
        self.max_entries = max_entries
        self.storage_path = storage_path or os.path.join(
            os.path.dirname(__file__), "data", "memory.json"
        )
        self._memories: List[MemoryEntry] = []
        self._user_preferences: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """从文件加载记忆"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._memories = [
                        MemoryEntry.from_dict(entry) for entry in data.get("memories", [])
                    ]
                    self._user_preferences = data.get("preferences", {})
                logger.info(f"Loaded {len(self._memories)} memories from {self.storage_path}")
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                logger.warning(f"Failed to load memories: {e}. Starting fresh.")
                self._memories = []
                self._user_preferences = {}

    def save(self) -> None:
        """保存记忆到文件"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        data = {
            "memories": [entry.to_dict() for entry in self._memories],
            "preferences": self._user_preferences,
            "last_updated": datetime.now().isoformat(),
        }
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug(f"Saved {len(self._memories)} memories")
        except OSError as e:
            logger.error(f"Failed to save memories: {e}")

    def add(
        self,
        user_message: str,
        bot_response: str,
        form: str,
        emotion_score: float = 0.0,
        keywords: Optional[List[str]] = None,
        context_summary: str = "",
    ) -> None:
        """添加一条新记忆"""
        entry = MemoryEntry(
            timestamp=datetime.now().isoformat(),
            user_message=user_message,
            bot_response=bot_response,
            form=form,
            emotion_score=emotion_score,
            keywords=keywords or [],
            context_summary=context_summary,
        )
        self._memories.append(entry)
        # 限制记忆数量
        if len(self._memories) > self.max_entries:
            self._memories = self._memories[-self.max_entries :]
        self.save()

    def get_recent(self, n: int = 5) -> List[MemoryEntry]:
        """获取最近 n 条记忆"""
        return self._memories[-n:] if self._memories else []

    def get_relevant_memories(self, query: str, top_k: int = 3) -> List[MemoryEntry]:
        """基于关键词获取相关记忆（简单实现）"""
        query_keywords = set(query.lower().split())
        scored = []
        for entry in self._memories:
            score = 0
            entry_text = f"{entry.user_message} {entry.bot_response} {entry.context_summary}".lower()
            for kw in query_keywords:
                if kw in entry_text:
                    score += 1
            if entry.keywords:
                for kw in entry.keywords:
                    if kw.lower() in query.lower():
                        score += 2
            if score > 0:
                scored.append((score, entry))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored[:top_k]]

    def get_memory_summary(self) -> str:
        """生成记忆摘要，用于注入系统提示词"""
        if not self._memories:
            return ""
        recent = self.get_recent(3)
        lines = ["[Recent Memories]"]
        for entry in recent:
            lines.append(
                f"- [{entry.form}] User: {entry.user_message[:50]}... "
                f"You responded: {entry.bot_response[:50]}..."
            )
        return "\n".join(lines)

    def get_emotion_trend(self) -> float:
        """获取近期情感趋势"""
        if not self._memories:
            return 0.0
        recent = self.get_recent(10)
        if not recent:
            return 0.0
        return sum(entry.emotion_score for entry in recent) / len(recent)

    def get_form_frequency(self) -> Dict[str, int]:
        """统计各形态出现频率"""
        freq: Dict[str, int] = {}
        for entry in self._memories:
            freq[entry.form] = freq.get(entry.form, 0) + 1
        return freq

    def set_preference(self, key: str, value: Any) -> None:
        """设置用户偏好"""
        self._user_preferences[key] = value
        self.save()

    def get_preference(self, key: str, default: Any = None) -> Any:
        """获取用户偏好"""
        return self._user_preferences.get(key, default)

    def clear(self) -> None:
        """清空所有记忆"""
        self._memories = []
        self._user_preferences = {}
        self.save()
        logger.info("All memories cleared")

    def generate_diary(self) -> str:
        """生成日记摘要"""
        if not self._memories:
            return "*(坐在长野原烟花店的屋顶，托腮望着夜空)* 嗯……今天还没有什么记录呢。等下一起去看烟花吧！🎆"
        
        recent = self.get_recent(self.max_entries)
        form_freq = self.get_form_frequency()
        most_used_form = max(form_freq, key=form_freq.get) if form_freq else "夏祭"
        emotion_trend = self.get_emotion_trend()
        
        # 提取关键话题
        all_keywords = []
        for entry in recent:
            all_keywords.extend(entry.keywords)
        top_keywords = list(set(all_keywords))[:5] if all_keywords else ["烟花"]
        
        diary = (
            f"*(坐在长野原烟花店的屋顶，轻轻翻开手账，笔尖在纸上沙沙作响)*\n\n"
            f"**宵宫的夏日手账** 🎆\n"
            f"日期：{datetime.now().strftime('%Y年%m月%d日')}\n"
            f"天气：{'晴朗' if emotion_trend > 0 else '多云' if emotion_trend == 0 else '微雨'}\n\n"
            f"今天和旅行者聊了 {len(recent)} 次天。"
            f"大多数时候我是「{most_used_form}」形态。\n"
            f"我们聊了很多关于「{'、'.join(top_keywords)}」的话题。\n"
        )
        
        if emotion_trend > 0.3:
            diary += "今天真的很开心！和旅行者在一起的每一刻都像烟花一样绚烂！✨\n"
        elif emotion_trend < -0.3:
            diary += "今天有些心事……但没关系，有旅行者在身边，就像有烟花照亮夜空一样温暖。\n"
        else:
            diary += "平平淡淡的一天，但和旅行者在一起，就算平凡也闪闪发光，就像夏夜的萤火虫。\n"
        
        # 引用一条具体记忆
        if recent:
            memorable = recent[-1]
            diary += (
                f"\n印象最深的是旅行者说：「{memorable.user_message[:40]}……」\n"
                f"我当时回答说：「{memorable.bot_response[:40]}……」\n"
            )
        
        diary += "\n*(合上本子，露出灿烂的笑容)* 明天也要一起放烟花哦！🎇"
        return diary

    @property
    def memory_count(self) -> int:
        return len(self._memories)
