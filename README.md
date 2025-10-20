## 简介
   Telegram消息转发工具

## 运行步骤
1. **获取Telegram API凭证**：
   - 访问 my.telegram.org
   - 登录你的 Telegram 账号
   - 进入 "API Development Tools"
   - 创建新的应用程序，获取 `api_id` 和 `api_hash`

2. **Docker运行**：
   ```bash
   docker run -d \
      --name telegram-message-forward \
      --network bridge \
      -e TZ=Asia/Shanghai \
      -v <your_path>/data:/app/data \
      -v <your_path>/log:/app/log \
      --restart always \
      keepfuns/telegram-message-forward:latest
   ```
   这会在 `data` 目录生成 `config.yaml` 文件。

3. **编辑配置文件**：
   编辑 `config.yaml` 文件，配置您的源频道和目标机器人，支持多源和多目标：
   ```yaml
   telegram:
      api_id: api_id # 从 my.telegram.org 获取
      api_hash: api_hash # 从 my.telegram.org 获取
      username: telegram # 监控账号用户名

   proxy:
      enable: true # 是否启用代理
      type: http  # 代理类型: http, socks4, socks5, mtproto
      host: 127.0.0.1 # 代理服务器地址
      port: 1080 # 代理端口
      username: 代理用户名 # 代理用户名（可选）
      password: 代理密码 # 代理密码（可选）

   sources:
      - 
         enabled: true # 是否启用监控
         id: 频道通知 # ID/名称/用户名
         include_keywords: # 包含关键词（空则接收所有）
            - 重要
            - 通知
         exclude_keywords: # 排除关键词（可选）
            - 广告
            - 推广
      - 
         enabled: true # 是否启用监控
         id: mybot # ID/名称/用户名
         include_keywords: # 包含关键词（空则接收所有）
            - 重要
            - 通知
         exclude_keywords: # 排除关键词（可选）
            - 广告
            - 推广

   destinations:
      - 
         enabled: true # 是否启用转发
         id: -100529759276 # ID/名称/用户名
      - 
         enabled: true # 是否启用转发
         id: yonghuming # ID/名称/用户名
   ```

3. **重启**：
   ```bash
   docker restart telegram-message-forward
   ```

4. **生成Session文件**：
   - Telegram认证，需输入`手机号`、`验证码`
   - 其中`手机号`需要带`+`号，如`+86`
   ```bash
   docker exec -it telegram-message-forward python /app/src/login.py
   ```

5. **重启**：
   ```bash
   docker restart telegram-message-forward
   ```

## 主要特点
1. **多源多目标支持**：可以同时监控多个频道/机器人/用户，并转发到多个频道/机器人/用户
2. **灵活配置**：配置ID、名称、用户名等任一皆可匹配到频道、群组、机器、用户
3. **灵活的过滤规则**：每个源可以设置独立的包含和排除关键词
4. **原文转发**：消息保持原文转发，包括文本、图片、媒体、链接、按钮等

## 免责声明
- 本项目完全免费，仅限个人学习、研究和非商业用途
- 本项目开发者不对因使用本项目而可能导致的任何直接或间接后果负责

## 赞赏
- 如果您欣赏本项目，欢迎为它点亮一颗⭐️
- 如果本项目对您有帮助，不妨请我喝杯咖啡
<br/><br/>
<span><img src="assets/zhifubao.png" alt="支付宝" width="20%" align="left">
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<img src="assets/weixin.png" alt="微信 " width="20%" align="left"></span>
