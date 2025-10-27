import logging
import os

# 日志文件位置
LOG_FILE = "/app/log/console.log"


class Log:
    def __init__(self, level: str):
        # 确保配置目录存在
        log_dir = os.path.dirname(LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 配置日志
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )

        # 关闭 Telethon 的频道更新 INFO 日志，只显示 WARNING 及以上级别
        logging.getLogger("telethon").setLevel(logging.WARNING)
        # 关闭 APScheduler 的 INFO 日志，只显示 WARNING 及以上级别
        logging.getLogger("apscheduler").setLevel(logging.WARNING)
