
from googleapiclient.discovery import build
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os



API_KEY = "AIzaSyA0eTLB2ITthzKYa98_RCGOhTLr8JSh67E"

CHANNEL_ID = "UC_x5XG1OV2P6uZZ5FSM9Ttw"

MAX_RESULTS = 20


# Підключення до YOUTUBE API


youtube = build(
    'youtube',
    'v3',
    developerKey=API_KEY
)

print("Підключення до YouTube API успішне")


# Отримання списку відео


request = youtube.search().list(
    part='snippet',
    channelId=CHANNEL_ID,
    maxResults=MAX_RESULTS,
    order='date',
    type='video'
)

response = request.execute()

print("Дані з API отримано!")


# Створення списку даних


videos = []


for item in response['items']:

    video_id = item['id']['videoId']

    title = item['snippet']['title']

    published = item['snippet']['publishedAt']

  
    # Отримання статистики відео
 

    stats_request = youtube.videos().list(
        part='statistics',
        id=video_id
    )

    stats_response = stats_request.execute()

    stats = stats_response['items'][0]['statistics']

    views = int(stats.get('viewCount', 0))

    likes = int(stats.get('likeCount', 0))

    comments = int(stats.get('commentCount', 0))

    videos.append({
        'Title': title,
        'Published': published,
        'Views': views,
        'Likes': likes,
        'Comments': comments,
        'VideoID': video_id
    })


# Створення DATAFRAME


df = pd.DataFrame(videos)

print("\nПочатковий DataFrame:")
print(df)


# Аналіз структури даних


print("\nІнформація про DataFrame:")

print(df.info())

print("\nСтатистика:")

print(df.describe())


# Очищення даних


df.dropna(inplace=True)

print("\nПорожні значення видалено!")


# Перетворення дати


df['Published'] = pd.to_datetime(df['Published'])

print("\nДата перетворена!")


# Додавання нових стовпців


df['Year'] = df['Published'].dt.year

df['Month'] = df['Published'].dt.month

df['Popularity'] = df['Likes'] + df['Comments']

print("\nНові стовпці додано!")


# Фільтрація даних


filtered_df = df[df['Views'] > 1000]

print("\nВідфільтровані дані:")
print(filtered_df)


# Групування даних 


grouped = filtered_df.groupby('Month')['Views'].sum()

print("\nГрупування по місяцях:")
print(grouped)


# Сортування даних


sorted_df = filtered_df.sort_values(
    by='Views',
    ascending=False
)

print("\nВідсортовані дані:")
print(sorted_df)


# Пошук найпопулярнішого відео


top_video = sorted_df.head(1)

print("\nНайпопулярніше відео:")
print(top_video[['Title', 'Views']])


# Середнє значення переглядів


average_views = filtered_df['Views'].mean()

print(f"\nСередня кількість переглядів: {average_views}")


# Створення папки OUTPUT


if not os.path.exists('output'):
    os.makedirs('output')


# Збереження CSV


filtered_df.to_csv(
    'output/youtube_data.csv',
    index=False,
    encoding='utf-8-sig'
)

print("\nCSV файл успішно збережено!")

top_videos = df.sort_values(
    by='Views',
    ascending=False
).head(10)


top_videos = df.sort_values(
    by='Views',
    ascending=False
).head(5)


# Побудова графіка

top_videos['ShortTitle'] = (
    top_videos['Title'].str[:25] + '...'
)

x = np.arange(len(top_videos))

width = 0.35

plt.figure(figsize=(14, 7))

plt.bar(
    x - width/2,
    top_videos['Likes'],
    width,
    label='Лайки'
)

plt.bar(
    x + width/2,
    top_videos['Comments'],
    width,
    label='Коментарі'
)

plt.xticks(
    x,
    top_videos['ShortTitle'],
    rotation=10
)

plt.title('Порівняння лайків та коментарів')

plt.xlabel('Відео')

plt.ylabel('Кількість')

plt.legend()

plt.tight_layout()

plt.savefig('output/chart.png')

plt.show()

print("\nГрафік успішно збережено")


print("\nРоботу DATA PIPELINE Завершено")