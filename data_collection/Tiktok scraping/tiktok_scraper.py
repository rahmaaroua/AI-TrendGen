import csv
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def setup_driver():
    """Initializes and configures the Chrome WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent detection
    options.add_argument("--log-level=3")  # Suppress unnecessary logs
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    return driver


def fetch_trending_tiktoks(max_videos=60):
    """Scrapes trending TikTok videos, extracting views and date_posted first before other details."""
    driver = setup_driver()
    driver.get("https://www.tiktok.com/explore")
    time.sleep(5)  # Allow time for initial page load

    print("[🔄] Waiting for TikTok Explore page to load...")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    video_data = []
    seen_urls = set()
    attempts = 0
    max_attempts = 60

    while len(video_data) < max_videos and attempts < max_attempts:
        time.sleep(random.uniform(2, 4))  # Mimic human-like delay

        # Extract video URLs and views using JavaScript
        video_elements = driver.execute_script("""
            return Array.from(document.querySelectorAll('a[href*="/video/"]'))
                        .map(el => ({
                            url: el.href, 
                            views: el.closest('div').innerText.split('\\n')[0]  // Extracts views reliably
                        }));
        """)

        for video in video_elements:
            url, views = video["url"], video["views"]
            if url not in seen_urls and "/video/" in url:
                video_data.append({"url": url, "views": views})
                seen_urls.add(url)
                print(f"[✅] Found Video: {url} | Views: {views}")

                if len(video_data) >= max_videos:
                    break

        # Scroll down dynamically
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(random.uniform(2, 4))  # Random delay to avoid detection

        attempts += 1
        print(f"[🔄] Scroll attempt {attempts}/{max_attempts}")

    print(f"[🔥] Found {len(video_data)} trending videos after {attempts} scrolls.")

    # **Step 2: Scrape full details from individual video pages**
    for i, video in enumerate(video_data):
        print(f"[📹] Scraping full details for video {i + 1}/{len(video_data)}: {video['url']}")
        video.update(scrape_tiktok_video(driver, video["url"]))

    driver.quit()
    return video_data


def scrape_tiktok_video(driver, video_url):
    """Extracts full details (likes, shares, comments, hashtags, date_posted) from video pages."""
    driver.get(video_url)
    time.sleep(random.uniform(3, 5))  # Short delay to load content

    data = {}

    try:
        like_count = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//strong[@data-e2e="like-count"]'))
        ).text
        data["likes"] = like_count
    except:
        data["likes"] = "N/A"

    try:
        shares = driver.find_element(By.XPATH, '//strong[@data-e2e="share-count"]').text
        data["shares"] = shares
    except:
        data["shares"] = "N/A"

    try:
        comment_count = driver.find_element(By.XPATH, '//strong[@data-e2e="comment-count"]').text
        data["comments_count"] = comment_count
    except:
        data["comments_count"] = "N/A"

    try:
        hashtags = [tag.text for tag in driver.find_elements(By.XPATH, '//a[contains(@href, "/tag/")]')]
        data["hashtags"] = ", ".join(hashtags) if hashtags else "None"
    except:
        data["hashtags"] = "None"

    try:
        # Try to find the relative date (e.g., "3 days ago", "1 week ago")
        date_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'ago') or contains(text(), 'Il y a')]"))
        )
        date_posted = date_element.text
    except:
        try:
            # Try to find the absolute date format (e.g., "Jan 14, 2024")
            date_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(), ',')]"))
            )
            date_posted = date_element.text
        except:
            date_posted = "Unknown"

    data["date_posted"] = date_posted

    print(f"[✅] Done scraping video: {video_url}")
    return data


# Run the scraper
if __name__ == "__main__":
    tiktoks = fetch_trending_tiktoks()

    # Save to CSV
    with open("tiktok_trendings.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["url", "views", "likes", "shares", "comments_count", "hashtags", "date_posted"])
        writer.writeheader()
        writer.writerows(tiktoks)

    print("[✅] Scraping complete. Data saved to tiktok_trending.csv")
