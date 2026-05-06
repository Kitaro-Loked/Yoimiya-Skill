"""性能追踪模块 - 增强版

增强功能：
- 慢操作告警阈值配置
- 上下文信息记录
- 告警回调支持
- 结构化统计输出
"""

import logging
import time
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

# 告警回调类型
AlertCallback = Callable[[str, float, Dict[str, Any]], None]


class PerformanceTracker:
    """增强版性能追踪器"""

    def __init__(
        self,
        enabled: bool = True,
        slow_threshold: float = 1.0,
        alert_callback: Optional[AlertCallback] = None,
    ):
        """
        Args:
            enabled: 是否启用性能追踪
            slow_threshold: 慢操作告警阈值（秒）
            alert_callback: 慢操作告警回调函数，签名为 (name, duration, context) -> None
        """
        self.enabled = enabled
        self.slow_threshold = slow_threshold
        self.alert_callback = alert_callback
        self._timings: Dict[str, List[Dict[str, Any]]] = {}

    def track(self, name: str, **context: Any):
        """上下文管理器，用于追踪代码块执行时间

        Args:
            name: 追踪名称
            **context: 额外的上下文信息（如 user_id、message_length 等）

        Example:
            with tracker.track("handle_message", user_id="123"):
                await process_message(ctx)
        """
        return _PerformanceContext(self, name, **context)

    def record(self, name: str, duration: float, **context: Any) -> None:
        """记录一次执行时间

        Args:
            name: 追踪名称
            duration: 执行耗时（秒）
            **context: 额外的上下文信息
        """
        if not self.enabled:
            return

        if name not in self._timings:
            self._timings[name] = []

        self._timings[name].append({
            "duration": duration,
            "context": context,
        })

        # 慢操作告警
        if duration > self.slow_threshold:
            logger.warning(
                f"Slow operation: {name} took {duration:.3f}s "
                f"(threshold: {self.slow_threshold:.3f}s)"
            )
            if self.alert_callback:
                try:
                    self.alert_callback(name, duration, context)
                except Exception as e:
                    logger.error(f"Alert callback failed: {e}")

    def get_stats(self, name: str) -> Dict[str, Any]:
        """获取性能统计

        Returns:
            包含 count、avg、min、max、p95 的字典
        """
        records = self._timings.get(name, [])
        if not records:
            return {}

        durations = [r["duration"] for r in records]
        durations_sorted = sorted(durations)
        n = len(durations_sorted)
        p95_idx = int(n * 0.95) - 1
        p95 = durations_sorted[max(0, p95_idx)]

        return {
            "count": n,
            "avg": sum(durations) / n,
            "min": min(durations),
            "max": max(durations),
            "p95": p95,
            "slow_count": sum(1 for d in durations if d > self.slow_threshold),
        }

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """获取所有性能统计"""
        return {name: self.get_stats(name) for name in self._timings}

    def get_slow_operations(self) -> List[Dict[str, Any]]:
        """获取所有慢操作记录

        Returns:
            慢操作列表，每项包含 name、duration、context
        """
        slow_ops = []
        for name, records in self._timings.items():
            for record in records:
                if record["duration"] > self.slow_threshold:
                    slow_ops.append({
                        "name": name,
                        "duration": record["duration"],
                        "context": record["context"],
                    })
        return slow_ops

    def reset(self) -> None:
        """重置所有性能数据"""
        self._timings.clear()
        logger.info("Performance tracker reset")

    def export_stats(self) -> Dict[str, Any]:
        """导出完整统计信息（用于监控上报）"""
        return {
            "enabled": self.enabled,
            "slow_threshold": self.slow_threshold,
            "operations": self.get_all_stats(),
            "slow_operations": self.get_slow_operations(),
        }


class _PerformanceContext:
    """性能追踪上下文管理器"""

    def __init__(self, tracker: PerformanceTracker, name: str, **context: Any):
        self.tracker = tracker
        self.name = name
        self.context = context
        self.start_time = 0.0

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        # 如果有异常，在上下文中记录
        if exc_type is not None:
            self.context["error"] = f"{exc_type.__name__}: {exc_val}"
        self.tracker.record(self.name, duration, **self.context)
