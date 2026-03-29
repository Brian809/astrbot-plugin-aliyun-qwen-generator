from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register

from .group_handler import GroupImageHandler
from .image_generator import ImageGenerator
from .llm_handler import LLMImageHandler


@register(
    "astrbot_plugin_aliyun_qwen_generator",
    "Brian809",
    "阿里云通义千问图片生成插件",
    "1.1.0",
)
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self._init_generator()

    def _init_generator(self):
        """初始化图片生成器"""
        api_key = self.context.get_config().get("aliyun_qwen_api_key", "")
        api_url = self.context.get_config().get("aliyun_qwen_api_url", "")

        if not api_key:
            raise ValueError("aliyun_qwen_api_key 未配置")

        self.generator = ImageGenerator(api_key=api_key, api_url=api_url)
        self.group_handler = GroupImageHandler(self.generator)
        self.llm_handler = LLMImageHandler(self.generator)

    async def initialize(self):
        """插件初始化"""
        pass

    async def terminate(self):
        """插件销毁"""
        pass

    @filter.command("image")
    async def image(self, event: AstrMessageEvent):
        """群聊指令：/image <描述>"""
        async for result in self.group_handler.handle(event):
            yield result

    @filter.llm("generate_image")
    async def llm_generate_image(self, event: AstrMessageEvent, description: str = ""):
        """
        LLM 工具：生成图片
        Args:
            description: 图片的详细描述，包括主体、场景、风格、色彩等
        """
        async for result in self.llm_handler.handle(event, description):
            yield result
