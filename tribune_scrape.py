import requests
from bs4 import BeautifulSoup
import datetime
import mysql.connector


# ============================================================
# 1. MYSQL CONNECTION (same as your Reddit script)
# ============================================================

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",          # change if needed
        password="password",  # your MySQL password
        database="workfuture" # your database
    )


# ============================================================
# 2. EXTRACT NEWS ARTICLE
# ============================================================

def extract_news_article(url, topic=None, location=None):
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")

    # ---------- PLATFORM ----------
    platform = url.split("/")[2]  # domain name

    # ---------- DATE ----------
    # Try to extract date from URL (/2025/10/27/)
    date = None
    parts = url.split("/")
    for i, p in enumerate(parts):
        if len(p) == 4 and p.isdigit():  # year
            try:
                year = int(parts[i])
                month = int(parts[i + 1])
                day = int(parts[i + 2])
                date = datetime.date(year, month, day)
                break
            except:
                pass

    if not date:
        date = datetime.date.today()

    # ---------- TITLE ----------
    h1 = soup.find("h1")
    title = h1.get_text(strip=True) if h1 else "NO_TITLE"

    # ---------- ARTICLE BODY ----------
    selectors = [
        ".story-body", ".article-body",   # Chicago Tribune
        "article",                        # Block Club
        ".story-content", ".body-copy"    # Crain’s
    ]

    text = ""

    for sel in selectors:
        block = soup.select_one(sel)
        if block:
            paragraphs = block.find_all("p")
            text = "\n".join(p.get_text(strip=True) for p in paragraphs)
            if text.strip():
                break

    # fallback = all paragraphs
    if not text.strip():
        text = "\n".join(p.get_text(strip=True) for p in soup.find_all("p"))

    # ---------- COMPOSE FINAL TEXT ----------
    full_text = title + "\n\n" + text

    # ---------- STRUCTURE MATCHING REDDIT FORMAT ----------
    return {
        "dates": date.isoformat(),
        "platform": platform,
        "texts": full_text,
        "sentiment_score": None,
        "topic": topic,
        "location": location,
        "engagement": None
    }


# ============================================================
# 3. SAVE ARTICLE TO DB (same pattern as save_post_to_db)
# ============================================================

def save_news_to_db(article):
    db = connect_db()
    cursor = db.cursor()

    sql = """
        INSERT INTO scrape_results
        (dates, platform, texts, sentiment_score, topic, location, engagement)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    vals = (
        article["dates"],
        article["platform"],
        article["texts"],
        article["sentiment_score"],
        article["topic"],
        article["location"],
        article["engagement"]
    )

    cursor.execute(sql, vals)
    db.commit()

    post_id = cursor.lastrowid  # same logic as Reddit script

    cursor.close()
    db.close()

    return post_id



# ============================================================
# 4. MAIN EXECUTION
# ============================================================

if __name__ == "__main__":
    url = input("Paste News URL: ").strip()

    topic = input("Enter topic: ").strip() or None
    location = input("Enter location (city, region, or country): ").strip() or None

    print("\nExtracting article...")
    article = extract_news_article(url, topic=topic, location=location)

    print("Saving to database...")
    post_id = save_news_to_db(article)

    print("\n✅ Done! Saved with post_id =", post_id)
