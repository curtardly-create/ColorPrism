import os
import re
import json
import time
import random
import hashlib
import requests
from datetime import datetime, timedelta

OUTPUT_BASE = "D:/tmp/sample-gallery-v2"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# Each theme: keywords for Unsplash search + expected photo descriptions
THEMES = {
    "family_summer": {
        "search_queries": [
            "family-park-sunset",
            "children-playing-outdoor",
            "parents-child-beach",
            "family-picnic-grass",
            "kids-running-happy",
            "father-daughter-park",
            "mother-son-summer",
            "family-walking-sunset",
            "children-bubble-blowing",
            "family-camping-tent",
        ],
        "description": "亲子、家庭、公园、日落、户外活动",
        "base_date": "2024-06-01T17:00:00+08:00",
        "location": {"lat": 22.527, "lng": 113.943, "city": "深圳", "poi": "深圳湾公园"},
        "scene_tags": ["park", "sunset", "family", "outdoor", "children"],
        "actions": ["running", "smiling", "playing", "walking", "hugging"],
        "emotions": ["happy", "warm", "joyful"],
    },
    "city_trip": {
        "search_queries": [
            "tourist-landmark-selfie",
            "traveler-backpack-city",
            "street-food-market-people",
            "couple-travel-photo",
            "friends-road-trip",
            "woman-solo-travel-city",
            "hiker-mountain-view",
            "tourist-old-town",
            "traveler-beach-tropical",
            "friends-vacation-group",
        ],
        "description": "旅行、交通、景点、美食、人物",
        "base_date": "2024-08-15T09:00:00+08:00",
        "location": {"lat": 31.230, "lng": 121.474, "city": "上海", "poi": "外滩"},
        "scene_tags": ["travel", "city", "landmark", "street", "adventure"],
        "actions": ["walking", "exploring", "photographing", "eating", "hiking"],
        "emotions": ["excited", "curious", "adventurous"],
    },
    "graduation_party": {
        "search_queries": [
            "graduation-ceremony-cap-gown",
            "friends-celebration-toast",
            "birthday-party-cake-candles",
            "group-friends-happy-celebration",
            "party-decoration-balloon-people",
            "confetti-celebration-friends",
            "restaurant-dinner-friends-toast",
            "champagne-toast-celebration",
            "friends-dancing-party",
            "graduation-photo-family",
        ],
        "description": "毕业、舞台、朋友合照、聚餐、庆祝",
        "base_date": "2024-07-01T18:00:00+08:00",
        "location": {"lat": 30.573, "lng": 104.067, "city": "成都", "poi": "四川大学"},
        "scene_tags": ["party", "celebration", "graduation", "friends", "indoor"],
        "actions": ["toasting", "dancing", "smiling", "hugging", "cheering"],
        "emotions": ["joyful", "excited", "nostalgic"],
    },
}


def search_unsplash_photos(query, count=5):
    """Scrape Unsplash search results to get photo IDs"""
    url = f"https://unsplash.com/s/photos/{query}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            print(f"    HTTP {resp.status_code} for {query}")
            return []

        # Extract photo IDs from the page
        # Unsplash uses patterns like /photos/XXXXXXXXXXXX
        photo_ids = re.findall(r'/photos/([a-zA-Z0-9_-]{8,})', resp.text)
        # Deduplicate while preserving order
        seen = set()
        unique = []
        for pid in photo_ids:
            if pid not in seen:
                seen.add(pid)
                unique.append(pid)

        return unique[:count]
    except Exception as e:
        print(f"    Error searching {query}: {e}")
        return []


def download_unsplash_photo(photo_id, filepath, width=1200):
    """Download a specific Unsplash photo by ID"""
    url = f"https://images.unsplash.com/photo-{photo_id}?w={width}&q=80&auto=format"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code == 200 and len(resp.content) > 10000:
            with open(filepath, "wb") as f:
                f.write(resp.content)
            return len(resp.content)
    except Exception as e:
        print(f"    Download error: {e}")
    return 0


def download_from_pexels_fallback(query, filepath, count=1):
    """Fallback: use Pexels CDN with search-based seeds"""
    seed = hashlib.md5(query.encode()).hexdigest()[:10]
    url = f"https://images.pexels.com/photos/{seed}/pexels-photo-{seed}.jpeg?auto=compress&cs=tinysrgb&w=1200"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        if resp.status_code == 200 and len(resp.content) > 10000:
            with open(filepath, "wb") as f:
                f.write(resp.content)
            return len(resp.content)
    except:
        pass
    return 0


