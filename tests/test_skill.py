"""YoimiyaSummerSoul Skill 完整测试套件 v1.2"""

import json
import os
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock openclaw.sdk 以避免依赖问题
class MockBaseSkill:
    def __init__(self):
        pass

class MockDecorator:
    def __call__(self, func):
        return func

def mock_on_command(cmd):
    return MockDecorator()

def mock_on_message():
    return MockDecorator()

# 注入 mock 模块
mock_sdk = type(sys)('openclaw.sdk')
mock_sdk.BaseSkill = MockBaseSkill
mock_sdk.on_command = mock_on_command
mock_sdk.on_message = mock_on_message
sys.modules['openclaw'] = type(sys)('openclaw')
sys.modules['openclaw.sdk'] = mock_sdk

from yoimiya_skill.yoimiya_skill import YoimiyaSummerSoul, PerformanceTracker, setup_logging
from yoimiya_skill.memory import EmotionMemory, MemoryEntry
from yoimiya_skill.emotion_manager import EmotionManager, EmotionState
from yoimiya_skill.events import SeasonalEventManager, MinigameManager
from yoimiya_skill.prompts import get_system_prompt, get_supported_languages, get_all_emotion_states
from yoimiya_skill.localization import get_localized_text, get_emotion_shift_message, get_proactive_messages
from yoimiya_skill.config_manager import ConfigManager
from yoimiya_skill.exceptions import ConfigError, MemoryError


