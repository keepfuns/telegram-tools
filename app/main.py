import logging
from src import conf, monitor, log, client, scheduler
import asyncio

logger = logging.getLogger(__name__)


async def app():
    logger.info("🚀 启动Telegram-Tools系统...")

    # 初始化日志
    log.Log("INFO")

    config_manager = conf.ConfigManager()
    # 创建默认配置文件（如果不存在）
    config_manager.create_default_config()

    # 加载配置
    config = config_manager.load_config()

    if config_manager.validate_config(config):
        client_manage = None
        telegram_scheduler = None

        client_manage = client.ClientManage(config)
        await client_manage.init_client()

        try:
            # 启动监控
            telegram_monitor = monitor.TelegramMonitor(config)
            await telegram_monitor.start(client_manage)
        except Exception as e:
            logger.error(f"❌ 监控转发功能错误: {e}")

        try:
            # 启动定时
            telegram_scheduler = scheduler.TelegramScheduler(config)
            await telegram_scheduler.start(client_manage)
        except Exception as e:
            logger.error(f"❌ 定时发送功能错误: {e}")


if __name__ == "__main__":
    asyncio.run(app())
