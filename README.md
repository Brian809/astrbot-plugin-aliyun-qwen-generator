# astrbot-plugin-aliyun-qwen-generator

基于阿里云通义千问（Qwen）图像生成 API 的 AstrBot 插件，支持群聊指令和 LLM 工具调用两种方式生成图片。

## 功能特性

- 🎨 **高质量图片生成**：基于阿里云 Qwen-Image-2.0-Pro 模型
- 💬 **群聊指令支持**：通过 `/image` 指令在群聊中生成图片
- 🤖 **LLM 工具集成**：支持 AstrBot 的 LLM Function Calling
- ⚡ **异步非阻塞**：使用后台任务，不阻塞 Bot 响应
- 🔧 **可配置参数**：支持自定义 API 地址、图片尺寸等

## 安装方法

### 方式一：通过 AstrBot 插件市场安装
还没上架……
1. ~~打开 AstrBot WebUI~~
2. ~~进入"插件市场"~~
3. ~~搜索 `astrbot-plugin-aliyun-qwen-generator`~~
4. ~~点击安装~~

### 方式二：手动安装

```bash
# 进入 AstrBot 插件目录
cd AstrBot/data/plugins

# 克隆仓库
git clone https://github.com/Brian809/astrbot-plugin-aliyun-qwen-generator.git

# 重启 AstrBot
```

## 配置说明

### 获取阿里云 API Key

1. 访问 [阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/api-key)
2. 创建或获取 API Key
3. 确保账户有通义万相的调用额度

### 插件配置

在 AstrBot WebUI 的插件配置中填写：

| 配置项 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| `aliyun_qwen_api_key` | ✅ | - | 阿里云 DashScope API Key |
| `aliyun_qwen_api_url` | ❌ | `https://dashscope.aliyuncs.com/api/v1` | API 基础地址，根据地域修改 |

## 使用方法

### 群聊指令

在群聊中发送：

```
/image 一只可爱的橘猫在草地上晒太阳，卡通风格
```

Bot 会立即回复"生成中"，然后在后台生成图片后自动发送。

### LLM 工具调用

当 AstrBot 的 LLM 功能开启时，可以直接对 Bot 说：

```
帮我画一只猫
```

LLM 会自动调用图片生成工具。

## 项目结构

```
astrbot-plugin-aliyun-qwen-generator/
├── main.py                 # 插件入口
├── image_generator.py      # 图片生成核心类
├── group_handler.py        # 群聊指令处理器
├── llm_handler.py          # LLM 工具处理器
├── _conf_schema.json       # 配置定义
└── metadata.yaml           # 插件元数据
```

## 技术实现

### 核心类说明

#### `ImageGenerator`

封装阿里云 API 调用：

```python
generator = ImageGenerator(api_key="your-key")
result = await generator.generate("一只可爱的猫")
if result.success:
    print(result.image_url)
```

#### `GroupImageHandler`

处理群聊 `/image` 指令：
- 解析用户输入
- 调用生成器
- 异步发送结果

#### `LLMImageHandler`

处理 LLM 工具调用：
- 接收 LLM 传入的参数
- 返回生成结果

### 异步设计

```
用户发送指令
    ↓
立即返回"生成中"
    ↓
create_task(后台任务)
    ↓
to_thread(同步API调用)
    ↓
生成完成 → 发送图片
```

## 常见问题

### Q: 提示 "aliyun_qwen_api_key 未配置"

A: 在 AstrBot WebUI 的插件配置中填写 API Key。

### Q: 图片生成失败

A: 检查：
1. API Key 是否正确
2. 账户是否有足够额度
3. 网络是否能访问阿里云 API

### Q: 生成速度很慢

A: 图片生成通常需要 5-30 秒，这是正常的。插件已使用异步设计，不会阻塞其他功能。

## 开发计划

- [ ] 支持更多图片尺寸选项
- [ ] 支持图生图功能
- [ ] 支持生成进度显示
- [ ] 支持图片风格预设

## 许可证

MIT License

## 作者

Brian809

## 相关链接

- [AstrBot 文档](https://astrbot.app/)
- [阿里云 DashScope](https://dashscope.console.aliyun.com/)
- [通义万相 API 文档](https://help.aliyun.com/zh/dashscope/developer-reference/tongyi-wanxiang)