class TestConfigManager(unittest.TestCase):
    """测试配置管理器"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "config.json")
        config = {
            "skill": {"name": "TestSkill", "version": "1.0.0"},
            "performance": {"prompt_cache_ttl": 1800},
            "monitoring": {"log_level": "DEBUG"},
            "emotion_keywords": {"烟花": "test response"},
        }
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f)
        self.manager = ConfigManager(config_path=self.config_path, ttl=1)

    def tearDown(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        os.rmdir(self.temp_dir)

    def test_get_config(self):
        config = self.manager.get_config()
        self.assertIn("skill", config)
        self.assertEqual(config["skill"]["name"], "TestSkill")

    def test_get_nested(self):
        name = self.manager.get("skill.name")
        self.assertEqual(name, "TestSkill")

    def test_get_default(self):
        value = self.manager.get("nonexistent.key", "default")
        self.assertEqual(value, "default")

    def test_cache(self):
        # 第一次加载
        config1 = self.manager.get_config()
        # 第二次应该从缓存读取
        config2 = self.manager.get_config()
        self.assertEqual(config1, config2)

    def test_cache_ttl_expiry(self):
        # 获取配置
        self.manager.get_config()
        # 修改文件
        time.sleep(0.1)
        config = {
            "skill": {"name": "UpdatedSkill", "version": "2.0.0"},
            "performance": {},
            "monitoring": {},
        }
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f)
        # 等待缓存过期
        time.sleep(1.1)
        new_config = self.manager.get_config()
        self.assertEqual(new_config["skill"]["name"], "UpdatedSkill")

    def test_force_reload(self):
        config1 = self.manager.get_config()
        # 修改文件
        config = {
            "skill": {"name": "ForceReloaded", "version": "3.0.0"},
            "performance": {},
            "monitoring": {},
        }
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f)
        # 强制重载
        config2 = self.manager.get_config(force_reload=True)
        self.assertEqual(config2["skill"]["name"], "ForceReloaded")

    def test_get_skill_config(self):
        skill_config = self.manager.get_skill_config()
        self.assertEqual(skill_config["name"], "TestSkill")
        self.assertEqual(skill_config["prompt_cache_ttl"], 1800)
        self.assertEqual(skill_config["log_level"], "DEBUG")

    def test_get_emotion_keywords(self):
        keywords = self.manager.get_emotion_keywords()
        self.assertIn("烟花", keywords)

    def test_file_not_found(self):
        bad_manager = ConfigManager(config_path="/nonexistent/config.json")
        with self.assertRaises(FileNotFoundError):
            bad_manager.get_config()


class TestLocalization(unittest.TestCase):
    """测试本地化模块"""

    def test_get_localized_text_zh(self):
        text = get_localized_text("current_emotion", "zh", emotion="元气")
        self.assertIn("元气", text)

    def test_get_localized_text_en(self):
        text = get_localized_text("current_emotion", "en", emotion="Energetic")
        self.assertIn("Energetic", text)

    def test_get_localized_text_ja(self):
        text = get_localized_text("current_emotion", "ja", emotion="元気")
        self.assertIn("元気", text)

    def test_get_localized_text_unknown_key(self):
        text = get_localized_text("unknown_key", "zh")
        self.assertEqual(text, "unknown_key")

    def test_get_emotion_shift_message(self):
        msg = get_emotion_shift_message("元气", "zh")
        self.assertTrue(len(msg) > 0)

    def test_get_emotion_shift_message_unknown(self):
        msg = get_emotion_shift_message("unknown", "zh")
        self.assertEqual(msg, "")

    def test_get_proactive_messages(self):
        msgs = get_proactive_messages("zh")
        self.assertTrue(len(msgs) > 0)

    def test_get_proactive_messages_default(self):
        msgs = get_proactive_messages("unknown_lang")
        self.assertTrue(len(msgs) > 0)


class TestPrompts(unittest.TestCase):
    """测试提示词系统"""

    def test_get_system_prompt_zh(self):
        prompt = get_system_prompt("zh")
        self.assertIn("Identity", prompt)
        self.assertIn("宵宫", prompt)

    def test_get_system_prompt_en(self):
        prompt = get_system_prompt("en")
        self.assertIn("Identity", prompt)
        self.assertIn("Yoimiya", prompt)

    def test_get_system_prompt_ja(self):
        prompt = get_system_prompt("ja")
        self.assertIn("Identity", prompt)
        self.assertIn("宵宮", prompt)

    def test_get_system_prompt_all_languages(self):
        for lang in ["zh", "en", "ja"]:
            prompt = get_system_prompt(lang)
            self.assertTrue(len(prompt) > 0, f"{lang} prompt is empty")

    def test_supported_languages(self):
        langs = get_supported_languages()
        self.assertEqual(langs, ["zh", "en", "ja"])

    def test_emotion_states(self):
        states = get_all_emotion_states()
        self.assertIn("元气", states)
        self.assertIn("热血", states)
        self.assertIn("温柔", states)


class TestMemory(unittest.TestCase):
    """测试情感记忆系统"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.memory_path = os.path.join(self.temp_dir, "memory.json")
        self.memory = EmotionMemory(max_entries=10, storage_path=self.memory_path)

    def tearDown(self):
        if os.path.exists(self.memory_path):
            os.remove(self.memory_path)
        os.rmdir(self.temp_dir)

    def test_add_memory(self):
        self.memory.add("你好", "你好呀！", "元气", 0.5, ["问候"])
        self.assertEqual(self.memory.memory_count, 1)

    def test_get_recent(self):
        for i in range(5):
            self.memory.add(f"msg{i}", f"resp{i}", "元气")
        recent = self.memory.get_recent(3)
        self.assertEqual(len(recent), 3)
        self.assertEqual(recent[-1].user_message, "msg4")

    def test_max_entries_limit(self):
        for i in range(15):
            self.memory.add(f"msg{i}", f"resp{i}", "元气")
        self.assertEqual(self.memory.memory_count, 10)

    def test_get_relevant_memories(self):
        self.memory.add("烟花", "砰——啪！", "元气", keywords=["烟花"])
        self.memory.add("战斗", "看箭！", "热血", keywords=["战斗"])
        relevant = self.memory.get_relevant_memories("烟花", top_k=1)
        self.assertEqual(len(relevant), 1)
        self.assertEqual(relevant[0].user_message, "烟花")

    def test_memory_summary(self):
        self.memory.add("你好", "你好呀！", "元气")
        summary = self.memory.get_memory_summary()
        self.assertIn("Recent Memories", summary)

    def test_emotion_trend(self):
        self.memory.add("a", "b", "元气", 0.5)
        self.memory.add("c", "d", "元气", 0.3)
        trend = self.memory.get_emotion_trend()
        self.assertAlmostEqual(trend, 0.4, places=1)

    def test_form_frequency(self):
        self.memory.add("a", "b", "元气")
        self.memory.add("c", "d", "热血")
        self.memory.add("e", "f", "元气")
        freq = self.memory.get_form_frequency()
        self.assertEqual(freq["元气"], 2)
        self.assertEqual(freq["热血"], 1)

    def test_preferences(self):
        self.memory.set_preference("language", "en")
        self.assertEqual(self.memory.get_preference("language"), "en")
        self.assertEqual(self.memory.get_preference("unknown", "default"), "default")

    def test_generate_diary(self):
        for i in range(5):
            self.memory.add(f"msg{i}", f"resp{i}", "元气", 0.2)
        diary = self.memory.generate_diary()
        self.assertIn("手账", diary)
        self.assertIn("msg", diary)

    def test_clear(self):
        self.memory.add("a", "b", "元气")
        self.memory.clear()
        self.assertEqual(self.memory.memory_count, 0)

    def test_persistence(self):
        self.memory.add("test", "response", "元气")
        # 创建新实例，应该能加载之前的记忆
        memory2 = EmotionMemory(max_entries=10, storage_path=self.memory_path)
        self.assertEqual(memory2.memory_count, 1)

    def test_auto_cleanup_by_age(self):
        """测试按年龄自动清理"""
        # 创建一条旧记忆
        old_entry = MemoryEntry(
            timestamp=(datetime.now() - timedelta(days=10)).isoformat(),
            user_message="old",
            bot_response="old_resp",
            form="元气",
        )
        self.memory._memories.append(old_entry)
        self.memory.save()

        # 创建新实例触发清理
        memory2 = EmotionMemory(
            max_entries=10,
            storage_path=self.memory_path,
            auto_cleanup=True,
            cleanup_interval=0,  # 立即清理
            max_age_days=7,
        )
        # 旧记忆应该被清理
        self.assertEqual(memory2.memory_count, 0)

    def test_manual_cleanup(self):
        """测试手动清理"""
        old_entry = MemoryEntry(
            timestamp=(datetime.now() - timedelta(days=10)).isoformat(),
            user_message="old",
            bot_response="old_resp",
            form="元气",
        )
        self.memory._memories.append(old_entry)
        self.memory.add("new", "new_resp", "元气")

        removed = self.memory.cleanup_old_memories(max_age_days=7)
        self.assertEqual(removed, 1)
        self.assertEqual(self.memory.memory_count, 1)

    def test_memory_entry_age(self):
        """测试记忆条目年龄计算"""
        entry = MemoryEntry(
            timestamp=datetime.now().isoformat(),
            user_message="test",
            bot_response="test",
            form="元气",
        )
        self.assertLess(entry.age_seconds, 1)

        old_entry = MemoryEntry(
            timestamp=(datetime.now() - timedelta(days=1)).isoformat(),
            user_message="old",
            bot_response="old",
            form="元气",
        )
        self.assertGreater(old_entry.age_seconds, 86000)


