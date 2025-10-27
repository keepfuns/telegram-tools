from typing import List, Dict, Any
import logging
import sys
from telethon import TelegramClient

DATA_PATH = "/app/data/"
logger = logging.getLogger(__name__)


class ClientManage:
    def __init__(self, config: Dict[str, Any]):
        self.client = None
        self.config = config

    async def init_client(self):
        telegram_config = self.config.get("telegram", {})
        api_id = telegram_config.get("api_id")
        api_hash = telegram_config.get("api_hash")

        # 显示配置信息
        logger.info(f"🔑  API_ID: {api_id}")
        logger.info(f"🔑  API_HASH: {api_hash}")

        try:
            # 创建客户端
            self.client = TelegramClient(
                DATA_PATH + "telegram.session",
                api_id,
                api_hash,
                proxy=self.get_proxy(),
            )
            # 启动客户端
            await self.client.start()
            me = await self.client.get_me()
            logger.info(f"📶  连接成功: @{me.username} (ID: {me.id})")
        except Exception as e:
            logger.error(f"❌  Telegram客户端初始化失败: {e}")
            sys.exit(1)

    def get_proxy(self):
        """获取代理设置 - 支持多种代理类型"""
        proxy_config = self.config.get("proxy", {})
        if not proxy_config.get("enable", False):
            logger.info("🌐  使用代理: 否")
            return None

        proxy_type = proxy_config.get("type", "http").lower()
        host = proxy_config.get("host", "127.0.0.1")
        port = proxy_config.get("port", 1080)
        username = proxy_config.get("username")
        password = proxy_config.get("password")

        # 支持的代理类型
        valid_types = ["http", "socks4", "socks5", "mtproto"]
        if proxy_type not in valid_types:
            logger.warning(f"⚠️  不支持的代理类型: {proxy_type}，使用默认的http代理")
            proxy_type = "http"

        proxy_dict = {
            "proxy_type": proxy_type,
            "addr": host,
            "port": port,
        }

        # 为SOCKS和HTTP代理添加认证信息
        if proxy_type in ["http", "socks4", "socks5"]:
            if username and password:
                proxy_dict["username"] = username
                proxy_dict["password"] = password
        # MTProto代理使用不同的参数名
        elif proxy_type == "mtproto":
            proxy_dict["proxy_type"] = "mtproto"
            if password:  # MTProto使用secret而不是password
                proxy_dict["secret"] = password

        logger.info(f"🌐  使用代理: {proxy_type}")
        logger.info(f"🔌  代理地址: {host}:{port}")
        return proxy_dict

    async def resolve_entities(self, identifiers: List[str]) -> List[Any]:
        """解析实体ID"""
        entities = []

        for identifier in identifiers:
            try:
                # 方法1: 直接解析
                entity = await self.client.get_entity(identifier["id"])
            except (ValueError, TypeError):
                # 方法2: 从对话列表查找
                entity = await self.find_entity_in_dialogs(identifier["id"])

            if entity:
                entity_id = getattr(entity, "id")
                entity_name = getattr(
                    entity, "title", getattr(entity, "first_name", f"实体_{entity_id}")
                )
                identifier["id"] = entity_id
                identifier["name"] = entity_name
                identifier["entity"] = entity
                entities.append(identifier)
                logger.debug(f"✅  解析实体: {entity_name} (ID: {entity_id})")
            else:
                logger.error(f"❌  无法解析实体: {identifier['id']}")

        return entities

    async def find_entity_in_dialogs(self, identifier):
        """在对话列表中查找实体"""
        identifier_str = str(identifier).lower()

        async for dialog in self.client.iter_dialogs():
            entity = dialog.entity

            # 匹配ID
            if hasattr(entity, "id") and str(entity.id) == identifier_str:
                return entity

            # 匹配标题
            if hasattr(entity, "title") and entity.title:
                if entity.title.lower() == identifier_str:
                    return entity

            # 匹配用户名
            if hasattr(entity, "username") and entity.username:
                username = entity.username.lower()
                if username == identifier_str or f"@{username}" == identifier_str:
                    return entity

            # 匹配名称
            if hasattr(entity, "first_name") and entity.first_name:
                if entity.first_name.lower() == identifier_str:
                    return entity

        return None

    async def forward_message(self, event, destinations: List[Any]):
        """转发消息到所有目标"""
        message = event.message
        message_text = message.text or message.raw_text or ""
        media = message.media

        for dest in destinations:
            try:
                # 直接转发原消息（保持原样）
                await self.client.forward_messages(dest["entity"], message)
            except Exception:
                try:
                    if media:
                        # 新建转发消息（不支持按钮）
                        await self.client.send_file(
                            dest["entity"],
                            media,
                            caption=message_text,
                        )
                    else:
                        # 新建转发消息（仅支持文本）
                        await self.client.send_message(
                            dest["entity"],
                            message_text,
                        )
                except Exception as e:
                    logger.error(f"❌  转发消息到 {dest['name']} 失败: {e}")
