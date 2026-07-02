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

import re
def parse_m3u(content):
    channels = []

    lines = content.splitlines()

    i = 0

    while i < len(lines):

        line = lines[i].strip()

        if line.startswith("#EXTINF"):

            extinf = line

            name = line.split(",")[-1].strip()

            group = ""
            logo = ""
            tvg_id = ""

            m = re.search(r'group-title="([^"]*)"', extinf)
            if m:
                group = m.group(1)

            m = re.search(r'tvg-logo="([^"]*)"', extinf)
            if m:
                logo = m.group(1)

            m = re.search(r'tvg-id="([^"]*)"', extinf)
            if m:
                tvg_id = m.group(1)

            if i + 1 < len(lines):

                url = lines[i + 1].strip()

                channels.append({
                    "name": name,
                    "url": url,
                    "group": group,
                    "logo": logo,
                    "tvg_id": tvg_id,
                    "extinf": extinf
                })

                i += 1

        i += 1

    return channels

def deduplicate_channels(channels):
    unique = []
    seen = set()

    for channel in channels:
        key = (channel["name"], channel["url"])

        if key not in seen:
            seen.add(key)
            unique.append(channel)

    return unique
        
    
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

    print(f"Before dedup: {len(all_channels)}")

    all_channels = deduplicate_channels(all_channels)

    print(f"After dedup: {len(all_channels)}")

    if all_channels:
        print("Sample channel:")
        print(all_channels[0])

    build_playlist(all_channels)

    print("Playlist generated:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
