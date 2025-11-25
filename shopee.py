# pip install undetected-chromedriver
# pip install setuptools

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import pandas as pd
import sys
import subprocess

def login_shopee(browser, email, password):
    print("Membuka halaman login Shopee...")
    browser.get("https://shopee.co.id/buyer/login?next=https%3A%2F%2Fshopee.co.id%2F")
    # browser.get("https://shopee.co.id/Miniso-Official-Boneka-Small-Penguin-Plush-Toy-Boneka-Lucu-mainan-anak-boneka-lucu-lembut-boneka-gemoy-boneka-import-boneka-anak-Hadiah-Ulang-Tahun-Kado-anak-Kado-untuk-cewek-Hadiah-untuk-cowok-Kado-Natal-i.40847197.4805760963?sp_atk=d0e4f8f9-fd4e-4955-8756-394137549d53&xptdk=d0e4f8f9-fd4e-4955-8756-394137549d53")
    # Tunggu input email muncul
    WebDriverWait(browser, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".W2x2F8 .X0Jdtz"))
    )

    # Isi Email dan Password
    print("Mengisi email dan password...")
    browser.find_element(By.CSS_SELECTOR, ".W2x2F8 .X0Jdtz").send_keys(email)
    browser.find_element(By.CSS_SELECTOR, ".wIH_BM .X0Jdtz").send_keys(password)
    time.sleep(1)
    
    # # Klik tombol Login
    print("Menekan tombol login...")
    browser.find_element(By.CSS_SELECTOR, ".b5aVaf.PVSuiZ.Gqupku.qz7ctP.qxS7lQ.Q4KP5g").click()

    # Tunggu sebentar untuk verifikasi manual (captcha/OTP)
    print("\n>>> Silakan selesaikan verifikasi Shopee secara manual (captcha atau OTP).")
    print("Saya tunggu 30 detik...")
    time.sleep(90)

    # Setelah login berhasil, pastikan halaman utama terbuka
    try:
        WebDriverWait(browser, 5).until(
            # EC.presence_of_element_located((By.CSS_SELECTOR, "input.shopee-searchbar-input__input"))
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.shopee-searchbar-input"))
            
        )
        print("✅ Login Shopee berhasil!")
    except TimeoutException:
        print("⚠️ Login gagal atau belum selesai verifikasi.")
        return False
    
    return True

def buka_produk(browser, url_produk):
    print(f"Membuka halaman produk:\n{url_produk}")
    browser.get(url_produk)
    print("✅ Halaman produk berhasil dibuka!")

