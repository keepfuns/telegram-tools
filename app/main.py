import logging
from src import conf, monitor, log, client, scheduler
import sys

logger = logging.getLogger(__name__)


logger.info("🚀 启动Telegram-Tools系统...")

# 初始化日志
log.Log("INFO")

config_manager = conf.ConfigManager()
# 创建默认配置文件（如果不存在）
config_manager.create_default_config()

# 加载配置
config = config_manager.load_config()

if config_manager.validate_config(config):
    telegram_client = None
    telegram_scheduler = None
    try:
        telegram_client = client.TelegramClient(config)

        # 启动监控
        telegram_monitor = monitor.TelegramMonitor(config)
        telegram_monitor.start(telegram_client)

        # 启动定时
        telegram_scheduler = scheduler.TelegramScheduler(config)
        telegram_scheduler.start(telegram_client)
    except Exception as e:
        logger.error(f"❌ Telegram-Tools系统错误: {e}")
        if telegram_client and telegram_client.is_connected():
            telegram_client.disconnect()
        if telegram_scheduler and telegram_scheduler.running:
            telegram_scheduler.shutdown()
        sys.exit(1)
