# 1. ІМПОРТИ
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from googleapiclient.discovery import build

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from sklearn.cluster import KMeans

from mlxtend.frequent_patterns import apriori, association_rules

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities


# 2. ОТРИМАННЯ ДАНИХ (YouTube API)

API_KEY = "AIzaSyA0eTLB2ITthzKYa98_RCGOhTLr8JSh67E"

youtube = build("youtube", "v3", developerKey=API_KEY)

queries = ["game", "music", "sports", "technology", "education"]

videos = []

for q in queries:
    request = youtube.search().list(
        part="snippet",
        maxResults=10,
        q=q,
        type="video"
    )
    response = request.execute()
    videos += response["items"]

video_ids = [v["id"]["videoId"] for v in videos]

stats = youtube.videos().list(
    part="statistics,snippet",
    id=",".join(video_ids)
).execute()

data_list = []

for item in stats["items"]:
    data_list.append({
        "views": int(item["statistics"].get("viewCount", 0)),
        "likes": int(item["statistics"].get("likeCount", 0)),
        "category": item["snippet"]["categoryId"]
    })

data = pd.DataFrame(data_list)


# 🔹 Додаємо назви категорій
category_map = {
    "10": "Music",
    "17": "Sports",
    "20": "Gaming",
    "22": "People",
    "24": "Entertainment",
    "27": "Education",
    "28": "Technology"
}

data["category_name"] = data["category"].map(category_map)


# 3. ДОДАВАННЯ ОЗНАК

np.random.seed(42)

data["age"] = np.random.randint(16, 40, len(data))
data["watch_time"] = np.random.randint(5, 300, len(data))

scaler = MinMaxScaler()
data[["views", "likes", "watch_time"]] = scaler.fit_transform(
    data[["views", "likes", "watch_time"]]
)

prob = (
    0.4 * data["likes"] +
    0.4 * data["watch_time"] +
    0.2 * np.random.rand(len(data))
)

data["subscribe"] = (prob > prob.mean()).astype(int)


# 🔥 ЗБЕРІГАЄМО ФІНАЛЬНУ ТАБЛИЦЮ ДЛЯ ВИВОДУ
data_final = data.copy()


# 4. ПІДГОТОВКА ДАНИХ ДЛЯ МОДЕЛЕЙ

data_model = pd.get_dummies(data.drop("category_name", axis=1))

X = data_model.drop("subscribe", axis=1)
y = data_model["subscribe"]


# 5. ДЕРЕВО РІШЕНЬ

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = DecisionTreeClassifier(max_depth=4, min_samples_leaf=3, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

cm = confusion_matrix(y_test, y_pred)

if cm.shape == (2, 2):
    TN, FP, FN, TP = cm.ravel()
    sensitivity = TP / (TP + FN) if (TP + FN) > 0 else 0
    specificity = TN / (TN + FP) if (TN + FP) > 0 else 0
else:
    sensitivity = 0
    specificity = 0

print("\n=== DECISION TREE ===")
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Sensitivity:", sensitivity)
print("Specificity:", specificity)

plt.figure(figsize=(12, 6))
plot_tree(model, feature_names=X.columns, class_names=["No", "Yes"], filled=True)
plt.title("Decision Tree")
plt.show()


# 6. K-MEANS

scaler_k = StandardScaler()
X_kmeans = scaler_k.fit_transform(data_model[["age", "views"]])

kmeans = KMeans(n_clusters=3, random_state=42)
data_model["cluster"] = kmeans.fit_predict(X_kmeans)

plt.figure(figsize=(8, 5))
plt.scatter(data_model["age"], data_model["views"], c=data_model["cluster"])

centers = scaler_k.inverse_transform(kmeans.cluster_centers_)
plt.scatter(centers[:, 0], centers[:, 1], marker="X", s=200)

plt.title("K-means clustering")
plt.xlabel("Age")
plt.ylabel("Views")
plt.grid()
plt.show()


# 7. АСОЦІАТИВНІ ПРАВИЛА

assoc_data = data_model.filter(like="category_")

assoc_data["subscribe"] = data_model["subscribe"]

frequent = apriori(assoc_data, min_support=0.05, use_colnames=True)

print("\n=== ASSOCIATION RULES ===")

if not frequent.empty:
    rules = association_rules(frequent, metric="lift", min_threshold=1)
    
    if not rules.empty:
        print(rules.head())
    else:
        print("Правила не знайдені (але часті набори є)")
else:
    print("Недостатньо даних")

# 8. НАЇВНИЙ БАЙЄС

texts = [
    "action game is cool",
    "strategy game is hard",
    "sports game is fun",
    "action action game",
    "music is relaxing",
    "sports are exciting",
    "strategy games need thinking",
    "action games are fast",
    "education videos are useful",
    "technology is interesting"
]

labels = [1,0,1,1,1,1,0,1,0,0]

vectorizer = CountVectorizer()
X_text = vectorizer.fit_transform(texts)

X_train, X_test, y_train, y_test = train_test_split(
    X_text, labels, test_size=0.25, random_state=42
)

nb = MultinomialNB()
nb.fit(X_train, y_train)

pred = nb.predict(X_test)

cm = confusion_matrix(y_test, pred)

if cm.shape == (2, 2):
    TN, FP, FN, TP = cm.ravel()
    sensitivity = TP / (TP + FN) if (TP + FN) > 0 else 0
    specificity = TN / (TN + FP) if (TN + FP) > 0 else 0
else:
    sensitivity = 0
    specificity = 0

print("\n=== NAIVE BAYES ===")
print("Accuracy:", accuracy_score(y_test, pred))
print("Sensitivity:", sensitivity)
print("Specificity:", specificity)


# 9. ГРАФ 

import networkx as nx

G = nx.Graph()

# вузли
for i in range(len(data_model)):
    G.add_node(i)

# зв’язки по схожості
for i in range(len(data_model)):
    for j in range(i + 1, len(data_model)):
        
        age_diff = abs(data_model.loc[i, "age"] - data_model.loc[j, "age"])
        views_diff = abs(data_model.loc[i, "views"] - data_model.loc[j, "views"])
        
        # умова схожості
        if age_diff <= 3 and views_diff <= 0.1:
            G.add_edge(i, j)

# пошук спільнот
from networkx.algorithms.community import greedy_modularity_communities
communities = greedy_modularity_communities(G)

print("\n=== COMMUNITIES===")
print("Кількість спільнот:", len(communities))

# розфарбування по спільнотах
color_map = {}
for i, comm in enumerate(communities):
    for node in comm:
        color_map[node] = i

colors = [color_map[node] for node in G.nodes()]

# малювання графа
plt.figure(figsize=(7, 7))
pos = nx.spring_layout(G, seed=42)

nx.draw(
    G,
    pos,
    node_color=colors,
    cmap=plt.cm.Set1,
    node_size=80,
    with_labels=False
)

plt.title("Graph based on similarity (Age & Views)")
plt.show()

# 🔥 ФІНАЛЬНИЙ ВИВІД ДАНИХ (ДЛЯ ЗВІТУ)

print("\n=== FINAL DATA ===")
print(data_final[[
    "age",
    "views",
    "likes",
    "watch_time",
    "category_name",
    "subscribe"
]].head(20))