import asyncio
import json
from typing import Any

import dashscope
from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register
from dashscope import MultiModalConversation


@register("astrbot_plugin_aliyun_qwen_generator", "Brian809", "阿里云通义千问图片生成插件", "1.1.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""

    # 注册指令的装饰器。指令名为 image。注册成功后，发送 `/image` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("image")
    async def image(self, event: AstrMessageEvent):
        """这是一个 image 指令""" # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        user_name = event.get_sender_name()
        message_str = event.message_str # 用户发的纯文本消息字符串
        message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        logger.info(message_chain)
        try:
            image_api_response = await asyncio.to_thread(self._get_image_api_response_sync, message_str)

            # 处理成功响应
            # 解析JSON字符串为字典
            response_dict = json.loads(image_api_response)
            image_url = response_dict["output"]["choices"][0]["message"]["content"][0]["image"]
            logger.info(image_url)
            yield event.make_result().url_image(image_url)

        except Exception as e:
            logger.error(f"图片生成失败: {str(e)}")
            yield event.plain_result(f"{user_name} 对不起！图片生成失败，请稍后重试")

        yield event.plain_result("图片生成中...") # 发送一条纯文本消息

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""

    def _get_image_api_response_sync(self, prompt: str, size: str = "2048*2048") -> str:
        """获取图片API响应

        服务端的响应格式：
        ```json
        {
            "status_code": 200,
            "request_id": "d2d1a8c0-325f-9b9d-8b90-xxxxxx",
            "code": "",
            "message": "",
            "output": {
                "text": null,
                "finish_reason": null,
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {
                            "role": "assistant",
                            "content": [
                                {
                                    "image": "https://dashscope-result-wlcb.oss-cn-wulanchabu.aliyuncs.com/xxx.png?Expires=xxx"
                                }
                            ]
                        }
                    }
                ]
            },
            "usage": {
                "input_tokens": 0,
                "output_tokens": 0,
                "width": 2048,
                "image_count": 1,
                "height": 2048
            }
        }
        ```
        """
        messages = [
            {
                "role": "user",
                "content": [
                    {"text": f"{prompt}"}
                ]
            }
        ]

        dashscope.base_http_api_url = self.context.get_config().get("aliyun_qwen_api_url", "")
        api_key = self.context.get_config().get("aliyun_qwen_api_key", "")
        if not dashscope.base_http_api_url:
            dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"

        if not api_key:
            logger.error("aliyun_qwen_api_key is not set in config.yaml")
            raise RuntimeError("aliyun_qwen_api_key is not set!")

        response: Any = MultiModalConversation.call(
            api_key=api_key,
            model="qwen-image-2.0-pro",
            messages=messages,
            result_format="message",
            stream=False,
            watermark=False,
            prompt_extend=True,
            negative_prompt="低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感，人脸无细节，过度光滑，画面具有AI感。构图混乱。文字模糊，扭曲。",
            size=f"{size}"
        )
        if response.status_code == 200:
            return json.dumps(response.output, ensure_ascii=False)
        else:
            logger.error(f"HTTP返回码：{response.status_code}")
            logger.error(f"错误码：{response.code}")
            logger.error(f"错误信息：{response.message}")
            logger.error("请参考文档：https://help.aliyun.com/zh/model-studio/developer-reference/error-code")
            raise RuntimeError(f"Error: {response.message}")
