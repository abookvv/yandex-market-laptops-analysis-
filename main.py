#pip install lxml
#pip install requests beautifulsoup4 pandas tqdm


import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm

url = "https://market.yandex.ru/search?text=ноутбук&rs=eJwzEv7EKMDBKLDwEKsEg0bjcVaN5908ADqfBf0%2C"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Запрос к странице
response = requests.get(url, headers=HEADERS)
soup = BeautifulSoup(response.text, "lxml")

# Поиск карточек товаров
items = soup.find_all("div", {"data-zone-name": "product-item"})  # (уточните класс!)

data = []
for item in tqdm(items[:20]):  # Парсим первые 20 для теста
    try:
        title = item.find("h3", {"data-zone-name": "title"}).text.strip()
        price = item.find("span", {"data-zone-name": "price"}).text.replace("₽", "").strip()
        rating = item.find("div", {"data-zone-name": "rating"}).text.strip() if item.find("div", {
            "data-zone-name": "rating"}) else "N/A"
        link = "https://market.yandex.ru" + item.find("a", {"data-zone-name": "title"})["href"]

        data.append({
            "Название": title,
            "Цена (руб)": price,
            "Рейтинг": rating,
            "Ссылка": link
        })
    except Exception as e:
        print(f"Ошибка при парсинге карточки: {e}")

# Сохраняем в CSV
df = pd.DataFrame(data)
df.to_csv("yandex_market_laptops.csv", index=False)
print("Данные сохранены!")