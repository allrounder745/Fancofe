import json
from playwright.sync_api import sync_playwright

def extract_m3u8_links():
    output = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.fancode.com/live", timeout=60000)
        page.wait_for_timeout(5000)

        # Get all live match URLs
        links = page.eval_on_selector_all("a[href*='/live-streaming/']", "els => els.map(e => e.href)")
        print(f"[✓] Found {len(links)} match links")

        for link in links:
            print(f"[→] Visiting: {link}")
            page.goto(link, timeout=60000)
            page.wait_for_timeout(10000)

            # Grab M3U8 from network requests
            m3u8_url = ""

            try:
                # Intercept network requests for .m3u8
                def handle_response(response):
                    nonlocal m3u8_url
                    if ".m3u8" in response.url and not m3u8_url:
                        m3u8_url = response.url

                page.on("response", handle_response)
                page.wait_for_timeout(5000)

                if m3u8_url:
                    output.append({
                        "match_page": link,
                        "m3u8": m3u8_url,
                        "status": "LIVE"
                    })

            except Exception as e:
                print("❌ Error:", e)

        browser.close()

    with open("live_matches.json", "w") as f:
        json.dump(output, f, indent=2)

    print("[✓] live_matches.json updated")

if __name__ == "__main__":
    extract_m3u8_links()