if __name__ == "__main__":
    try: 
        # Setup browser
        options = uc.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(
            '--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/117.0.0.0 Safari/537.36"'
        )
        options.add_argument("--window-size=1366,768")


        # browser = uc.Chrome(version_main=141, options=options, use_subprocess=True)
        browser = uc.Chrome(options=options, use_subprocess=True)
        wait = WebDriverWait(browser, 20)
        
        html = browser.page_source
        soup = BeautifulSoup(html, "html.parser")

        # Data login Shopee
        # email = "meeychellaa@gmail.com"
        email = "meychellapermatasari@gmail.com"
        password = "Harmoni20"
        # email = "sumayouwkevin@gmail.com"
        # password = "Sembarang8"

        information = []

        # URL Produk Shopee
        #url_produk = "https://shopee.co.id/Miniso-Official-Boneka-Small-Penguin-Plush-Toy-Boneka-Lucu-mainan-anak-boneka-lucu-lembut-boneka-gemoy-boneka-import-boneka-anak-Hadiah-Ulang-Tahun-Kado-anak-Kado-untuk-cewek-Hadiah-untuk-cowok-Kado-Natal-i.40847197.4805760963?sp_atk=d0e4f8f9-fd4e-4955-8756-394137549d53&xptdk=d0e4f8f9-fd4e-4955-8756-394137549d53"
        # url_produk = "https://shopee.co.id/sepatu-onitsuka-edr-ginger-peach-sepatu-pria-sepatu-wanita-sepatu-sneakers-i.1063280085.41508300702?xptdk=ca424b77-e460-4064-8e5c-3b7de054e877"
        if len(sys.argv) >= 3:
            url_produk = sys.argv[1]
            review_count = int(sys.argv[2])
        else:
            url_produk = "https://shopee.co.id/Miniso-Official-Boneka-Small-Penguin-Plush-Toy-Boneka-Lucu-mainan-anak-boneka-lucu-lembut-boneka-gemoy-boneka-import-boneka-anak-Hadiah-Ulang-Tahun-Kado-anak-Kado-untuk-cewek-Hadiah-untuk-cowok-Kado-Natal-i.40847197.4805760963?sp_atk=d0e4f8f9-fd4e-4955-8756-394137549d53&xptdk=d0e4f8f9-fd4e-4955-8756-394137549d53"
            review_count = 25
        print(f"URL Produk: {url_produk}")
        print(f"Jumlah Review yang diinginkan: {review_count}\n")
        
        # Jalankan login
        if login_shopee(browser, email, password):

            # Kalau login berhasil, buka link produk
            buka_produk(browser, url_produk)

            # Tunggu biar kamu bisa lihat hasilnya
            time.sleep(3)
            
            #tunggu container nama produk muncul
            container_name = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='WBVL_7']"))
            )

            html = browser.page_source
            soup = BeautifulSoup(html, "html.parser")

            # Scroll biar data lengkap
            for _ in range(2):
                browser.execute_script("window.scrollBy(0, 1000);")
                time.sleep(2)

            # -----------------SCRAPING IMG URL -----------------
            img_elem = soup.select_one("div.UBG7wZ img.uXN1L5")

            if img_elem:
                image_url = img_elem.get("src", "")
                if image_url:
                    print("🖼️ Gambar produk:", image_url)
                else:
                    print("⚠️ Attribute src tidak ditemukan pada tag img.")
            else:
                print("⚠️ Tag img untuk gambar produk tidak ditemukan.")

            # -----------------SCRAPING NAME-----------------
            product_elem = soup.select_one("div.WBVL_7 h1.vR6K3w")
            if product_elem:
                product_name = product_elem.get_text(strip=True)
                print("🛍️ Judul produk:", product_name)
            else:
                print("⚠️ Nama produk tidak ditemukan.")

            # -----------------SCRAPING PRICE-----------------
            price_elem = soup.select_one("div.jRlVo0 div.IZPeQz.B67UQ0")
            if price_elem:
                product_price = price_elem.get_text(strip=True)
                print("💰 Harga produk:", product_price)
            else:
                print("⚠️ Harga produk tidak ditemukan.")

            # -----------------DESCRIPTION-----------------
            # desc_elem = soup.select_one("div.Gf4Ro0 div.e8lZp3")
            # print("📝 Deskripsi produk:", desc_elem.get_text(strip=True))
            desc_elem = soup.select_one("div.Gf4Ro0 div.e8lZp3")
            if desc_elem:
                # pisahkan tiap paragraf dengan newline
                description = desc_elem.get_text(separator="\n", strip=True)
                print("📝 Deskripsi produk:\n", description)
            else:
                print("⚠️ Deskripsi produk tidak ditemukan.")
            # -----------------LOCATION-----------------
            # Cari elemen <h3> dengan teks "Dikirim Dari"
            location_label = soup.find("h3", string=lambda text: text and "Dikirim Dari" in text)

            if location_label:
                # Ambil <div> setelahnya
                location_elem = location_label.find_next("div")
                location_text = location_elem.get_text(strip=True)
                print("📍 Lokasi penjual:", location_text)
            else:
                print("⚠️ Lokasi penjual tidak ditemukan.")

            # -----------------SIMPAN KE EXCEL UNTUK INFO-----------------
            information.append({
                            "image": image_url,
                            "name": product_name,
                            "price": product_price,
                            "description": description,
                            "location": location_text
                        })
            df_info = pd.DataFrame(information)
            # df.to_excel("tokopedia_reviews_Program_3.xlsx", index=False)
            output_path = r"C:\xampp\htdocs\TA\Program\result\information_from_shopee.xlsx"
            df_info.to_excel(output_path, index=False)
            # -----------------SCRAPING REVIEWS-----------------
            data = []
            # review_count = 25
            page = 1
            last_review_snapshot = set()  # Untuk deteksi duplikasi

            while len(data) < review_count:
                try:
                    # Tunggu container review muncul
                    container_reviews = wait.until(
                        EC.presence_of_element_located((
                            By.CSS_SELECTOR,
                            "div.shopee-product-comment-list"
                        ))
                    )
                except TimeoutException:
                    print("⚠️ Tidak menemukan container review, keluar dari loop.")
                    break

                soup = BeautifulSoup(browser.page_source, "html.parser")
                time.sleep(2)

                # Ambil semua container review individual di dalamnya
                review_containers = soup.select("div.shopee-product-comment-list div.q2b7Oq")
                new_reviews = []

                for review in review_containers:
                    if len(data) >= review_count:
                        break
                    try:
                        account_name = review.select_one("a.InK5kS").get_text(strip=True)
                        review_elem = review.select_one("div.meQyXP")
                        
                        if not review_elem:
                            continue

                        # biat din dinamis untuk tiap review
                        # review_dict = {"account": account_name}
                        review_dict = {
                            "account": account_name,
                            "review": "",
                            "label": ""
                        }

                        divs = review_elem.select("div.F35Wh2")

                        if divs:
                            # ambil semua label apapun namanya
                            for div in divs:
                                label_elem = div.select_one("span.KSv3lN")
                                label = label_elem.get_text(strip=True) if label_elem else ""
                                text = div.get_text(strip=True).replace(label, "").strip(": ").strip()
                                if label:
                                    review_dict[label] = text

                            # komentar tambahan (tanpa label)
                            extra_elem = review_elem.select_one("div.WedDv")
                            if extra_elem:
                                review_dict["review"] = extra_elem.get_text(strip=True)
                        else:
                            # review polos tanpa label
                            review_dict["review"] = review_elem.get_text(separator=" ", strip=True)

                        # hindari duplikasi
                        key = tuple(review_dict.items())
                        if key not in last_review_snapshot:
                            new_reviews.append(key)
                            data.append(review_dict)

                    except AttributeError:
                        continue


                print(f"📄 Total review terkumpul: {len(data)}")

                # Jika tidak ada review baru, artinya halaman terakhir
                if not new_reviews:
                    print("🚫 Tidak ada review baru ditemukan. Halaman terakhir tercapai.")
                    break

                # Update snapshot review terakhir
                last_review_snapshot = set(new_reviews)

                if len(data) >= review_count:
                    print("✅ Sudah mencapai batas review_count, berhenti scraping.")
                    break

                # Coba pindah ke halaman berikutnya
                try:
                    next_btn = wait.until(
                        EC.element_to_be_clickable((
                            By.CSS_SELECTOR,
                            "button.shopee-icon-button.shopee-icon-button--right"
                        ))
                    )

                    print(f"➡️ Menekan tombol halaman berikutnya ({page + 1})...")
                    next_btn.click()
                    time.sleep(4)

                    page += 1

                except Exception as e:
                    print("❌ Gagal menemukan atau menekan tombol halaman berikutnya:", str(e))
                    break

            print(f"\n📊 Jumlah review akhir: {len(data)}")
            print(data)
            df = pd.DataFrame(data)
            output_path = r"C:\xampp\htdocs\TA\Program\result\crawling_from_shopee.xlsx"
            df.to_excel(output_path, index=False)


    # Tutup browser setelah selesai
    finally:
        print("Menutup browser...")
        try:
            browser.quit()
        except:
            pass

# -----------------RUN PREPROCESSING AUTOMATICALLY-----------------
print("\n=== MEMULAI PREPROCESSING REVIEW ===\n")
try:
    result = subprocess.run(
        ["python", r"C:\xampp\htdocs\TA\Program\prediction_shopee.py"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    print("\n=== PREPROCESSING SELESAI ===")
except Exception as e:
    print("Gagal menjalankan preprocessing:", e)