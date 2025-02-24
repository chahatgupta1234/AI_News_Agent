import requests
from bs4 import BeautifulSoup
import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def fetch_article_summary(article_url):
    #print(f"Fetching article content: {article_url}")
    try:
        response = requests.get(article_url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            return "Failed to fetch content"
        
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        full_text = " ".join([para.get_text(strip=True) for para in paragraphs])
        return full_text if full_text else "No content available"
    except Exception as e:
        print(f"Error fetching article summary: {e}")
        return "Error fetching content"


def fetch_bbc_articles():
    print("Fetching BBC articles...")
    url = "https://www.bbc.com/news/world/asia/india"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

    if response.status_code != 200:
        print("Failed to fetch BBC articles")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    articles = []

    for item in soup.find_all("a", class_="sc-2e6baa30-0 gILusN"):  # Fetch up to 10 articles
        title = item.get("aria-label")  # BBC sometimes stores titles in aria-label

        if not title:
            title_tag = item.find("h3") or item.find("span")  # Check <h3> and <span> as fallback
            title = title_tag.get_text(strip=True) if title_tag else "No Title"

        link = item['href']
        if not link.startswith("http"):
            link = "https://www.bbc.com" + link

        #print(f"Extracted Title: {title}, Link: {link}")  # Debugging to ensure title extraction works

        summary = fetch_article_summary(link)  # Fetch article summary
        articles.append({"title": title, "link": link, "summary": summary})

    print(f"Total BBC Articles Fetched: {len(articles)}")
    return articles


def fetch_indian_express_articles():
    print("Fetching Indian Express articles...")
    url = "https://indianexpress.com/latest-news/"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    
    if response.status_code != 200:
        print("Failed to fetch Indian Express articles")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    articles = []

    for item in soup.find_all("div", class_="articles"): 
        title_tag = item.find("h2")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        link = title_tag.find("a")['href']
        summary_tag = item.find("p")
        summary = summary_tag.get_text(strip=True) if summary_tag else "No summary available"

        articles.append({"title": title, "link": link, "summary": summary})
    
    return articles

def fetch_all_articles():
    articles = []
    articles.extend(fetch_indian_express_articles())
    articles.extend(fetch_bbc_articles())
    return articles

# def classify_articles(articles, num_clusters=5):
#     print("Classifying articles into sub-topics...")
#     summaries = [article['summary'] for article in articles]
#     # Check if summaries are empty
#     if not summaries:
#         print("No summaries found in articles.")
#         return articles
    
#     # Print summaries for debugging
#     for i, summary in enumerate(summaries):
#         print(f"Summary {i+1}: {summary}")
    
    
#     vectorizer = TfidfVectorizer(stop_words='english')
#     X = vectorizer.fit_transform(summaries)
    
#     kmeans = KMeans(n_clusters=num_clusters, random_state=42)
#     kmeans.fit(X)
#     labels = kmeans.labels_
    
#     for i, article in enumerate(articles):
#         article['sub_topic'] = f"Sub-topic {labels[i] + 1}"
    
#     return articles


def classify_articles(articles):
    print("Classifying articles into topics...")

    category_keywords = {
        "Sports": ["cricket", "football", "tennis", "NBA", "FIFA", "Olympics", "Champions Trophy"],
        "Politics": ["government", "minister", "election", "policy", "parliament", "BJP", "Congress"],
        "World News": ["global", "international", "world", "UN", "foreign", "USA"],
        "Crime": ["murder", "theft", "arrest", "fraud", "police", "investigation"],
        "India": ["Delhi", "Mumbai", "Bangalore", "India", "Kolkata", "Modi"]
    }

    for article in articles:
        assigned_category = "Uncategorized"  # Default if no match

        for category, keywords in category_keywords.items():
            if any(keyword.lower() in article["title"].lower() or keyword.lower() in article["summary"].lower() for keyword in keywords):
                assigned_category = category
                break  # Stop checking once a category is assigned

        article["category"] = assigned_category

    return articles



def save_articles_to_json(articles, filename="articles.json"):
    print(f"Saving articles to {filename}...")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)
