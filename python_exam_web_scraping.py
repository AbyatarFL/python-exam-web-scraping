# config awal

import sys
import json
import openpyxl
import os
import csv
import logging
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# 1. Scrape the Search Results
def scrape_list_view(driver, start_date_value, end_date_value):
    driver.get("https://www.melbourne.vic.gov.au/planning-permit-register")

    # Cari menu tab
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "ul.vertical-tabs__menu"))
    )
    time.sleep(2)

    # buka tab Tanggal
    date_range_tab = driver.find_element(By.CSS_SELECTOR, "a[href='#edit-date-range-pane']")
    driver.execute_script("arguments[0].click();", date_range_tab)

    # Isi tanggal awal dan akhir
    driver.find_element(By.ID, "edit-date-range-pane-application-decision-date-from").send_keys(start_date_value)
    driver.find_element(By.ID, "edit-date-range-pane-application-decision-date-to").send_keys(end_date_value)

    # Submit
    search_btn = driver.find_element(By.ID, "edit-date-range-pane-submit")
    driver.execute_script("arguments[0].click();", search_btn)

    logging.info("Search submitted!")

    all_data = []
    while True:
        # Tunggu baris tabel muncul
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tbody tr"))
        )

        # ambil semua baris
        rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if not cols:
                continue
            # ambil link dari kolom pertama
            link_element = cols[0].find_element(By.TAG_NAME, "a")
            url = link_element.get_attribute("href")

            # ambil id dari url
            appid = ""
            if "appid=" in url:
                appid = url.split("appid=")[-1].split("&")[0]

            # isi dictionary
            all_data.append({
                "id": appid,
                "url": url,
                "date_collected": datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            })

        # print halaman berapa
        page_summary = driver.find_element(By.CSS_SELECTOR, "p.page-summary").text.strip()
        logging.info(f"Scraped {page_summary}, total collected: {len(all_data)}")

        # cek apakah ada tombol next
        try:
            next_button = driver.find_element(By.LINK_TEXT, "[Next >>]")
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(2)
        except:
            logging.info("No more pages.")
            break

    return all_data

# 2. Parse the Details of Each Result
def scrape_details(driver, all_data):
    details_data = []

    # ambil url dan id yang exist dari data sebelumnya
    for row in all_data:
        url = row["url"]
        appid = row["id"]

        driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table"))
        )

        details_dict = {
            "id": appid,
            "details_url": url,
            "date_scraped": datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        }

        # ambil semua pasangan key-value dari tabel
        rows = driver.find_elements(By.CSS_SELECTOR, "tr")
        for r in rows:
            try:
                key = r.find_element(By.TAG_NAME, "th").text.strip()
                value = r.find_element(By.TAG_NAME, "td").text.strip()
                details_dict[key] = value
            except:
                continue

        details_data.append(details_dict)
        logging.info(f"Scraped details for ID {appid}")

    return details_data

def ensure_output_folder():
    """Buat folder output di lokasi yang sama dengan main script"""
    base_dir = os.path.dirname(os.path.abspath(__file__))  # folder di mana file .py ini berada
    folder_name = os.path.join(base_dir, "Output_Files")

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    return folder_name

def save_csv(all_data, details_data):
    """Save data ke CSV"""
    output_dir = ensure_output_folder()

    headers = ["id", "url", "date_collected"]

    fixed_fields = ["id", "details_url", "date_scraped"]
    all_keys = set()
    for d in details_data:
        all_keys.update(d.keys())
    for f in fixed_fields:
        all_keys.discard(f)
    fieldnames = fixed_fields + sorted(all_keys)

    with open(os.path.join(output_dir, "output.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(all_data)

    with open(os.path.join(output_dir, "details_output.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(details_data)


def save_json(all_data, details_data):
    """Save data ke JSON"""
    output_dir = ensure_output_folder()

    with open(os.path.join(output_dir, "output.json"), "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4)

    with open(os.path.join(output_dir, "details_output.json"), "w", encoding="utf-8") as f:
        json.dump(details_data, f, indent=4)


def save_xlsx(all_data, details_data):
    """Save data ke XLSX (Excel) sebagai file terpisah"""
    output_dir = ensure_output_folder()

    # save all_data
    wb1 = openpyxl.Workbook()
    ws1 = wb1.active
    ws1.title = "List_View"
    headers1 = ["id", "url", "date_collected"]
    ws1.append(headers1)
    for row in all_data:
        ws1.append([row.get(h, "") for h in headers1])
    wb1.save(os.path.join(output_dir, "output.xlsx"))

    # save details_data
    wb2 = openpyxl.Workbook()
    ws2 = wb2.active
    ws2.title = "Details_View"

    fixed_fields = ["id", "details_url", "date_scraped"]
    all_keys = set()
    for d in details_data:
        all_keys.update(d.keys())
    for f in fixed_fields:
        all_keys.discard(f)
    fieldnames = fixed_fields + sorted(all_keys)

    ws2.append(fieldnames)
    for row in details_data:
        ws2.append([row.get(h, "") for h in fieldnames])
    wb2.save(os.path.join(output_dir, "details_output.xlsx"))

def main():
    start_date_value = input("Masukkan tanggal mulai (mm/dd/yyyy): ")
    end_date_value = input("Masukkan tanggal akhir (mm/dd/yyyy): ")

    driver = setup_driver()
    try:
        all_data = scrape_list_view(driver, start_date_value, end_date_value)
        details_data = scrape_details(driver, all_data)

        # Save in all formats
        save_csv(all_data, details_data)
        save_json(all_data, details_data)
        save_xlsx(all_data, details_data)

        logging.info("All files saved (CSV, JSON, XLSX).")
    finally:
        driver.quit()
        logging.info("Driver closed.")


if __name__ == "__main__":
    main()