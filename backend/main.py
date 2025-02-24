# from fastapi import FastAPI
# from crawler import fetch_all_articles,save_articles_to_json, classify_articles
# #from summarizer import summarize
# from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI()

# # Enable CORS for local development
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Adjust this in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.get("/")
# def home():
#     print("Home endpoint accessed")
#     return {"message": "Welcome to the AI News Agent!"}


# @app.get("/news")
# def get_news():
#     print("Fetching and summarizing articles...")
#     articles = fetch_all_articles()
#     print(f"Total Articles Fetched: {len(articles)}")
#     print("Articles fetched:")
#     classified_articles = classify_articles(articles)
#     save_articles_to_json(classified_articles)
#     print("Process completed successfully.")
#     summarized_articles = []

#     for article in articles:
#         summary = article.get("summary", "Content not available")  # Use "summary" instead of "content"

        
#         summarized_articles.append({
#             "title": article["title"],
#             "summary": summary,
#             "seo_title": f"SEO Optimized: {article['title']}",
#             "meta_description": f"Summary of {article['title']} - {summary[:150]}",
#             "keywords": ", ".join(article["title"].split()[:5]),
#             "link": article["link"]
#         })
#     return summarized_articles

from fastapi import FastAPI
from crawler import fetch_all_articles, save_articles_to_json, classify_articles
from fastapi.middleware.cors import CORSMiddleware
GEMINI_API_KEY = "AIzaSyBawWJl0BvJDMSxfQ15YcOY9fW3ZWzfwq4"
app = FastAPI()
import requests


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def summarize_with_gemini(text):
    # print(f"Summarizing with Gemini for text: {text}")
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": f"Summarize this news article briefly so that easily understand by humans what is this news. and if summary not available then create one news summary: {text}"}]}]
    }

    try:
        response = requests.post(f"{url}?key={GEMINI_API_KEY}", headers=headers, json=payload)
        response_data = response.json()
        
        if 'candidates' in response_data and len(response_data['candidates']) > 0:
            return response_data['candidates'][0]['content']['parts'][0]['text']
        else:
            return text
    except Exception as e:
        print(f"Error summarizing with Gemini: {e}")
        return "Summary not available."

@app.get("/")
def home():
    print("Home endpoint accessed")
    return {"message": "Welcome to the AI News Agent!"}

@app.get("/news")
def get_news():
    print("Fetching and summarizing articles...")
    articles = fetch_all_articles()
    print(f"Total Articles Fetched: {len(articles)}")

    classified_articles = classify_articles(articles)
    save_articles_to_json(classified_articles)
    
    summarized_articles = []

    #for article in classified_articles:
     #   summary = article.get("summary", "Content not available")

    for article in classified_articles:
        raw_summary = article.get("summary", "Content not available")
        gemini_summary = summarize_with_gemini(raw_summary)

        summarized_articles.append({
            "title": article["title"],
            "summary": gemini_summary,
            "seo_title": f"SEO Optimized: {article['title']}",
            "meta_description": f"Summary of {article['title']}",
            "keywords": ", ".join(article["title"].split()),
            "link": article["link"],
            "sub_topic": article.get("category", "Uncategorized")
        })
    print(f"Gemini Summary Summarised")
    return summarized_articles