class TestEmotionManager(unittest.TestCase):
    """测试情绪管理器"""

    def setUp(self):
        self.manager = EmotionManager()

    def test_get_all_states(self):
        states = self.manager.get_all_states()
        self.assertIn("元气", states)
        self.assertIn("热血", states)
        self.assertIn("温柔", states)

    def test_get_state(self):
        state = self.manager.get_state("元气")
        self.assertIsNotNone(state)
        self.assertEqual(state.name, "元气")
        self.assertIsInstance(state.keywords, list)

    def test_detect_emotion(self):
        # 包含元气关键词
        detected = self.manager.detect_emotion("烟花 祭典 孩子")
        self.assertEqual(detected, "元气")

        # 包含热血关键词
        detected = self.manager.detect_emotion("战斗 弓箭 勇气")
        self.assertEqual(detected, "热血")

        # 包含温柔关键词
        detected = self.manager.detect_emotion("回忆 星空 梦想")
        self.assertEqual(detected, "温柔")

        # 无关键词
        detected = self.manager.detect_emotion("abcdefg")
        self.assertIsNone(detected)

    def test_get_system_prompt_with_emotion(self):
        base = "Base prompt"
        result = self.manager.get_system_prompt_with_emotion(base, "元气", "zh")
        self.assertIn("Base prompt", result)
        self.assertIn("元气", result)

    def test_get_random_state(self):
        state = self.manager.get_random_state()
        self.assertIn(state, self.manager.get_all_states())

    def test_get_random_state_exclude(self):
        state = self.manager.get_random_state(exclude="元气")
        self.assertNotEqual(state, "元气")


