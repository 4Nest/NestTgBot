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

4. 构建并运行容器：
   ```bash
   docker-compose up -d
   ```

5. 查看日志：
   ```bash
   docker-compose logs -f
   ```

### 配置说明

- `telegram.api_id` 和 `telegram.api_hash`：从 [Telegram](https://my.telegram.org/) 获取
- `user.my_user_id`：您的 Telegram 用户 ID
- `user.my_channel_ids`：您要监控的频道 ID
- `deepseek.api_key`：从 [DeepSeek](https://platform.deepseek.com/) 获取的 API 密钥
- `xai.api_key`：从 [X.AI](https://x.ai/) 获取的 API 密钥

## 插件系统

本机器人支持插件扩展，插件位于 `plugins/` 目录中。