def try_direct_people_urls(theme_name, query_idx, filepath):
    """Try known working Unsplash photo URLs with people"""
    # Curated Unsplash photo URLs known to contain people
    # Format: direct image URLs from Unsplash CDN
    people_photos = {
        "family_summer": [
            "https://images.unsplash.com/photo-1475503572774-15a45e5d60b9?w=1200&q=80",  # family park
            "https://images.unsplash.com/photo-1476703993599-0035a21b17a9?w=1200&q=80",  # family sunset
            "https://images.unsplash.com/photo-1502086223501-7ea6ecd79368?w=1200&q=80",  # child playing
            "https://images.unsplash.com/photo-1471341971476-ae15ff5dd4ea?w=1200&q=80",  # family outdoor
            "https://images.unsplash.com/photo-1484820540004-14229fe36ca4?w=1200&q=80",  # family walking
            "https://images.unsplash.com/photo-1504439904031-93ded9f94e4e?w=1200&q=80",  # kids playing
            "https://images.unsplash.com/photo-1516733725897-1aa7646-0e4e?w=1200&q=80",  # parent child
            "https://images.unsplash.com/photo-1491013516836-7db643ee1256?w=1200&q=80",  # father daughter
            "https://images.unsplash.com/photo-1504175970294-503faf4bf0a8?w=1200&q=80",  # family beach
            "https://images.unsplash.com/photo-1515067286836-b54441a4565f?w=1200&q=80",  # family camping
            "https://images.unsplash.com/photo-1530089711-2634-4b49-8f73-d0e29b666a78?w=1200&q=80", # kids running
            "https://images.unsplash.com/photo-1518831959646-742c3a6e6893?w=1200&q=80",  # family picnic
            "https://images.unsplash.com/photo-1523438885200-e635ba2c371e?w=1200&q=80",  # mother child
            "https://images.unsplash.com/photo-1519689680058-324335c77eba?w=1200&q=80",  # parents children
            "https://images.unsplash.com/photo-1543854589-fdd815f176e0?w=1200&q=80",  # child outdoor
            "https://images.unsplash.com/photo-1504473032632-81f37a60de6e?w=1200&q=80",  # child happy
            "https://images.unsplash.com/photo-1471341971476-ae15ff5dd4ea?w=1200&q=80",  # family summer
            "https://images.unsplash.com/photo-1494894194458-0174142560c3?w=1200&q=80",  # family outdoor
            "https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?w=1200&q=80",  # child smiling
            "https://images.unsplash.com/photo-1516733725897-1aa76e56385a?w=1200&q=80",  # parent child park
        ],
        "city_trip": [
            "https://images.unsplash.com/photo-1501554728187-ce583db33af7?w=1200&q=80",  # tourist landmark
            "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=1200&q=80",  # traveler backpack
            "https://images.unsplash.com/photo-1527631746610-bca00a040d60?w=1200&q=80",  # street food people
            "https://images.unsplash.com/photo-1506929562872-bb421503ef21?w=1200&q=80",  # couple travel
            "https://images.unsplash.com/photo-1530789253380-cc9028f00d4b?w=1200&q=80",  # friends road trip
            "https://images.unsplash.com/photo-1504150558240-0b4285ad9e26?w=1200&q=80",  # woman travel
            "https://images.unsplash.com/photo-1551632811-561732d1e306?w=1200&q=80",  # hiker mountain
            "https://images.unsplash.com/photo-1467269204594-9661ca13455b?w=1200&q=80",  # tourist old town
            "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200&q=80",  # beach people
            "https://images.unsplash.com/photo-1539635278303-d4002c07eae3?w=1200&q=80",  # friends vacation
            "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=1200&q=80",  # travel adventure
            "https://images.unsplash.com/photo-1503220317375-aaad61436b1b?w=1200&q=80",  # traveler city
            "https://images.unsplash.com/photo-1500835556837-99ac7563d553?w=1200&q=80",  # tourist photo
            "https://images.unsplash.com/photo-1504609773096-104ff2c73ba4?w=1200&q=80",  # travel couple
            "https://images.unsplash.com/photo-1542273917363-3b1817f69a2d?w=1200&q=80",  # traveler adventure
            "https://images.unsplash.com/photo-1526481280693-3bfa7568e0f3?w=1200&q=80",  # street market
            "https://images.unsplash.com/photo-1500259783852-0ca9ce8a64dc?w=1200&q=80",  # travel friends
            "https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=1200&q=80",  # scenic traveler
            "https://images.unsplash.com/photo-1523742064082-5ed633019864?w=1200&q=80",  # city exploration
            "https://images.unsplash.com/photo-1517760444937-f6397edc215e?w=1200&q=80",  # travel adventure
        ],
        "graduation_party": [
            "https://images.unsplash.com/photo-1523059623039-a9ed027e7fad?w=1200&q=80",  # graduation ceremony
            "https://images.unsplash.com/photo-1529156069898-49953e3a716c?w=1200&q=80",  # friends celebration
            "https://images.unsplash.com/photo-1530103862676-de8c9debad1d?w=1200&q=80",  # birthday cake
            "https://images.unsplash.com/photo-1523580494863-6f3031224c94?w=1200&q=80",  # graduation happy
            "https://images.unsplash.com/photo-1496843916299-5dead52e8e1c?w=1200&q=80",  # party celebration
            "https://images.unsplash.com/photo-1513151233558-d860c5398176?w=1200&q=80",  # confetti party
            "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&q=80",  # restaurant dinner
            "https://images.unsplash.com/photo-1573140401552-3fab0b46081c?w=1200&q=80",  # champagne toast
            "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=1200&q=80",  # party people
            "https://images.unsplash.com/photo-1544928147-79a2dbc1f389?w=1200&q=80",  # celebration group
            "https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?w=1200&q=80",  # party dancing
            "https://images.unsplash.com/photo-1519671482749-fd09be7ccebf?w=1200&q=80",  # celebration toast
            "https://images.unsplash.com/photo-1504593811423-6dd665756598?w=1200&q=80",  # friends gathering
            "https://images.unsplash.com/photo-1528605248644-14dd04022da1?w=1200&q=80",  # dinner friends
            "https://images.unsplash.com/photo-1527529482837-4698179dc6ce?w=1200&q=80",  # celebration happy
            "https://images.unsplash.com/photo-1509099836639-18ba1795216d?w=1200&q=80",  # party fun
            "https://images.unsplash.com/photo-1478147427282-58a87a120781?w=1200&q=80",  # dinner gathering
            "https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=1200&q=80",  # party crowd
            "https://images.unsplash.com/photo-1551749987-2106c811aaa2?w=1200&q=80",  # friends cheers
            "https://images.unsplash.com/photo-1511632765486-a01980e01a18?w=1200&q=80",  # family celebration
        ],
    }

    urls = people_photos.get(theme_name, [])
    if query_idx < len(urls):
        url = urls[query_idx]
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            if resp.status_code == 200 and len(resp.content) > 10000:
                with open(filepath, "wb") as f:
                    f.write(resp.content)
                return len(resp.content)
        except:
            pass
    return 0


