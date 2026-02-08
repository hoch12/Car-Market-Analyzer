import time
import random
import os
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# --- CONSTANTS ---
STATE_FILE = "scraper_state.json"


def get_project_root():
    """Returns the absolute path to the project root directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(current_dir))


def load_config():
    """Loads configuration from config.json."""
    root = get_project_root()
    config_path = os.path.join(root, 'config.json')
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_state():
    """Loads the last scraped page number from a state file."""
    root = get_project_root()
    state_path = os.path.join(root, STATE_FILE)
    if os.path.exists(state_path):
        with open(state_path, 'r') as f:
            return json.load(f)
    return {"last_page": 0}


def save_state(page_number):
    """Saves the current page number to a state file."""
    root = get_project_root()
    state_path = os.path.join(root, STATE_FILE)
    with open(state_path, 'w') as f:
        json.dump({"last_page": page_number}, f)


def get_existing_urls(csv_path):
    """Reads the CSV and returns a set of already scraped URLs to avoid duplicates."""
    if not os.path.exists(csv_path):
        return set()
    try:
        df = pd.read_csv(csv_path)
        if 'url' in df.columns:
            return set(df['url'].unique())
    except Exception:
        return set()
    return set()


def setup_driver(config):
    """Initializes Chrome WebDriver."""
    options = webdriver.ChromeOptions()
    if config['driver']['headless']:
        options.add_argument('--headless')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument(f"user-agent={config['driver']['user_agent']}")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


def extract_ad_data_flexible(element):
    """Extracts data from a single ad element."""
    data = {}
    try:
        # 1. URL & Title
        try:
            link_el = element.find_element(By.TAG_NAME, "a")
            data['url'] = link_el.get_attribute("href")
            data['title'] = link_el.text.strip()
        except:
            return None

        if not data['url']:
            return None

        # 2. Price
        try:
            price_el = element.find_element(By.XPATH, ".//*[contains(@class, 'price')]")
            data['raw_price'] = price_el.text.strip()
        except:
            data['raw_price'] = "0"

        # 3. Description
        try:
            info_el = element.find_element(By.XPATH, ".//*[contains(@class, 'info')]")
            data['description'] = info_el.text.strip()
        except:
            data['description'] = ""

        return data
    except Exception:
        return None


def main():
    try:
        config = load_config()
    except Exception as e:
        print(f"Error loading config: {e}")
        return

    scraper_cfg = config['scraper']
    paths_cfg = config['paths']
    base_url_config = scraper_cfg['base_url']

    # Prepare paths
    root = get_project_root()
    output_dir = os.path.join(root, paths_cfg['output_folder'])
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, paths_cfg['output_filename'])

    # Load state (Resume logic)
    state = load_state()
    start_page = state['last_page'] + 1

    # Load existing URLs to prevent duplicates
    seen_urls = get_existing_urls(output_path)
    print(f"--- INFO: Loaded {len(seen_urls)} existing cars. Resuming from page {start_page}. ---")

    if start_page > scraper_cfg['num_pages']:
        print("Target pages already reached. Increase 'num_pages' in config.json if you want more.")
        return

    driver = setup_driver(config)

    try:
        print("\n" + "=" * 50)
        print("⚠️  MANUAL INTERVENTION REQUIRED")
        print("1. Browser opens. Click 'Souhlasím' (Agree).")
        print("2. Press ENTER here in terminal.")
        print("=" * 50 + "\n")

        driver.get(base_url_config)
        input(">>> Press ENTER here after cookies are handled... <<<")

        for page_number in range(start_page, scraper_cfg['num_pages'] + 1):

            separator = "&" if "?" in base_url_config else "?"
            full_url = f"{base_url_config}{separator}strana={page_number}"

            print(f"Loading Page {page_number}/{scraper_cfg['num_pages']}: {full_url}")
            driver.get(full_url)

            # Scroll down to trigger lazy loading
            body = driver.find_element(By.TAG_NAME, "body")
            for _ in range(3):
                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.5)
            time.sleep(random.uniform(2, 4))  # Random delay

            # Find ads (Flexible selector)
            ads = driver.find_elements(By.XPATH, "//div[contains(@class, 'c-item')]")
            if not ads:
                ads = driver.find_elements(By.XPATH, "//a[contains(@href, '/osobni/detail/')]")

            page_new_data = []

            for ad in ads:
                data = extract_ad_data_flexible(ad)
                if data and data.get('url'):
                    # DUPLICATE CHECK
                    if data['url'] not in seen_urls:
                        seen_urls.add(data['url'])
                        page_new_data.append(data)

            # SAVE DATA IMMEDIATELY (Append mode)
            if page_new_data:
                df = pd.DataFrame(page_new_data)
                # If file doesn't exist, write header. If it does, skip header.
                header = not os.path.exists(output_path)
                df.to_csv(output_path, mode='a', header=header, index=False, encoding='utf-8')
                print(f"   -> Saved {len(page_new_data)} new cars (Total unique: {len(seen_urls)})")
            else:
                print("   -> No new unique cars found on this page.")

            # UPDATE STATE
            save_state(page_number)

    except Exception as e:
        print(f"Critical Error: {e}")

    finally:
        driver.quit()
        print("--- SCRAPING PAUSED/FINISHED ---")


if __name__ == "__main__":
    main()