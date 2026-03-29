"""
图片生成器基类
封装阿里云通义千问图片生成的核心功能
"""

import asyncio
import json
from dataclasses import dataclass
from typing import Any

import dashscope
from astrbot.api import logger
from dashscope import MultiModalConversation


@dataclass
class ImageGenResult:
    """图片生成结果"""
    success: bool
    image_url: str | None = None
    prompt: str | None = None
    error_message: str | None = None
    raw_response: dict | None = None


class ImageGenerator:
    """图片生成器基类"""

    DEFAULT_API_URL = "https://dashscope.aliyuncs.com/api/v1"
    DEFAULT_SIZE = "2048*2048"
    DEFAULT_MODEL = "qwen-image-2.0-pro"

    def __init__(self, api_key: str, api_url: str | None = None):
        """
        初始化图片生成器
        Args:
            api_key: 阿里云 DashScope API Key
            api_url: API 基础 URL，默认使用官方地址
        """
        self.api_key = api_key
        self.api_url = api_url or self.DEFAULT_API_URL

        if not self.api_key:
            raise ValueError("API Key 不能为空")

    async def generate(
        self,
        prompt: str,
        size: str = DEFAULT_SIZE,
        negative_prompt: str | None = None,
        watermark: bool = False,
        prompt_extend: bool = True
    ) -> ImageGenResult:
        """
        异步生成图片
        Args:
            prompt: 图片描述
            size: 图片尺寸，默认 2048*2048
            negative_prompt: 负面提示词
            watermark: 是否添加水印
            prompt_extend: 是否自动扩展提示词
        Returns:
            ImageGenResult: 生成结果
        """
        try:
            # 使用 to_thread 将同步调用转为异步
            response_json = await asyncio.to_thread(
                self._generate_sync,
                prompt=prompt,
                size=size,
                negative_prompt=negative_prompt,
                watermark=watermark,
                prompt_extend=prompt_extend
            )

            response_dict = json.loads(response_json)

            # 提取图片 URL
            image_url = response_dict["choices"][0]["message"]["content"][0]["image"]

            return ImageGenResult(
                success=True,
                image_url=image_url,
                prompt=prompt,
                raw_response=response_dict
            )

        except Exception as e:
            logger.error(f"图片生成失败: {str(e)}")
            return ImageGenResult(
                success=False,
                error_message=str(e),
                prompt=prompt
            )

    def _generate_sync(
        self,
        prompt: str,
        size: str,
        negative_prompt: str | None,
        watermark: bool,
        prompt_extend: bool
    ) -> str:
        """
        同步生成图片（内部方法）

        Returns:
            JSON 字符串格式的响应
        """
        messages = [
            {
                "role": "user",
                "content": [
                    {"text": prompt}
                ]
            }
        ]

        dashscope.base_http_api_url = self.api_url

        # 默认负面提示词
        if negative_prompt is None:
            negative_prompt = (
                "低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，"
                "蜡像感，人脸无细节，过度光滑，画面具有AI感。构图混乱。文字模糊，扭曲。"
            )

        response: Any = MultiModalConversation.call(
            api_key=self.api_key,
            model=self.DEFAULT_MODEL,
            messages=messages,
            result_format="message",
            stream=False,
            watermark=watermark,
            prompt_extend=prompt_extend,
            negative_prompt=negative_prompt,
            size=size
        )

        if response.status_code == 200:
            return json.dumps(response.output, ensure_ascii=False)
        else:
            logger.error(f"HTTP返回码：{response.status_code}")
            logger.error(f"错误码：{response.code}")
            logger.error(f"错误信息：{response.message}")
            raise RuntimeError(f"API 错误: {response.message}")
