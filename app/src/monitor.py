from telethon import events
import logging
from typing import Dict, Any
from . import client

logger = logging.getLogger(__name__)


class TelegramMonitor:
    """Telegram监控器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    async def start_monitor(self, client_manage: client.ClientManage):
        """开始监控"""
        # 检查是否有启用的源和目标
        enabled_sources = [
            s for s in self.config.get("sources", []) if s.get("enabled", False)
        ]
        enabled_destinations = [
            d for d in self.config.get("destinations", []) if d.get("enabled", False)
        ]
        if not enabled_sources and not enabled_destinations:
            logger.warning("⚠️ 没有启用的来源和目标，关闭转发功能")
            return

        # 获取源实体
        sources = self.config.get("sources", [])
        enabled_sources = [s for s in sources if s.get("enabled", False)]
        logger.info(f"📡 来源数量: {len(enabled_sources)}/{len(sources)}")
        source_entities = await client_manage.resolve_entities(enabled_sources)
        valid_sources = [s for s in source_entities if s["entity"] is not None]

        if not valid_sources:
            logger.error("❌ 没有有效来源实体，转发功能无法启动")
            return

        # 显示监控配置
        logger.info(f"📡 开始监控 {len(valid_sources)} 个来源")
        for source in valid_sources:
            source_config = next(
                (s for s in enabled_sources if s["id"] == source["id"]), {}
            )
            include_keywords = source_config.get("include_keywords", [])
            exclude_keywords = source_config.get("exclude_keywords", [])
            logger.info(
                f"   - {source['name']} (ID: {source['id']}, 包含: {include_keywords}, 排除: {exclude_keywords})"
            )

        # 获取目标实体
        destinations = self.config.get("destinations", [])
        enabled_destinations = [d for d in destinations if d.get("enabled", False)]
        logger.info(f"🎯 目标数量: {len(enabled_destinations)}/{len(destinations)}")
        destination_entities = await client_manage.resolve_entities(
            enabled_destinations
        )
        valid_destinations = [
            s for s in destination_entities if s["entity"] is not None
        ]

        if not valid_destinations:
            logger.error("❌ 没有有效的目标实体，转发功能无法启动")
            return

        # 显示目标配置
        logger.info(f"🎯 开始转发 {len(valid_destinations)} 个目标")
        for dest in valid_destinations:
            logger.info(f"   - {dest['name']} (ID: {dest['id']})")

        # 创建消息处理器
        client = client_manage.client

        @client.on(events.NewMessage(chats=[s["entity"] for s in valid_sources]))
        async def handler(event):
            try:
                # 获取消息信息
                chat = await event.get_chat()
                source_id = chat.id
                source_name = getattr(
                    chat, "title", getattr(chat, "username", f"源_{source_id}")
                )
                message_text = event.message.text or event.message.raw_text or ""

                # 记录消息信息
                logger.debug(f"收到消息 [{source_name}]: \n{message_text}")

                # 查找对应的源配置
                source_config = next(
                    (s for s in enabled_sources if s["id"] == source_id),
                    {},
                )
                if not source_config:
                    logger.warning(f"收到未知源的消息: {source_name} (ID: {source_id})")
                    return

                # 应用关键词过滤（只对文本内容过滤）
                if self.message_filter(message_text, source_config):
                    logger.info(f"🎯 [{source_name}] 匹配到消息: \n{message_text}")

                    # 转发消息到所有目标
                    await client_manage.client.forward_message(
                        event, valid_destinations
                    )
                else:
                    logger.debug(f"[{source_name}] 消息不匹配关键词")

            except Exception as e:
                logger.error(f"处理消息时出错: {e}")

        logger.info("✅ 实时监控已启动，等待新消息...")

    def message_filter(self, text: str, source_config: Dict[str, Any]) -> bool:
        """消息过滤"""
        if not text:
            return False

        include_keywords = source_config.get("include_keywords", [])
        exclude_keywords = source_config.get("exclude_keywords", [])

        # 如果没有设置包含关键词，则默认所有消息都满足包含条件
        include_condition = (
            any(keyword.lower() in text.lower() for keyword in include_keywords)
            if include_keywords
            else True
        )
        # 如果没有设置排除关键词，则默认所有消息都满足排除条件
        exclude_condition = (
            not any(keyword.lower() in text.lower() for keyword in exclude_keywords)
            if exclude_keywords
            else True
        )

        return include_condition and exclude_condition
