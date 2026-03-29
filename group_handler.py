"""
群聊图片处理器
处理群聊中的 /image 指令
"""

import asyncio

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent

from .image_generator import ImageGenerator


class GroupImageHandler:
    """群聊图片处理器"""

    def __init__(self, image_generator: ImageGenerator):
        """
        初始化群聊处理器
        Args:
            image_generator: 图片生成器实例
        """
        self.generator = image_generator

    async def handle(self, event: AstrMessageEvent) -> None:
        """
        处理群聊指令
        Args:
            event: AstrBot 消息事件
        """
        user_name = event.get_sender_name()
        prompt = event.message_str.replace("/image", "").strip()

        if not prompt:
            yield event.plain_result("请输入图片描述，例如：/image 一只可爱的猫")
            return

        # 发送等待提示
        yield event.plain_result(f"{user_name} 图片生成中，请稍候...")

        # 后台生成图片
        asyncio.create_task(
            self._generate_and_send(event, user_name, prompt)
        )

    async def _generate_and_send(
        self,
        event: AstrMessageEvent,
        user_name: str,
        prompt: str
    ) -> None:
        """
        后台生成图片并发送
        Args:
            event: 消息事件
            user_name: 用户名
            prompt: 图片描述
        """
        try:
            result = await self.generator.generate(prompt)

            if result.success:
                logger.info(f"图片生成成功: {result.image_url}")
                # 发送图片
                await event.send(
                    event.make_result().url_image(result.image_url)
                )
            else:
                error_msg = result.error_message or "未知错误"
                logger.error(f"图片生成失败: {error_msg}")
                await event.send(
                    event.plain_result(f"{user_name} 图片生成失败，请稍后重试")
                )

        except Exception as e:
            logger.error(f"处理图片生成任务时出错: {str(e)}")
            await event.send(
                event.plain_result(f"{user_name} 图片生成出错，请稍后重试")
            )