class TestEvents(unittest.TestCase):
    """测试事件系统"""

    def setUp(self):
        self.event_manager = SeasonalEventManager()
        self.minigame_manager = MinigameManager()

    def test_seasonal_event_loading(self):
        events = self.event_manager.list_all_events()
        self.assertTrue(len(events) > 0)

    def test_event_message_structure(self):
        events = self.event_manager.list_all_events()
        for event in events:
            self.assertIn("date", event)
            self.assertIn("name", event)

    def test_fireworks_game(self):
        result = self.minigame_manager.play_fireworks_game("zh")
        self.assertIn("烟花", result)

    def test_fireworks_game_en(self):
        result = self.minigame_manager.play_fireworks_game("en")
        self.assertIn("firework", result)

    def test_fireworks_game_ja(self):
        result = self.minigame_manager.play_fireworks_game("ja")
        self.assertIn("花火", result)

    def test_bomb_game(self):
        result = self.minigame_manager.play_bomb_game("zh")
        self.assertIn("炸弹", result)

    def test_memory_game(self):
        result = self.minigame_manager.play_memory_game("zh")
        self.assertIn("回忆", result)

    def test_list_games(self):
        games = self.minigame_manager.list_games("zh")
        self.assertIn("烟花", games)
        self.assertIn("炸弹", games)
        self.assertIn("回忆", games)


class TestPerformanceTracker(unittest.TestCase):
    """测试性能追踪器"""

    def test_track_enabled(self):
        tracker = PerformanceTracker(enabled=True)
        with tracker.track("test_op"):
            pass
        stats = tracker.get_stats("test_op")
        self.assertEqual(stats["count"], 1)

    def test_track_disabled(self):
        tracker = PerformanceTracker(enabled=False)
        with tracker.track("test_op"):
            pass
        stats = tracker.get_stats("test_op")
        self.assertEqual(stats, {})

    def test_multiple_tracks(self):
        tracker = PerformanceTracker(enabled=True)
        for _ in range(5):
            with tracker.track("test_op"):
                pass
        stats = tracker.get_stats("test_op")
        self.assertEqual(stats["count"], 5)

    def test_slow_threshold_alert(self):
        """测试慢操作告警"""
        alerted = []

        def alert_callback(name, duration, context):
            alerted.append((name, duration, context))

        tracker = PerformanceTracker(
            enabled=True,
            slow_threshold=0.01,
            alert_callback=alert_callback,
        )
        with tracker.track("slow_op"):
            time.sleep(0.05)

        stats = tracker.get_stats("slow_op")
        self.assertEqual(stats["slow_count"], 1)
        self.assertEqual(len(alerted), 1)
        self.assertEqual(alerted[0][0], "slow_op")

    def test_p95_stats(self):
        tracker = PerformanceTracker(enabled=True)
        for i in range(20):
            tracker.record("test", float(i) * 0.01)
        stats = tracker.get_stats("test")
        self.assertIn("p95", stats)
        self.assertGreater(stats["p95"], 0)

    def test_context_tracking(self):
        tracker = PerformanceTracker(enabled=True)
        tracker.record("op", 0.5, user_id="123", message_length=50)
        stats = tracker.get_stats("op")
        self.assertEqual(stats["count"], 1)

    def test_reset(self):
        tracker = PerformanceTracker(enabled=True)
        tracker.record("op", 0.1)
        tracker.reset()
        stats = tracker.get_all_stats()
        self.assertEqual(stats, {})

    def test_export_stats(self):
        tracker = PerformanceTracker(enabled=True, slow_threshold=0.01)
        tracker.record("op", 0.5)
        exported = tracker.export_stats()
        self.assertTrue(exported["enabled"])
        self.assertEqual(exported["slow_threshold"], 0.01)
        self.assertIn("operations", exported)


