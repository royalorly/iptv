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

def download_playlist(url):
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()

        print(f"Downloaded: {url}")

        return r.text

    except Exception as e:
        print(f"Failed: {url}")
        print(e)

        return None

def parse_m3u(content):
    channels = []

    lines = content.splitlines()

    i = 0

    while i < len(lines):

        line = lines[i].strip()

        if line.startswith("#EXTINF"):

            name = line.split(",")[-1].strip()

            if i + 1 < len(lines):

                url = lines[i + 1].strip()

                channels.append({
                    "name": name,
                    "url": url,
                    "extinf": line
                })

                i += 1

        i += 1

    return channels
        
    
def build_playlist(channels):
    OUTPUT_DIR.mkdir(exist_ok=True)

    lines = ["#EXTM3U", ""]

    for channel in channels:
        lines.append(channel["extinf"])
        lines.append(channel["url"])
        lines.append("")

    OUTPUT_FILE.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )


def main():
    config = load_config()

    sources = load_sources()

    all_channels = []

    for url in sources:
        text = download_playlist(url)

        if text:
            channels = parse_m3u(text)

            print(f"{len(channels)} channels")

            all_channels.extend(channels)

    print(f"Total channels: {len(all_channels)}")

    build_playlist(all_channels)

    print("Playlist generated:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
