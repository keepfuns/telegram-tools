import logging
import os
from typing import Dict, Any
import sys
import time

# 导入 ruamel.yaml
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

# 配置文件位置
DATA_PATH = "/app/data/"
CONFIG_FILE = DATA_PATH + "config.yaml"
SESSION_FILE = DATA_PATH + "telegram.session"

# 创建 YAML 实例并配置
yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.width = 4096  # 防止长字符串换行

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器（支持注释）"""

    @staticmethod
    def create_default_config():
        """创建带详细注释的默认配置文件"""
        if not os.path.exists(CONFIG_FILE):
            # 使用 CommentedMap 保持顺序和注释
            default_config = CommentedMap()

            # Telegram 配置
            default_config["telegram"] = CommentedMap(
                [
                    ("api_id", "API_ID"),
                    ("api_hash", "API_HASH"),
                ]
            )
            default_config.yaml_set_comment_before_after_key(
                "telegram", before="Telegram API 配置"
            )
            default_config["telegram"].yaml_set_comment_before_after_key(
                "api_id", before="从 https://my.telegram.org 获取"
            )
            default_config["telegram"].yaml_set_comment_before_after_key(
                "api_hash", before="从 https://my.telegram.org 获取"
            )

            # 代理配置
            default_config["proxy"] = CommentedMap(
                [
                    ("enable", False),
                    ("type", "http"),
                    ("host", "127.0.0.1"),
                    ("port", 1080),
                    ("username", "用户名"),
                    ("password", "密码"),
                ]
            )
            default_config.yaml_set_comment_before_after_key(
                "proxy", before="\n代理配置（可选）"
            )
            default_config["proxy"].yaml_set_comment_before_after_key(
                "enable", before="是否启用代理"
            )
            default_config["proxy"].yaml_set_comment_before_after_key(
                "type", before="代理类型: http, socks4, socks5, mtproto"
            )
            default_config["proxy"].yaml_set_comment_before_after_key(
                "host", before="代理服务器地址"
            )
            default_config["proxy"].yaml_set_comment_before_after_key(
                "port", before="代理端口"
            )
            default_config["proxy"].yaml_set_comment_before_after_key(
                "username", before="代理用户名（可选）"
            )
            default_config["proxy"].yaml_set_comment_before_after_key(
                "password", before="代理密码（可选）"
            )

            # 监控来源配置
            sources = CommentedSeq()
            source_item = CommentedMap(
                [
                    ("enabled", False),
                    ("id", "频道通知"),
                    ("include_keywords", ["重要", "通知"]),
                    ("exclude_keywords", ["广告", "推广"]),
                ]
            )
            sources.append(source_item)
            default_config["sources"] = sources
            default_config.yaml_set_comment_before_after_key(
                "sources", before="\n监控来源配置"
            )

            # 为源频道配置添加详细注释
            source_item.yaml_set_comment_before_after_key(
                "enabled", before="是否启用监控来源"
            )
            source_item.yaml_set_comment_before_after_key(
                "id",
                before="ID/名称/用户名",
            )
            source_item.yaml_set_comment_before_after_key(
                "include_keywords", before="包含关键词（空则接收所有）"
            )
            source_item.yaml_set_comment_before_after_key(
                "exclude_keywords", before="排除关键词（可选）"
            )

            # 转发目标配置
            destinations = CommentedSeq()
            dest_item = CommentedMap(
                [
                    ("enabled", False),
                    ("id", -100529759276),
                ]
            )
            destinations.append(dest_item)
            default_config["destinations"] = destinations
            default_config.yaml_set_comment_before_after_key(
                "destinations", before="\n转发目标配置"
            )

            # 为目标配置添加详细注释
            dest_item.yaml_set_comment_before_after_key(
                "enabled", before="是否启用转发目标"
            )
            dest_item.yaml_set_comment_before_after_key(
                "id",
                before="ID/名称/用户名",
            )

            # 定时任务配置
            schedulers = CommentedSeq()
            sche_item = CommentedMap(
                [
                    ("enabled", False),
                    ("id", "签到机器"),
                    ("cron", "5 0 * * *"),
                    ("message", "签到"),
                ]
            )
            schedulers.append(sche_item)
            default_config["schedulers"] = schedulers
            default_config.yaml_set_comment_before_after_key(
                "schedulers", before="\n定时任务配置"
            )

            # 为定时配置添加详细注释
            sche_item.yaml_set_comment_before_after_key(
                "enabled", before="是否启用定时任务"
            )
            sche_item.yaml_set_comment_before_after_key(
                "id",
                before="ID/名称/用户名",
            )
            sche_item.yaml_set_comment_before_after_key(
                "cron",
                before="指定时间",
            )
            sche_item.yaml_set_comment_before_after_key(
                "message",
                before="发送信息内容",
            )

            # 确保配置目录存在
            config_dir = os.path.dirname(CONFIG_FILE)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)

            # 保存配置文件
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                yaml.dump(default_config, f)

            logger.info(f"📝 已创建带详细注释的默认配置文件: {CONFIG_FILE}")
            logger.warning("🚨  请编辑配置文件后重启")
            sys.exit(0)

    @staticmethod
    def load_config() -> Dict[str, Any]:
        """加载配置文件（保留注释）"""
        if not os.path.exists(CONFIG_FILE):
            logger.error(f"❌ 配置文件不存在: {CONFIG_FILE}")
            sys.exit(1)

        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = yaml.load(f)
            logger.info(f"✅ 配置文件加载成功: {CONFIG_FILE}")
            return config
        except Exception as e:
            logger.error(f"❌ 配置文件加载失败: {e}")
            sys.exit(1)

    @staticmethod
    def save_config(config: Dict[str, Any]):
        """保存配置文件（保留注释和顺序）"""
        try:
            # 确保使用 CommentedMap 类型以保留注释
            if not isinstance(config, (CommentedMap, CommentedSeq)):
                # 转换普通字典为 CommentedMap
                config = ConfigManager.dict_to_commented_map(config)

            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                yaml.dump(config, f)
            logger.info(f"✅ 配置文件保存成功: {CONFIG_FILE}")
        except Exception as e:
            logger.error(f"❌ 配置文件保存失败: {e}")
            raise

    @staticmethod
    def dict_to_commented_map(data):
        """将普通字典转换为 CommentedMap（递归处理）"""
        if isinstance(data, dict):
            result = CommentedMap()
            for key, value in data.items():
                result[key] = ConfigManager.dict_to_commented_map(value)
            return result
        elif isinstance(data, list):
            result = CommentedSeq()
            for item in data:
                result.append(ConfigManager.dict_to_commented_map(item))
            return result
        else:
            return data

    @staticmethod
    def update_config_with_comments(new_config: Dict[str, Any]):
        """更新配置但保留原有注释"""
        try:
            # 先加载现有配置（包含注释）
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    existing_config = yaml.load(f)

                # 合并新配置到现有配置（保留注释结构）
                ConfigManager.merge_configs(existing_config, new_config)
                config_to_save = existing_config
            else:
                config_to_save = ConfigManager.dict_to_commented_map(new_config)

            # 保存配置
            ConfigManager.save_config(config_to_save)

        except Exception as e:
            logger.error(f"❌ 更新配置失败: {e}")
            raise

    @staticmethod
    def merge_configs(existing: CommentedMap, new: dict):
        """递归合并配置"""
        for key, value in new.items():
            if (
                key in existing
                and isinstance(existing[key], (CommentedMap, dict))
                and isinstance(value, dict)
            ):
                ConfigManager.merge_configs(existing[key], value)
            elif (
                key in existing
                and isinstance(existing[key], (CommentedSeq, list))
                and isinstance(value, list)
            ):
                # 对于列表，直接替换但保留注释结构
                existing[key] = ConfigManager.dict_to_commented_map(value)
            else:
                existing[key] = value

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> bool:
        """验证配置文件的必需字段"""
        required_fields = {
            "telegram": ["api_id", "api_hash"],
            "sources": [],
            "destinations": [],
            "schedulers": [],
        }

        for section, fields in required_fields.items():
            if section not in config:
                logger.error(f"❌ 配置缺少必需部分: {section}")
                return False

            for field in fields:
                if field not in config[section]:
                    logger.error(f"❌ 配置 {section} 缺少必需字段: {field}")
                    return False

        api_id = config.get("telegram").get("api_id")
        if not api_id or api_id == "API_ID":
            logger.error("❌ telegram配置中没有可用api_id")
            return False
        api_hash = config.get("telegram").get("api_hash")
        if not api_hash or api_hash == "API_HASH":
            logger.error("❌ telegram配置中没有可用api_hash")
            return False

        # 检查session文件
        if not os.path.exists(SESSION_FILE):
            logger.error(f"❌ Session文件不存在: {SESSION_FILE}")
            logger.warning(
                "🚨 请终端运行 docker exec -it telegram-tools python /app/src/login.py 生成Session文件"
            )
            time.sleep(3600)
            return False

        return True
