from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time

data = []

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# відкриваємо сайт
driver.get("https://www.yakaboo.ua/")
time.sleep(3)

# 🔹 РОБОТА З ФОРМОЮ (пошук)
search = driver.find_element(By.NAME, "q")
search.send_keys("книги")  # що шукаємо
search.send_keys(Keys.RETURN)

time.sleep(5)

# 🔹 ЗБІР ДАНИХ
books = driver.find_elements(By.CSS_SELECTOR, "div[class*='product']")

for book in books[:10]:
    try:
        title = book.find_element(By.CSS_SELECTOR, "[class*='title']").text
        price = book.find_element(By.CSS_SELECTOR, "[class*='price']").text
        link = book.find_element(By.TAG_NAME, "a").get_attribute("href")

        # відкриваємо книгу для автора
        driver.get(link)
        time.sleep(3)

        try:
            author = driver.find_element(By.CSS_SELECTOR, "[class*='author']").text
        except:
            author = "Немає автора"

        data.append({
            "title": title,
            "author": author,
            "price": price
        })

        driver.back()
        time.sleep(2)

    except:
        continue

driver.quit()

# 🔹 ЗБЕРЕЖЕННЯ
with open("books.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["title", "author", "price"])
    writer.writeheader()
    writer.writerows(data)

print("Дані збережено")