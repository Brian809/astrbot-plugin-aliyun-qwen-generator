from astrbot.api import AstrBotConfig
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
    def __init__(self, context: Context, config: AstrBotConfig = None):
        super().__init__(context)
        self.config = config
        self.generator = None
        self.group_handler = None
        self.llm_handler = None

    def _init_generator(self) -> bool:
        """初始化图片生成器，返回是否成功"""
        if self.generator is not None:
            return True

        api_key = self.config.get("aliyun_qwen_api_key", "")
        api_url = self.config.get("aliyun_qwen_api_url", "")

        if not api_key:
            return False

        self.generator = ImageGenerator(api_key=api_key, api_url=api_url)
        self.group_handler = GroupImageHandler(self.generator)
        self.llm_handler = LLMImageHandler(self.generator)
        return True

    async def initialize(self):
        """插件初始化"""
        pass

    async def terminate(self):
        """插件销毁"""
        pass

    @filter.command("image")
    async def image(self, event: AstrMessageEvent):
        """群聊指令：/image <描述>"""
        if not self._init_generator():
            yield event.plain_result("请先配置 aliyun_qwen_api_key")
            return
        async for result in self.group_handler.handle(event):
            yield result

    @filter.llm_tool(name="generate_image")
    async def llm_generate_image(self, event: AstrMessageEvent, description: str):
        '''生成图片。

        根据用户提供的描述生成一张图片。当用户想要生成图片、画图、创作图像时使用此工具。

        Args:
            description(string): 图片的详细描述，包括主体、场景、风格、色彩等。例如："一只可爱的橘猫在草地上晒太阳，卡通风格"
        '''
        if not self._init_generator():
            yield "图片生成服务未配置，请联系管理员配置 aliyun_qwen_api_key"
            return
        async for result in self.llm_handler.handle(event, description):
            yield result