def download_theme(theme_name, config):
    """Download images for a single theme"""
    theme_dir = os.path.join(OUTPUT_BASE, theme_name)
    os.makedirs(theme_dir, exist_ok=True)

    queries = config["search_queries"]
    total = len(queries) * 2  # 2 images per query
    downloaded = 0

    print(f"\n{'='*50}")
    print(f"Theme: {theme_name}")
    print(f"Description: {config['description']}")
    print(f"Target: {total} images")
    print(f"{'='*50}")

    for q_idx, query in enumerate(queries):
        for img_idx in range(2):
            if downloaded >= total:
                break

            filename = f"{theme_name}_{downloaded+1:03d}.jpg"
            filepath = os.path.join(theme_dir, filename)

            # Strategy 1: Try curated people photo URLs
            size = try_direct_people_urls(theme_name, q_idx * 2 + img_idx, filepath)

            if size == 0:
                # Strategy 2: Try Unsplash search
                photo_ids = search_unsplash_photos(query, count=3)
                if photo_ids and img_idx < len(photo_ids):
                    size = download_unsplash_photo(photo_ids[img_idx], filepath)

            if size > 0:
                downloaded += 1
                print(f"  [{downloaded}/{total}] {filename} ({size//1024}KB) - {query}")
            else:
                print(f"  [SKIP] {query} #{img_idx} - download failed")

            time.sleep(0.5)

    return downloaded


