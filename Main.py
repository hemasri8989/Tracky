import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# ----------------- Telegram Setup -----------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    try:
        requests.get(url)
    except Exception as e:
        print("Telegram error:", e)

# ----------------- IMAT Credentials -----------------
IMAT_USERNAME = os.environ.get("IMAT_USERNAME")
IMAT_PASSWORD = os.environ.get("IMAT_PASSWORD")

# ----------------- Selenium Setup -----------------
options = Options()
options.headless = True
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)

# ----------------- Login -----------------
driver.get("https://admission-imat.ilmiotest.it/login")
driver.find_element(By.NAME, "username").send_keys(IMAT_USERNAME)
driver.find_element(By.NAME, "password").send_keys(IMAT_PASSWORD)
driver.find_element(By.XPATH, '//button[@type="submit"]').click()
time.sleep(5)  # wait for login to complete

# ----------------- Go to slots page -----------------
SLOTS_URL = "https://admission-imat.ilmiotest.it/choice"
TARGET_CITIES = ["Chennai", "Delhi"]

def go_to_slots():
    driver.get(SLOTS_URL)
    time.sleep(2)
    # Check if country selection page appears
    try:
        country_dropdown = driver.find_element(By.NAME, "country")  # adjust if different
        for option in country_dropdown.find_elements(By.TAG_NAME, "option"):
            if option.text.strip().lower() == "india":
                option.click()
                driver.find_element(By.XPATH, '//button[text()="Submit"]').click()  # adjust button
                time.sleep(3)
                print("India selected.")
                break
    except NoSuchElementException:
        # No country selection, continue
        pass

go_to_slots()

# ----------------- Monitoring Loop -----------------
while True:
    try:
        go_to_slots()  # refresh page and select India if needed

        for city in TARGET_CITIES:
            try:
                # Find status dot next to city
                dot_element = driver.find_element(By.XPATH, f"//td[contains(text(), '{city}')]/following-sibling::td/span")
                dot_class = dot_element.get_attribute("class").lower()

                if "yellow" in dot_class or "green" in dot_class:
                    send_telegram(f"⚠️ Slot available in {city}! Status: {dot_class.upper()}")
                    print(f"Slot available in {city}! Status: {dot_class.upper()}")
                else:
                    print(f"No slot in {city}. Status: {dot_class.upper()}")
            except Exception:
                print(f"Could not find status for {city}.")

    except Exception as e:
        print("Error during check:", e)

    time.sleep(60)  # check every 1 minute
