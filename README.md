# NestTgBot

一个AI写的 Telegram 的人形Bot

## 插件系统

本机器人支持插件扩展，插件位于 `plugins/` 目录中。

## Docker 部署流程

### 1. 配置文件准备

首先，下载配置模板文件并重命名为 `config.yaml`：


然后编辑 `config.yaml` 文件，填入您的 API 凭据：

- `telegram.api_id` 和 `telegram.api_hash`：从 [Telegram](https://my.telegram.org/) 获取
- `user.my_user_id`：您的 Telegram 用户 ID
- `user.my_channel_ids`：您要监控的频道 ID
- `deepseek.api_key`：从 [DeepSeek](https://platform.deepseek.com/) 获取的 API 密钥
- `xai.api_key`：从 [X.AI](https://x.ai/) 获取的 API 密钥

### 2. 使用 Docker 运行（首次登录）

根据您的 CPU 架构选择相应的镜像：

**ARM 架构（如树莓派、M系列芯片）：**
```bash
docker run -it --rm \
  -v ./:/app \
  -v ./config.yaml:/app/config.yaml:ro \
  --name NTBot \
  chen256/nesttgbot:arm python bot.py
```

**x86 架构（Intel/AMD处理器）：**
```bash
docker run -it --rm \
  -v ./:/app \
  -v ./config.yaml:/app/config.yaml:ro \
  --name NTBot \
  chen256/nesttgbot:latest python bot.py
```

运行上述命令后，机器人会启动并尝试登录 Telegram。登录成功后，按 `Ctrl+C` 手动退出。

### 3. 使用 Docker Compose 启动

首次登录成功后，可以使用 `docker-compose` 来启动机器人服务。

根据您的 CPU 架构，需要修改 `docker-compose.yml` 文件中的镜像版本：

**ARM 架构：**
```yaml
version: '3.8'

services:
  nesttgbot:
    image: chen256/nesttgbot:arm
    container_name: nesttgbot
    volumes:
      - ./:/app
      - ./config.yaml:/app/config.yaml:ro
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
```

**x86 架构：**
```yaml
version: '3.8'

services:
  nesttgbot:
    image: chen256/nesttgbot:latest
    container_name: nesttgbot
    volumes:
      - ./:/app
      - ./config.yaml:/app/config.yaml:ro
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
```

启动服务：
```bash
docker-compose up -d
```

查看日志：
```bash
docker-compose logs -f
```


