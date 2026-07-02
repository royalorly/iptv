import yaml
from pathlib import Path

CONFIG_FILE = "config.yml"


def load_config():
    """读取配置文件"""
    config_path = Path(CONFIG_FILE)

    if not config_path.exists():
        raise FileNotFoundError(f"找不到配置文件：{CONFIG_FILE}")

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    print("=" * 50)
    print("Royal IPTV Builder")
    print("=" * 50)

    config = load_config()

    print("\n国家：")
    for country in config.get("countries", []):
        print(f"  - {country}")

    print("\n分类：")
    for category in config.get("categories", []):
        print(f"  - {category}")

    print("\n收藏频道：")
    for channel in config.get("favorites", []):
        print(f"  - {channel}")

    print("\n配置读取成功！")


if __name__ == "__main__":
    main()
