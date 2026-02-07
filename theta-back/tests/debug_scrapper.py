import requests
import re
import json
import html

# 🎯 TARGET: The same post
USER_ID = "107292705535950"
POST_ID = "3355584591268819"

# Construct the Embed URL (The "Public Backdoor")
target_url = f"https://www.facebook.com/plugins/post.php?href=https%3A%2F%2Fwww.facebook.com%2F{USER_ID}%2Fposts%2F{POST_ID}&width=500"

# 🎭 MASQUERADE: Desktop Chrome (Standard)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Fetch-Dest": "iframe",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Referer": "https://www.google.com/"
}


def clean_text(text):
    if not text: return ""
    # Decode HTML entities (&quot; -> ")
    text = html.unescape(text)
    # Remove tags
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()


def run_test():
    print(f"⚡ Fetching Embed: {target_url}")
    try:
        resp = requests.get(target_url, headers=HEADERS, timeout=10)
        print(f"✅ Status: {resp.status_code}")

        # SAVE RAW (Always debug this)
        with open("debug_embed.html", "w", encoding="utf-8") as f:
            f.write(resp.text)
        print("💾 Saved raw HTML to 'debug_embed.html'")

        # 🕵️ EXTRACTION LOGIC (Specific to Embeds)
        content = resp.text
        data = {"text": "", "images": []}

        # 1. TEXT STRATEGY: Look for the specific container classes Facebook uses in embeds
        # They usually put text in <p> tags inside a container
        # We grab all paragraphs and filter out the "Join Facebook" junk

        # Regex to capture content inside <p>...</p>
        p_matches = re.findall(r'<p[^>]*>(.*?)</p>', content, re.DOTALL)

        valid_lines = []
        for p in p_matches:
            clean = clean_text(p)
            if len(clean) > 5 and "Facebook" not in clean:
                valid_lines.append(clean)

        if valid_lines:
            data["text"] = "\n".join(valid_lines)
        else:
            # Fallback: Look for "story_text" or accessible descriptions
            # Sometimes text is in <div class="_5pbx ...">
            div_match = re.search(r'<div[^>]*class="[^"]*_5pbx[^"]*"[^>]*>(.*?)</div>', content, re.DOTALL)
            if div_match:
                data["text"] = clean_text(div_match.group(1))

        # 2. IMAGE STRATEGY
        # Embeds usually load the image as a background or img tag with specific class
        # Look for the main image in <img class="_46-i" ... src="...">
        img_matches = re.findall(r'<img[^>]+src="([^"]+)"', content)

        # Filter for actual content images (exclude spacers/icons)
        for img in img_matches:
            img = html.unescape(img)
            if "scontent" in img and "static" not in img:  # scontent is FB's CDN
                data["images"].append(img)

        print("\n-------- 🕵️ EXTRACTION RESULT --------")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("--------------------------------------")

        if not data["text"]:
            print("❌ TEXT NOT FOUND. Check 'debug_embed.html'.")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    run_test()