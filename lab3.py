import requests
import json

API_KEY = "AIzaSyA0eTLB2ITthzKYa98_RCGOhTLr8JSh67E"

# 1️⃣ Пошук відео (ігрова тематика)
search_url = "https://www.googleapis.com/youtube/v3/search"

search_params = {
    "part": "snippet",
    "q": "gaming",
    "type": "video",
    "maxResults": 5,
    "key": API_KEY
}

search_response = requests.get(search_url, params=search_params)
search_data = search_response.json()

video_ids = []

print("\nЗнайдені відео:\n")

for item in search_data["items"]:
    video_id = item["id"]["videoId"]
    title = item["snippet"]["title"]
    
    video_ids.append(video_id)
    
    print("Назва:", title)
    print("ID:", video_id)
    print("-" * 40)

# 2️⃣ Отримання статистики

videos_url = "https://www.googleapis.com/youtube/v3/videos"

videos_params = {
    "part": "snippet,statistics",
    "id": ",".join(video_ids),
    "key": API_KEY
}

videos_response = requests.get(videos_url, params=videos_params)
videos_data = videos_response.json()

results = []

print("\nСтатистика відео:\n")

for item in videos_data["items"]:
    title = item["snippet"]["title"]
    channel = item["snippet"]["channelTitle"]
    
    views = item["statistics"].get("viewCount", "0")
    likes = item["statistics"].get("likeCount", "0")
    comments = item["statistics"].get("commentCount", "0")

    video_info = {
        "title": title,
        "channel": channel,
        "views": int(views),
        "likes": int(likes),
        "comments": int(comments)
    }

    results.append(video_info)

    print("Назва:", title)
    print("Канал:", channel)
    print("Перегляди:", views)
    print("Лайки:", likes)
    print("Коментарі:", comments)
    print("-" * 40)

# 3️⃣ Збереження у файл

with open("youtube_data.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

print("\nДані збережено у файл youtube_data.json")


