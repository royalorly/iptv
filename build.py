import yaml
import re
import requests
from pathlib import Path

CONFIG_FILE = "config.yml"
CHANNEL_MAP_FILE = "channel_map.yml"
CHANNEL_MAP = {}
SOURCES_FILE = "sources.txt"
OUTPUT_DIR = Path("output")
OUTPUT_FILE = OUTPUT_DIR / "tv.m3u"
SORT_FILE = "sort.yml"
SORT_CONFIG = {}

def load_sort():
    with open(SORT_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_channel_map():
    with open(CHANNEL_MAP_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
        
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

        name = normalize_channel_name(channel["name"]).lower()

        if name in seen:
            continue

        seen.add(name)
        unique.append(channel)

    return unique
        

def filter_channels(channels):

    blacklist = [
        "注意事项",
        "说明",
        "公告",
        "测试",
    ]

    result = []

    for channel in channels:

        name = channel["name"]

        skip = False

        for word in blacklist:
            if word in name:
                skip = True
                break

        if not skip:
            result.append(channel)

    return result


def classify_channel(channel):
    name = channel["name"]

    if name.startswith("CCTV"):
        return "央视"

    if "卫视" in name:
        return "卫视"

    if any(x in name for x in [
        "凤凰", "TVB", "HOY", "翡翠", "明珠", "J2",
        "港台", "澳视", "澳门"
    ]):
        return "港澳"

    if any(x in name for x in [
        "NHK", "CNN", "BBC", "Bloomberg",
        "Discovery", "Animal Planet",
        "National Geographic"
    ]):
        return "国际"

    return channel["group"] if channel["group"] else "其它"



def normalize_channel_name(name):

    name = name.strip()

    # 去掉常见后缀
    remove_words = [
        "HD",
        "FHD",
        "UHD",
        "4K",
        "8K",
        "高清",
        "超清",
        "频道",
        "直播",
    ]

    for word in remove_words:
        name = name.replace(word, "")

    # 去空格
    name = name.replace(" ", "")

    # CCTV 统一格式
    m = re.match(r"(?i)cctv[- ]?(\d+)", name)

    if m:
        name = f"CCTV-{m.group(1)}"

    name = name.strip()

    return CHANNEL_MAP.get(name, name)



def build_playlist(channels):
    OUTPUT_DIR.mkdir(exist_ok=True)

    lines = ["#EXTM3U", ""]

    for channel in channels:

        group = classify_channel(channel)

        extinf = channel["extinf"]
        name = normalize_channel_name(channel["name"])

        # 修改频道名称
        extinf = re.sub(
            r',.*$',
            f',{name}',
            extinf
        )

        # 修改已有的 group-title
        if 'group-title="' in extinf:
            extinf = re.sub(
                r'group-title="[^"]*"',
                f'group-title="{group}"',
                extinf
            )
        else:
            # 如果没有 group-title，则添加
            extinf = extinf.replace(
                "#EXTINF:-1",
                f'#EXTINF:-1 group-title="{group}"'
            )

        lines.append(extinf)
        lines.append(channel["url"])
        lines.append("")

    OUTPUT_FILE.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )


def main():
    global SORT_CONFIG
    SORT_CONFIG = load_sort()
    global CHANNEL_MAP
    CHANNEL_MAP = load_channel_map()
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
    all_channels = filter_channels(all_channels)
    print(f"After dedup: {len(all_channels)}")

    if all_channels:
        print("Sample channel:")
        print(all_channels[0])

    build_playlist(all_channels)

    print("Playlist generated:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
