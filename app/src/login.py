import asyncio
import os
from telethon import TelegramClient
from telethon.tl.types import User
from ruamel.yaml import YAML

DATA_PATH = "/app/data/"
CONFIG_FILE = DATA_PATH + "config.yaml"
SESSION_FILE = DATA_PATH + "telegram.session"

# 创建 YAML 实例并配置
yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.width = 4096  # 防止长字符串换行


def load_config():
    """加载配置"""
    if not os.path.exists(CONFIG_FILE):
        print("❌ 配置文件不存在，请先运行主程序生成默认配置")
        return None

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return yaml.load(f)
    except Exception as e:
        print(f"❌ 加载配置文件失败: {e}")
        return None


def get_proxy(proxy_config):
    """获取代理设置 - 支持多种代理类型"""
    if not proxy_config.get("enable", False):
        return None

    proxy_type = proxy_config.get("type", "http").lower()
    host = proxy_config.get("host", "127.0.0.1")
    port = proxy_config.get("port", 1080)
    username = proxy_config.get("username")
    password = proxy_config.get("password")

    # 支持的代理类型
    valid_types = ["http", "socks4", "socks5", "mtproto"]
    if proxy_type not in valid_types:
        proxy_type = "http"

    proxy_dict = {
        "proxy_type": proxy_type,
        "addr": host,
        "port": port,
    }

    # 为SOCKS和HTTP代理添加认证信息
    if proxy_type in ["http", "socks4", "socks5"]:
        if username and password:
            proxy_dict["username"] = username
            proxy_dict["password"] = password
    # MTProto代理使用不同的参数名
    elif proxy_type == "mtproto":
        proxy_dict["proxy_type"] = "mtproto"
        if password:  # MTProto使用secret而不是password
            proxy_dict["secret"] = password

    return proxy_dict


async def generate_session_file():
    """生成.session文件"""

    print("=" * 50)
    print("🧰 Telegram Session文件生成工具 🧰")
    print("=" * 50)

    # 加载配置
    config = load_config()
    if not config:
        return

    telegram_config = config.get("telegram", {})
    api_id = telegram_config.get("api_id", "")
    api_hash = telegram_config.get("api_hash", "")

    # 如果API配置为空，提示用户输入
    if not api_id or api_id == "api_id":
        api_id = input("请输入API ID: ").strip()

    if not api_hash or api_hash == "api_hash":
        api_hash = input("请输入API Hash: ").strip()

    if not api_id or not api_hash:
        print("❌ 错误: API ID和API Hash不能为空")
        return

    try:
        api_id = int(api_id)
    except ValueError:
        print("❌ 错误: API ID必须是数字")
        return

    print(f"\n📁 Session文件将保存为: {SESSION_FILE}")

    # 创建客户端
    client = TelegramClient(
        SESSION_FILE.replace(".session", ""),
        api_id,
        api_hash,
        proxy=get_proxy(config.get("proxy")),
    )

    try:
        print("\n🔄 正在连接Telegram...")
        await client.start()

        # 获取用户信息
        me = await client.get_me()
        if isinstance(me, User):
            print("\n📶 登录成功!")
            print(f"   用户ID: {me.id}")
            print(
                f"   用户名: @{me.username}"
                if me.username
                else f"   姓名: {me.first_name}"
            )

        # 检查session文件是否生成
        if os.path.exists(SESSION_FILE):
            print(f"\n📁 Session文件已生成: {SESSION_FILE}")
            print("\n🚨  重要提示:")
            print("   - 请妥善保管.session文件，不要分享给他人")
            print("   - 此文件具有账户的完全访问权限")
        else:
            print(f"\n❌ Session文件生成失败: {SESSION_FILE}")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
    finally:
        await client.disconnect()


def main():
    """主函数"""
    try:
        asyncio.run(generate_session_file())
    except KeyboardInterrupt:
        print("\n\n↘️ 用户取消操作")
    except Exception as e:
        print(f"❌ 程序运行出错: {e}")


if __name__ == "__main__":
    main()
