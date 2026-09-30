import os
import time
import requests

OUTPUT_DIR = "D:/tmp/sample-gallery-v2/family_summer"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

# Additional curated Unsplash URLs with people - family/children/outdoor themes
EXTRA_URLS = [
    "https://images.unsplash.com/photo-1471341971476-ae15ff5dd4ea?w=1200&q=80",
    "https://images.unsplash.com/photo-1502086223501-7ea6ecd79368?w=1200&q=80",
    "https://images.unsplash.com/photo-1504439904031-93ded9f94e4e?w=1200&q=80",
    "https://images.unsplash.com/photo-1516733725897-1aa76e56385a?w=1200&q=80",
    "https://images.unsplash.com/photo-1543854589-fdd815f176e0?w=1200&q=80",
    "https://images.unsplash.com/photo-1504175970294-503faf4bf0a8?w=1200&q=80",
    "https://images.unsplash.com/photo-1491013516836-7db643ee1256?w=1200&q=80",
    "https://images.unsplash.com/photo-1530089711-2634-4b49-8f73-d0e29b666a78?w=1200&q=80",
    "https://images.unsplash.com/photo-1518831959646-742c3a6e6893?w=1200&q=80",
    "https://images.unsplash.com/photo-1523438885200-e635ba2c371e?w=1200&q=80",
    "https://images.unsplash.com/photo-1519689680058-324335c77eba?w=1200&q=80",
    "https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?w=1200&q=80",
    "https://images.unsplash.com/photo-1494894194458-0174142560c3?w=1200&q=80",
    "https://images.unsplash.com/photo-1504473032632-81f37a60de6e?w=1200&q=80",
    "https://images.unsplash.com/photo-1475503572774-15a45e5d60b9?w=1200&q=80",
]

os.makedirs(OUTPUT_DIR, exist_ok=True)
existing = len([f for f in os.listdir(OUTPUT_DIR) if f.endswith(".jpg")])
print(f"Existing images: {existing}")

downloaded = existing
for i, url in enumerate(EXTRA_URLS):
    if downloaded >= 20:
        break
    filename = f"family_summer_{downloaded+1:03d}.jpg"
    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code == 200 and len(resp.content) > 10000:
            with open(filepath, "wb") as f:
                f.write(resp.content)
            downloaded += 1
            print(f"  [{downloaded}/20] {filename} ({len(resp.content)//1024}KB)")
        else:
            print(f"  SKIP #{i+1}: HTTP {resp.status_code}, size={len(resp.content)}")
    except Exception as e:
        print(f"  ERROR #{i+1}: {e}")
    time.sleep(0.8)

print(f"\nDone! Total family_summer images: {downloaded}")
