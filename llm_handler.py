"""
LLM 图片处理器
处理 LLM 工具调用
"""

from collections.abc import AsyncGenerator

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent

from .image_generator import ImageGenerator


class LLMImageHandler:
    """LLM 图片处理器"""

    def __init__(self, image_generator: ImageGenerator):
        """
        初始化 LLM 处理器
        Args:
            image_generator: 图片生成器实例
        """
        self.generator = image_generator

    async def handle(
        self, event: AstrMessageEvent, description: str
    ) -> AsyncGenerator[str, None]:
        """
        处理 LLM 工具调用

        Args:
            event: AstrBot 消息事件
            description: LLM 传入的图片描述

        Yields:
            生成进度和结果信息
        """
        if not description:
            yield "请提供图片描述"
            return

        # 发送开始生成消息
        yield f"正在生成图片：{description[:50]}..."

        try:
            result = await self.generator.generate(description)

            if result.success:
                logger.info(f"LLM 图片生成成功: {result.image_url}")
                # 发送图片
                await event.send(event.make_result().url_image(result.image_url))
                yield f"图片已生成：{result.image_url}"
            else:
                error_msg = result.error_message or "未知错误"
                logger.error(f"LLM 图片生成失败: {error_msg}")
                yield f"图片生成失败：{error_msg}"

        except Exception as e:
            logger.error(f"LLM 处理图片生成任务时出错: {str(e)}")
            yield f"图片生成出错：{str(e)}"
