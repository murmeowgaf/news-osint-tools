import requests
import pandas as pd
import matplotlib.pyplot as plt
import socket
import json
from urllib.parse import urlparse
from collections import Counter

API_KEY = "YOUR_API_KEY"
IPINFO_TOKEN = "YOUR_KEY"
results = []


def get_ip_info(url):
    try:
        domain = urlparse(url).netloc
        ip = socket.gethostbyname(domain)
        org, country = None, None

        if IPINFO_TOKEN:
            resp = requests.get(f"https://ipinfo.io/{ip}?token={IPINFO_TOKEN}").json()
            org = resp.get("org")
            country = resp.get("country")

        return domain, ip, org, country
    except:
        return None, None, None, None


def search_news(query):
    url = f"https://newsapi.org/v2/everything?q={query}&language=ru&pageSize=50&sortBy=publishedAt&apiKey={API_KEY}"
    resp = requests.get(url).json()
    if resp.get("status") != "ok":
        print(f"[-] Ошибка для '{query}':", resp)
        return []
    return resp.get("articles", [])


# Ввод ключевых слов
user_input = input("Введите ключевые слова через запятую: ")
queries = [q.strip() for q in user_input.split(",") if q.strip()]

for q in queries:
    print(f"\n=== Поиск по ключу: {q} ===")
    arts = search_news(q)
    if not arts:
        print("[-] Ничего не найдено.")
        continue

    for art in arts:
        domain, ip, org, country = get_ip_info(art.get("url", ""))
        results.append(
            {
                "keyword": q,
                "title": art.get("title"),
                "url": art.get("url"),
                "source": art["source"].get("name"),
                "author": art.get("author"),
                "publishedAt": art.get("publishedAt"),
                "description": art.get("description"),
                "domain": domain,
                "ip": ip,
                "org": org,
                "country": country,
            }
        )

        print(f"\n[+] {art.get('title')}")
        print(f"    URL: {art.get('url')}")
        print(f"    Источник: {art['source'].get('name')}")
        if art.get("author"):
            print(f"    Автор: {art.get('author')}")
        print(f"    Дата: {art.get('publishedAt')}")
        if art.get("description"):
            print(f"    Описание: {art.get('description')}")
        if domain and ip:
            print(
                f"    Домен: {domain}, IP: {ip}, Организация: {org}, Страна: {country}"
            )

# Сохранение и анализ
if results:
    df = pd.DataFrame(results)
    df["publishedAt"] = pd.to_datetime(df["publishedAt"])
    df["date"] = df["publishedAt"].dt.date

    # Сохраняем CSV и JSON
    df.to_csv("osint_results.csv", index=False, encoding="utf-8")
    with open("osint_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n[*] Результаты сохранены в osint_results.csv и osint_results.json")

    # Топ-5 источников
    top_sources = Counter(df["source"]).most_common(5)
    print("\n=== Топ-5 источников ===")
    for src, count in top_sources:
        print(f"{src}: {count} статей")

    # График публикаций по дням
    counts = df.groupby("date").size()
    plt.figure(figsize=(10, 5))
    counts.plot(kind="bar", color="skyblue", edgecolor="black")
    plt.title("Количество статей по дням")
    plt.xlabel("Дата")
    plt.ylabel("Число статей")
    plt.tight_layout()
    plt.savefig("timeline.png")
    plt.show()
    print("[*] График сохранён в timeline.png")

    # Markdown-отчёт
    with open("osint_report.md", "w", encoding="utf-8") as f:
        f.write("# OSINT Report\n\n")
        f.write("## Топ-5 источников\n")
        for src, count in top_sources:
            f.write(f"- **{src}**: {count} статей\n")
        f.write("\n## Примеры статей\n")
        for art in results[:5]:
            f.write(
                f"- [{art['title']}]({art['url']}) ({art['source']}, {art['publishedAt']})\n"
            )
    print("[*] Markdown отчёт сохранён в osint_report.md")
else:
    print("[-] Ничего не собрано.")
