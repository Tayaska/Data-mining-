from googleapiclient.discovery import build
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report


API_KEY = "AIzaSyA0eTLB2ITthzKYa98_RCGOhTLr8JSh67E"

youtube = build('youtube', 'v3', developerKey=API_KEY)



def get_categories():
    request = youtube.videoCategories().list(
        part="snippet",
        regionCode="US"
    )
    response = request.execute()

    categories = {}

    for item in response['items']:
        categories[item['id']] = item['snippet']['title']

    return categories


category_dict = get_categories()


def get_videos(query="tutorial", max_results=30):

    request = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        maxResults=max_results
    )

    response = request.execute()

    video_ids = [item['id']['videoId'] for item in response['items']]

    stats_request = youtube.videos().list(
        part='statistics,snippet',
        id=','.join(video_ids)
    )

    stats_response = stats_request.execute()

    data = []

    for item in stats_response['items']:

        stats = item['statistics']
        snippet = item['snippet']
        category_id = snippet['categoryId']

        data.append({
            'title': snippet['title'],
            'views': int(stats.get('viewCount', 0)),
            'likes': int(stats.get('likeCount', 0)),
            'comments': int(stats.get('commentCount', 0)),
            'category': category_dict.get(category_id, "Unknown")
        })

    return pd.DataFrame(data)


df = get_videos("tutorial", 30)



# 1. ВІДОБРАЖЕННЯ ДАНИХ


pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

print("\nДані з YouTube:\n")
print(df.to_string(index=False))



# 2. ОЧИЩЕННЯ ДАНИХ


df = df.drop_duplicates()
df = df.dropna()

print("\nПропуски:\n", df.isnull().sum())



# 3. ПІДГОТОВКА ДАНИХ


features = df[['views', 'likes', 'comments']]

scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)



# 4. ВИБІР КІЛЬКОСТІ КЛАСТЕРІВ


inertia = []

for k in range(1, 8):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(scaled_features)
    inertia.append(kmeans.inertia_)

plt.figure()
plt.plot(range(1, 8), inertia, marker='o')
plt.title("Elbow method")
plt.xlabel("Number of clusters")
plt.ylabel("Inertia")
plt.show()



# 5. КЛАСТЕРИЗАЦІЯ


kmeans = KMeans(n_clusters=3, random_state=42)
df['cluster'] = kmeans.fit_predict(scaled_features)



# 6. АНАЛІЗ КЛАСТЕРІВ


print("\nСередні значення по кластерам:\n")
print(df.groupby('cluster')[['views', 'likes', 'comments']].mean())



# 7. КРОС-ТАБУЛЯЦІЯ


crosstab = pd.crosstab(df['category'], df['cluster'])

print("\nКрос-табуляція:\n")
print(crosstab)


# 8. ДИСТИЛЯЦІЯ ШАБЛОНІВ (ML)


X = df[['views', 'likes', 'comments']]
y = df['cluster']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("\nТочність моделі:", model.score(X_test, y_test))
print("\nЗвіт класифікації:\n")
print(classification_report(y_test, y_pred))



# 9. ЗБЕРЕЖЕННЯ РЕЗУЛЬТАТІВ


df.to_csv("youtube_analysis.csv", index=False)

print("\nДані збережено у файл youtube_analysis.csv")
