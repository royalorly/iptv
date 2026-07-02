import yaml
from pathlib import Path

CONFIG_FILE = "config.yml"
OUTPUT_DIR = Path("output")
OUTPUT_FILE = OUTPUT_DIR / "tv.m3u"


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_playlist(config):
    OUTPUT_DIR.mkdir(exist_ok=True)

    lines = [
        "#EXTM3U",
        "",
        "# Royal IPTV",
        "",
    ]

    for name in config.get("favorites", []):
        lines.append(f'#EXTINF:-1 group-title="Favorites",{name}')
        lines.append("https://example.com/live.m3u8")
        lines.append("")

    OUTPUT_FILE.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )


def main():
    config = load_config()
    build_playlist(config)
    print("Playlist generated:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
