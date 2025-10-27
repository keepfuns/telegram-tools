import logging
from src import conf, monitor, log, client, scheduler
import asyncio


async def app():
    # 初始化日志
    log.Log("INFO")

    logger = logging.getLogger(__name__)
    logger.info("🚀 启动Telegram-Tools系统...")

    config_manager = conf.ConfigManager()
    # 创建默认配置文件（如果不存在）
    config_manager.create_default_config()

    # 加载配置
    config = config_manager.load_config()

    if config_manager.validate_config(config):
        client_manage = None
        telegram_scheduler = None

        try:
            client_manage = client.ClientManage(config)
            await client_manage.init_client()

            # 启动监控
            telegram_monitor = monitor.TelegramMonitor(config)
            await telegram_monitor.start_monitor(client_manage)

            # 启动定时
            telegram_scheduler = scheduler.TelegramScheduler(config)
            await telegram_scheduler.start_scheduler(client_manage)

            await client_manage.client.run_until_disconnected()
        except Exception as e:
            logger.error(f"❌ 程序运行出错: {e}")
        finally:
            if client_manage and client_manage.client.is_connected():
                await client_manage.client.disconnect()
            if telegram_scheduler and telegram_scheduler.scheduler.running:
                telegram_scheduler.scheduler.shutdown()
            logger.info("⏹️ Telegram-Tools系统已停止")


if __name__ == "__main__":
    asyncio.run(app())
