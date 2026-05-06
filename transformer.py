from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import csv

driver = webdriver.Chrome()

driver.get("https://news.ycombinator.com/")
time.sleep(3)

titles = driver.find_elements(By.CLASS_NAME, "titleline")
subtexts = driver.find_elements(By.CLASS_NAME, "subtext")

data = []

for i in range(len(titles)):
    
    title = titles[i].text
    link = titles[i].find_element(By.TAG_NAME, "a").get_attribute("href")
    
    try:
        points = subtexts[i].find_element(By.CLASS_NAME, "score").text
    except:
        points = "0"
        
    try:
        author = subtexts[i].find_element(By.CLASS_NAME, "hnuser").text
    except:
        author = "unknown"
        
    try:
        time_posted = subtexts[i].find_element(By.CLASS_NAME, "age").text
    except:
        time_posted = "unknown"
    
    data.append([i+1, title, link, points, author, time_posted])

with open("hacker_news_full.csv", "w", newline="", encoding="utf-8-sig") as f:
    
    writer = csv.writer(f)
    
    writer.writerow([
        "№",
        "Заголовок",
        "Посилання",
        "Рейтинг",
        "Автор",
        "Час публікації"
    ])
    
    writer.writerows(data)

driver.quit()

print("Дані успішно збережені!")