class TestExceptions(unittest.TestCase):
    """测试自定义异常"""

    def test_config_error(self):
        err = ConfigError("test error")
        self.assertEqual(err.code, "CONFIG_ERROR")
        self.assertIn("test error", str(err))

    def test_config_not_found(self):
        err = ConfigError("not found")
        self.assertEqual(err.code, "CONFIG_ERROR")

    def test_memory_error(self):
        err = MemoryError("memory fail")
        self.assertEqual(err.code, "MEMORY_ERROR")


class TestYoimiyaSummerSoul(unittest.TestCase):
    """测试主 Skill 类"""

    def setUp(self):
        self.skill = YoimiyaSummerSoul()

    def test_initialization(self):
        self.assertEqual(self.skill.name, "Yoimiya_Summer_Soul_Skill")
        self.assertEqual(self.skill.current_emotion, "元气")
        self.assertEqual(self.skill.language, "zh")
        self.assertEqual(self.skill.version, "1.2.0")

    def test_config_manager(self):
        """测试 ConfigManager 已正确初始化"""
        self.assertIsNotNone(self.skill._config_manager)
        config = self.skill._config_manager.get_config()
        self.assertIn("skill", config)

    def test_proactive_chat_default(self):
        self.assertTrue(self.skill.proactive_chat_enabled)

    def test_default_emotion(self):
        self.assertIn(self.skill.current_emotion, self.skill._emotion_manager.get_all_states())

    def test_emotion_switch(self):
        # 模拟切换情绪
        old_emotion = self.skill.current_emotion
        self.skill.current_emotion = "热血"
        self.assertEqual(self.skill.current_emotion, "热血")
        self.assertNotEqual(old_emotion, self.skill.current_emotion)

    def test_detect_emotion(self):
        detected = self.skill._detect_emotion("我想看烟花")
        self.assertEqual(detected, "元气")

    def test_language_switch(self):
        self.skill.language = "en"
        self.assertEqual(self.skill.language, "en")
        self.skill.language = "ja"
        self.assertEqual(self.skill.language, "ja")

    def test_localized_text(self):
        text = self.skill._get_localized_text("current_emotion", emotion="元气")
        self.assertIn("元气", text)

    def test_localized_text_en(self):
        self.skill.language = "en"
        text = self.skill._get_localized_text("current_emotion", emotion="Energetic")
        self.assertIn("Energetic", text)

    def test_record_interaction(self):
        # 使用独立的临时内存路径
        import tempfile
        temp_dir = tempfile.mkdtemp()
        memory_path = os.path.join(temp_dir, "memory.json")
        self.skill._memory = EmotionMemory(max_entries=50, storage_path=memory_path)
        self.skill.record_interaction("你好", "你好呀！", 0.5)
        self.assertEqual(self.skill._memory.memory_count, 1)

    def test_get_memory_summary(self):
        self.skill.record_interaction("你好", "你好呀！")
        summary = self.skill.get_memory_summary()
        self.assertIn("Recent Memories", summary)

    def test_get_current_state_info(self):
        info = self.skill.get_current_state_info()
        self.assertEqual(info["emotion"], "元气")
        self.assertIn("emotion_tags", info)
        self.assertIn("keywords", info)
        self.assertIn("proactive_chat", info)

    def test_check_emotion_keywords(self):
        response = self.skill._check_emotion_keywords("烟花")
        self.assertIsNotNone(response)
        self.assertIn("烟花", response)

    def test_check_emotion_keywords_no_match(self):
        response = self.skill._check_emotion_keywords("xyzabc")
        self.assertIsNone(response)

    def test_config_loading(self):
        self.assertTrue(hasattr(self.skill, "_skill_config"))
        self.assertIn("auto_shift_probability", self.skill._skill_config)

    def test_performance_tracker(self):
        self.assertTrue(self.skill._perf_tracker.enabled)

    def test_proactive_message(self):
        msg = self.skill._get_proactive_message()
        self.assertIsNotNone(msg)
        self.assertTrue(len(msg) > 0)

    def test_reload_config(self):
        """测试配置重载"""
        self.skill.reload_config()
        # 重载后配置仍然可用
        config = self.skill._config_manager.get_config()
        self.assertIn("skill", config)

    def test_memory_auto_cleanup_enabled(self):
        """测试记忆自动清理已启用"""
        self.assertTrue(self.skill._memory.auto_cleanup)


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def setUp(self):
        self.skill = YoimiyaSummerSoul()

    def test_full_conversation_flow(self):
        """测试完整对话流程"""
        # 使用独立的临时内存路径
        import tempfile
        temp_dir = tempfile.mkdtemp()
        memory_path = os.path.join(temp_dir, "memory.json")
        self.skill._memory = EmotionMemory(max_entries=50, storage_path=memory_path)

        # 1. 初始状态
        self.assertEqual(self.skill.current_emotion, "元气")

        # 2. 记录对话
        self.skill.record_interaction("你好宵宫", "你好呀旅行者！", 0.8)
        self.assertEqual(self.skill._memory.memory_count, 1)

        # 3. 切换情绪
        self.skill.current_emotion = "热血"
        self.skill.record_interaction("教我射箭", "好！看好了！", 0.6)

        # 4. 检查记忆
        freq = self.skill._memory.get_form_frequency()
        self.assertEqual(freq["元气"], 1)
        self.assertEqual(freq["热血"], 1)

        # 5. 生成日记
        diary = self.skill._memory.generate_diary()
        self.assertIn("手账", diary)

    def test_multi_language_support(self):
        """测试多语言支持"""
        for lang in ["zh", "en", "ja"]:
            self.skill.language = lang
            prompt = get_system_prompt(lang)
            self.assertTrue(len(prompt) > 0, f"Prompt for {lang} is empty")

    def test_memory_persistence(self):
        """测试记忆持久化"""
        import tempfile
        temp_dir = tempfile.mkdtemp()
        memory_path = os.path.join(temp_dir, "memory.json")
        self.skill._memory = EmotionMemory(max_entries=50, storage_path=memory_path)

        self.skill.record_interaction("测试", "收到！", 0.0)
        count_before = self.skill._memory.memory_count

        # 创建新实例，使用相同路径
        skill2 = YoimiyaSummerSoul()
        skill2._memory = EmotionMemory(max_entries=50, storage_path=memory_path)
        self.assertEqual(skill2._memory.memory_count, count_before)

    def test_proactive_chat_toggle(self):
        """测试主动聊天开关"""
        self.assertTrue(self.skill.proactive_chat_enabled)
        self.skill.proactive_chat_enabled = False
        self.assertFalse(self.skill.proactive_chat_enabled)
        msg = self.skill._get_proactive_message()
        self.assertIsNone(msg)

    def test_emotion_detection_flow(self):
        """测试情绪检测流程"""
        # 元气话题
        emotion = self.skill._detect_emotion("今天祭典好热闹")
        self.assertEqual(emotion, "元气")

        # 热血话题
        emotion = self.skill._detect_emotion("我们去战斗吧")
        self.assertEqual(emotion, "热血")

        # 温柔话题
        emotion = self.skill._detect_emotion("你看那片星空")
        self.assertEqual(emotion, "温柔")

    def test_config_cache_performance(self):
        """测试配置缓存性能提升"""
        import time

        # 多次调用 _check_emotion_keywords，应该使用缓存
        start = time.time()
        for _ in range(100):
            self.skill._check_emotion_keywords("烟花")
        duration = time.time() - start

        # 100 次调用应该在 1 秒内完成（缓存生效）
        self.assertLess(duration, 1.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
