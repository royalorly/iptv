import yaml
import requests
from pathlib import Path

CONFIG_FILE = "config.yml"
SOURCES_FILE = "sources.txt"
OUTPUT_DIR = Path("output")
OUTPUT_FILE = OUTPUT_DIR / "tv.m3u"


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_sources():
    sources = []

    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            if line.startswith("#"):
                continue

            sources.append(line)

    return sources
    
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

    sources = load_sources()

    print("Sources:")

    for s in sources:
        print(s)

    build_playlist(config)

    print("Playlist generated:")
    print(OUTPUT_FILE)

if __name__ == "__main__":
    main()
