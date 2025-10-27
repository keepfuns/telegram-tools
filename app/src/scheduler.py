import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Dict, Any, List
from . import client

logger = logging.getLogger(__name__)


class TelegramScheduler:
    """Telegram定时任务管理器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.scheduler = AsyncIOScheduler()

    async def start_scheduler(self, client_manage: client.ClientManage):
        """调度定时任务"""
        # 检查是否有启用定时
        enabled_schedulers = [
            s for s in self.config.get("schedulers", []) if s.get("enabled", False)
        ]
        if not enabled_schedulers:
            logger.warning("⚠️ 没有启用的定时，关闭定时功能")
            return

        # 获取定时实体
        schedulers = self.config.get("schedulers", [])
        enabled_schedulers = [s for s in schedulers if s.get("enabled", False)]
        try:
            valid_schedulers = await client_manage.resolve_entities(enabled_schedulers)
            if not valid_schedulers:
                logger.error("❌ 没有有效定时实体，定时功能无法启动")
                return

            task_count = 0
            for scheduler in enabled_schedulers:
                try:
                    logger.info(scheduler)
                    trigger = CronTrigger.from_crontab(scheduler["cron"])
                    self.scheduler.add_job(
                        self.send_message,
                        trigger,
                        args=[client_manage, scheduler],
                        id=str(scheduler["id"]),
                        name=scheduler["name"],
                    )
                    task_count += 1
                except Exception as e:
                    logger.error(f"❌ 新增定时失败 {scheduler['name']}: {e}")

            self.scheduler.start()
            logger.info(f"✅ 定时任务已启动，共 {task_count} 个任务")
        except Exception as e:
            logger.error(f"❌ 执行定时任务失败: {e}")
            if self.scheduler.running:
                self.scheduler.shutdown()

    async def send_message(
        self,
        client_manage: client.ClientManage,
        scheduler: List[str],
    ):
        """发送定时消息"""
        try:
            await client_manage.client.send_message(
                scheduler["entity"], scheduler["message"]
            )
            logger.info(
                f"✅ 定时发送 {scheduler['message']} 到 {scheduler['name']} 成功"
            )
        except Exception as e:
            logger.error(
                f"❌ 定时发送 {scheduler['message']} 到 {scheduler['name']} 失败: {e}"
            )
