# NestTgBot

一个基于 Telegram 的多功能机器人，集成了 DeepSeek 和 X.AI 的 API 功能。

## 功能特性

- 基于 Telegram 的机器人交互
- 集成 DeepSeek AI 模型
- 集成 X.AI 模型
- 可扩展的插件系统
- 消息记录功能
- 音乐播放功能
- 其他实用工具

## 安装与配置

### 环境要求

- Python 3.7+
- Telegram API 凭据
- DeepSeek API 密钥
- X.AI API 密钥

### 方法一：传统安装

1. 克隆此仓库：
   ```bash
   git clone https://github.com/4Nest/NestTgBot.git
   cd NestTgBot
   ```

2. 创建虚拟环境并激活：
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

4. 配置机器人：
   - 复制配置模板：`cp config.example.yaml config.yaml`
   - 编辑 `config.yaml` 文件，填入您的 API 凭据

5. 运行机器人：
   ```bash
   python bot.py
   ```

### 方法二：Docker 部署（推荐）

1. 确保已安装 Docker 和 docker-compose：
   ```bash
   # Debian/Ubuntu 系统安装 Docker
   sudo apt update
   sudo apt install docker.io docker-compose
   
   # 启动 Docker 服务
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

2. 克隆此仓库：
   ```bash
   git clone https://github.com/4Nest/NestTgBot.git
   cd NestTgBot
   ```

3. 配置机器人：
   - 复制配置模板：`cp config.example.yaml config.yaml`
   - 编辑 `config.yaml` 文件，填入您的 API 凭据

4. 创建数据目录用于持久化存储 session 文件：
   ```bash
   mkdir -p data
   ```

5. 首次运行（需要交互式输入凭据）：
   ```bash
   # 使用交互式模式运行容器进行首次设置
   docker run -it --rm \
     -v $(pwd)/data:/app/data \
     -v $(pwd)/config.yaml:/app/config.yaml:ro \
     nesttgbot python bot.py
   
   # 按提示输入电话号码或机器人令牌完成认证
   # 认证完成后，按 Ctrl+C 退出
   ```

6. 构建并运行容器：
   ```bash
   docker-compose up -d
   ```

7. 查看日志：
   ```bash
   docker-compose logs -f
   ```

### 配置说明

- `telegram.api_id` 和 `telegram.api_hash`：从 [Telegram](https://my.telegram.org/) 获取
- `user.my_user_id`：您的 Telegram 用户 ID
- `user.my_channel_ids`：您要监控的频道 ID
- `deepseek.api_key`：从 [DeepSeek](https://platform.deepseek.com/) 获取的 API 密钥
- `xai.api_key`：从 [X.AI](https://x.ai/) 获取的 API 密钥

## Session 持久化

为了确保机器人在重启后不需要重新认证，session 文件会被持久化存储在 `data` 目录中。在 Docker 部署中，这个目录会被挂载到容器外部，确保 session 文件在容器重启后仍然存在。

## 插件系统

本机器人支持插件扩展，插件位于 `plugins/` 目录中。
