import time
import pandas as pd
import sys
import json
import subprocess
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


if len(sys.argv) >= 3:
    url = sys.argv[1]
    review_count = int(sys.argv[2])
else:
     url = " https://tk.tokopedia.com/ZSfLw2ccS/"
     review_count = 100  # default jika tidak ada argumen

# -----------HEADLESS-----------
options = webdriver.ChromeOptions()
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
# options.add_argument("--headless=new")  # Biar Chrome tidak muncul
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--log-level=3")

driver = webdriver.Chrome(options=options)
driver.get(url)
# driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
soup = BeautifulSoup(driver.page_source, "html.parser")
time.sleep(10)

#---------- pencet silang untuk iklan yang muncul ------------- 
#button nya ada di dalam div class="css-11hzwo5", jadi mencet button yg ada di situ

ad_container = WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "div.css-11hzwo5"))
)

# cari tombol di dalam div tsb
close_button = ad_container.find_element(By.TAG_NAME, "button")

# klik tombolnya
driver.execute_script("arguments[0].click();", close_button)
print("[INFO] Iklan tertutup otomatis.")
time.sleep(1)

driver.execute_script("window.scrollTo(0, document.body.scrollHeight/1.5);")

information = []
# -----------------SCRAPING IMG URL-----------------
heads = soup.find_all('div', attrs={'class': 'css-1logqad active'})
for head in heads:
    img = head.find('img')
    if img and img.get('src'):
        url_image = img['src']
        print("URL IMAGE : " + url_image)
for _ in range(5):
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(2)
# -----------------SCRAPING NAME-----------------
product_name = soup.find('h1', attrs = {'data-testid':'lblPDPDetailProductName'}).text
print("PRODUCT NAME : " + product_name)

# -----------------SCRAPING PRICE-----------------
product_price = soup.find('div', attrs = {'data-testid':'lblPDPDetailProductPrice'}).text
print("PRODUCT PRICE : " + product_price)

# -----------------DESCRIPTION-----------------
try:
    desc_div = soup.find('div', attrs={'data-testid': 'lblPDPDescriptionProduk'})
    if desc_div:
        # Ganti <br> dengan newline agar paragrafnya tetap terpisah
        for br in desc_div.find_all("br"):
            br.replace_with("\n")
        
        desc = desc_div.get_text(separator="\n", strip=True)
        print("PRODUCT DESC : " + desc)
    else:
        desc = "No Description"
        print("PRODUCT DESC : " + desc)
except Exception as e:
    desc = "No Description"
    print("PRODUCT DESC : " + desc)
    

# -----------------LOCATION-----------------
location = soup.find('h2', class_='css-793nib-unf-heading e1qvo2ff2').find('b').text
print("LOCATION : " + location)

# -----------------SIMPAN KE EXCEL UNTUK INFO-----------------
information.append({
                "image": url_image,
                "name": product_name,
                "price": product_price,
                "description": desc,
                "location": location
            })
df_info = pd.DataFrame(information)
# df.to_excel("tokopedia_reviews_Program_3.xlsx", index=False)
output_path = r"C:\xampp\htdocs\TA\Program\result\information_from_tokopedia.xlsx"
df_info.to_excel(output_path, index=False)
# -----------------BUKA TAB ULASAN-----------------
print("Membuka tab ulasan...")

try:
    # Scroll agar tab ulasan terlihat
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/1.5);")
    time.sleep(2)

    # Tunggu tombol ulasan muncul dan klik
    review_tab = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='review']"))
    )
    driver.execute_script("arguments[0].click();", review_tab)
    print("Tab ulasan berhasil dibuka.")
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
except Exception as e:
    print("Gagal membuka tab ulasan:", e)

# -----------------SCRAPING REVIEWS-----------------
data = []
page = 1
last_review_snapshot = set()
while len(data) < review_count:
    time.sleep(5)
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.css-15m2bcr"))
    )

    containers = driver.find_elements(By.CSS_SELECTOR, "article.css-15m2bcr")
    new_reviews = []

    for container in containers:
        if len(data) >= review_count:
            break

        # try:
        account = container.find_element(By.CSS_SELECTOR, "span.name").text.strip()

        # Cek tombol "Selengkapnya" (button.css-89c2tx)
        see_more_buttons = container.find_elements(By.CSS_SELECTOR, "button.css-89c2tx")
        if see_more_buttons:
            print("ada see more button")
            driver.execute_script("arguments[0].click();", see_more_buttons[0])
            time.sleep(3)
            print(f"[INFO] Klik 'Selengkapnya' pada review oleh {account}")
                # scroll 300px ke bawah
            time.sleep(1)

        # WebDriverWait(container, 5).until(
        #     lambda d: d.find_element(By.CSS_SELECTOR, "[data-testid='lblItemUlasan']")
        # )
        
        # review = container.find_element(By.CSS_SELECTOR, "span[data-testid='lblItemUlasan']").text.strip()
        # driver.execute_script("window.scrollBy(0, 50);")

        try:
            WebDriverWait(container, 3).until(
                lambda d: d.find_element(By.CSS_SELECTOR, "[data-testid='lblItemUlasan']")
            )
            review = container.find_element(By.CSS_SELECTOR, "span[data-testid='lblItemUlasan']").text.strip()

            # Kalau review kosong atau hanya spasi → skip
            if not review.strip():
                print(f"[SKIP] {account} tidak punya teks ulasan")
                continue
            driver.execute_script("window.scrollBy(0, 50);")

        except:
            # Tidak ada teks review → skip container ini
            print(f"[SKIP] {account} hanya kirim gambar / tidak ada teks")
            continue
        
        key = (account, review)
        if key not in last_review_snapshot:
            new_reviews.append(key)
            data.append({
                "account": account,
                "review": review,
                "label": ""
            })

        # except Exception as e:
        #     print(f"[WARN] Gagal ambil review: {e}")
        #     continue

    # Pindah halaman
    try:
        next_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Laman berikutnya']")
        if next_btn.get_attribute("disabled"):
            print("Tidak ada halaman berikutnya.")
            break

        driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
        driver.execute_script("arguments[0].click();", next_btn)
        print(f"Berpindah ke halaman {page + 1} ...")
        page += 1
        time.sleep(5)
    except Exception as e:
        print(f"Tombol halaman berikutnya tidak ditemukan.")
        break

    last_review_snapshot = set(new_reviews)

print("DONE SCRAPING YEAYYYY!!! :)")
driver.quit()

# print("+++" * 20)
# print(data) 
    
df = pd.DataFrame(data)
# df.to_excel("tokopedia_reviews_Program_3.xlsx", index=False)
output_path = r"C:\xampp\htdocs\TA\Program\result\crawling_from_tokopedia.xlsx"
df.to_excel(output_path, index=False)


# -----------------RUN PREPROCESSING AUTOMATICALLY-----------------
print("\n=== MEMULAI PREPROCESSING REVIEW ===\n")
try:
    result = subprocess.run(
        ["python", r"C:\xampp\htdocs\TA\Program\prediction_tokopedia.py"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    print("\n=== PREPROCESSING SELESAI ===")
except Exception as e:
    print("Gagal menjalankan preprocessing:", e)