def generate_rich_metadata(output_base, themes):
    """Generate metadata with people, actions, emotions - matching AssetCard schema"""
    metadata = {}

    for theme_name, config in themes.items():
        theme_dir = os.path.join(output_base, theme_name)
        if not os.path.exists(theme_dir):
            continue

        files = sorted([f for f in os.listdir(theme_dir) if f.endswith(".jpg")])
        base_dt = datetime.fromisoformat(config["base_date"].replace("+08:00", ""))

        for idx, filename in enumerate(files):
            asset_id = f"{theme_name}_{idx+1:03d}"
            timestamp = base_dt + timedelta(minutes=random.randint(10, 45) * idx)

            # Simulate people data based on theme
            if theme_name == "family_summer":
                people = [
                    {"person_id": f"p{random.randint(1,3):02d}", "role_guess": random.choice(["child", "parent"]),
                     "emotion": random.choice(["happy", "joyful"]), "face_quality": round(random.uniform(0.75, 0.95), 2)}
                    for _ in range(random.randint(1, 3))
                ]
                actions = random.sample(config["actions"], k=random.randint(1, 3))
                caption_templates = [
                    "傍晚一家人在公园散步，孩子开心地跑在前面",
                    "阳光透过树叶洒在草地上，孩子在追泡泡",
                    "父母牵着孩子的手走在夕阳下的公园小路上",
                    "孩子在沙滩上奔跑，海浪拍打着脚踝",
                    "一家人在草地上野餐，笑声不断",
                ]
            elif theme_name == "city_trip":
                people = [
                    {"person_id": f"p{random.randint(1,4):02d}", "role_guess": random.choice(["traveler", "friend", "couple"]),
                     "emotion": random.choice(["excited", "curious", "happy"]), "face_quality": round(random.uniform(0.70, 0.92), 2)}
                    for _ in range(random.randint(1, 3))
                ]
                actions = random.sample(config["actions"], k=random.randint(1, 2))
                caption_templates = [
                    "旅行者站在标志性建筑前留下合影",
                    "朋友几个人在街头探索当地美食",
                    "背着背包走在异国他乡的老城街道上",
                    "站在山顶俯瞰远处的城市天际线",
                    "在海边拍下旅行中最灿烂的笑容",
                ]
            else:
                people = [
                    {"person_id": f"p{random.randint(1,5):02d}", "role_guess": random.choice(["friend", "classmate", "graduate"]),
                     "emotion": random.choice(["joyful", "excited", "nostalgic"]), "face_quality": round(random.uniform(0.72, 0.93), 2)}
                    for _ in range(random.randint(2, 5))
                ]
                actions = random.sample(config["actions"], k=random.randint(1, 3))
                caption_templates = [
                    "朋友们举起酒杯为毕业干杯",
                    "穿着学士服在舞台上抛起学位帽",
                    "生日蛋糕前的烛光映照着笑脸",
                    "彩纸纷飞中大家欢呼拥抱",
                    "毕业那天和最好的朋友留下最后一张合影",
                ]

            metadata[asset_id] = {
                "asset_id": asset_id,
                "filename": filename,
                "source_path": f"sample_gallery/{theme_name}/{filename}",
                "asset_type": "image",
                "timestamp": timestamp.isoformat() + "+08:00",
                "location": {**config["location"], "privacy_level": "city_only"},
                "people": people,
                "scene_tags": config["scene_tags"],
                "actions": actions,
                "emotion": random.choice(config["emotions"]),
                "quality": {
                    "aesthetic": round(random.uniform(0.68, 0.95), 2),
                    "sharpness": round(random.uniform(0.72, 0.95), 2),
                    "exposure": round(random.uniform(0.65, 0.90), 2),
                    "duplicate_score": round(random.uniform(0.05, 0.20), 2),
                },
                "semantic_caption": random.choice(caption_templates),
                "safety": {"sensitive": False, "risk_tags": [], "share_allowed": True},
            }

    return metadata


def main():
    print("=" * 60)
    print("Sample Gallery V2 - People-Focused Photos")
    print("=" * 60)

    os.makedirs(OUTPUT_BASE, exist_ok=True)
    total_downloaded = 0

    for theme_name, config in THEMES.items():
        count = download_theme(theme_name, config)
        total_downloaded += count

    # Generate rich metadata
    print(f"\n{'='*50}")
    print("Generating rich metadata with people/actions/emotions...")
    metadata = generate_rich_metadata(OUTPUT_BASE, THEMES)

    metadata_path = os.path.join(OUTPUT_BASE, "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"  -> Saved {len(metadata)} asset cards to {metadata_path}")

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total images: {total_downloaded}")
    print(f"Output: {OUTPUT_BASE}")
    for theme_name in THEMES:
        theme_dir = os.path.join(OUTPUT_BASE, theme_name)
        if os.path.exists(theme_dir):
            count = len([f for f in os.listdir(theme_dir) if f.endswith(".jpg")])
            print(f"  {theme_name}: {count} images")
    print("Done!")


if __name__ == "__main__":
    main()
