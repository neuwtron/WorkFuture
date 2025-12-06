import requests
import datetime
import mysql.connector


# ============================================================
# 1. EXTRACT REDDIT POST + COMMENTS
# ============================================================

def extract_reddit_post_and_comments(url, topic=None, location=None):
    headers = {"User-Agent": "windows:reddit-scraper:0.1 (by /u/yourusername)"}

    # Clean URL
    url = url.strip()
    if not url.startswith("http"):
        raise ValueError("URL must start with http:// or https://")

    if not url.endswith(".json"):
        if url.endswith("/"):
            url = url[:-1]
        url += ".json"

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    # -------- MAIN POST --------
    post_data = data[0]["data"]["children"][0]["data"]
    timestamp = post_data["created_utc"]
    post_date = datetime.datetime.utcfromtimestamp(timestamp).isoformat()

    post_output = {
        "dates": post_date,
        "platform": "Reddit",
        "texts": (post_data.get("title") or "") + "\n\n" + (post_data.get("selftext") or ""),
        "sentiment_score": None,
        "topic": topic,
        "location": location,
        "engagement": None
    }

    # -------- COMMENTS --------
    comments_list = []

    def extract_comment_tree(comment_nodes):
        for node in comment_nodes:
            if node["kind"] != "t1":
                continue

            d = node["data"]

            comment_timestamp = d.get("created_utc")
            comment_date = (
                datetime.datetime.utcfromtimestamp(comment_timestamp).isoformat()
                if comment_timestamp else None
            )

            comments_list.append({
                "dates": comment_date,
                "platform": "Reddit",
                "texts": d.get("body", ""),
                "sentiment_score": None,
                "topic": topic,
                "location": location,
                "engagement": None
            })

            # recursive replies
            if isinstance(d.get("replies"), dict):
                extract_comment_tree(d["replies"]["data"]["children"])

    extract_comment_tree(data[1]["data"]["children"])

    return post_output, comments_list



# ============================================================
# 2. MYSQL CONNECTION
# ============================================================

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",          # change if needed
        password="password",  # change your MySQL password
        database="workfuture" # your DB name
    )



# ============================================================
# 3. SAVE POST (assign post_id = id)
# ============================================================

def save_post_to_db(post):
    db = connect_db()
    cursor = db.cursor()

    sql = """
        INSERT INTO scrape_results (dates, platform, texts, sentiment_score, topic, location, engagement)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    vals = (
        post["dates"],
        post["platform"],
        post["texts"],
        post["sentiment_score"],
        post["topic"],
        post["location"],
        post["engagement"]
    )

    cursor.execute(sql, vals)
    db.commit()

    post_id = cursor.lastrowid


    cursor.close()
    db.close()

    return post_id



# ============================================================
# 4. SAVE COMMENTS WITH post_id
# ============================================================

def save_comments_to_db(post_id, comments):
    db = connect_db()
    cursor = db.cursor()

    sql = """
        INSERT INTO comments
        (post_id, dates, platform, texts, sentiment_score, topic, location, engagement)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    for c in comments:
        vals = (
            post_id,
            c["dates"],
            c["platform"],
            c["texts"],
            c["sentiment_score"],
            c["topic"],
            c["location"],
            c["engagement"]
        )
        cursor.execute(sql, vals)

    db.commit()
    cursor.close()
    db.close()



# ============================================================
# 5. MAIN EXECUTION
# ============================================================

if __name__ == "__main__":
    reddit_url = input("Paste Reddit URL: ").strip()

    topic = input("Enter topic: ").strip() or None
    location = input("Enter location (city, region, or country): ").strip() or None

    print("\nExtracting...")
    post, comments = extract_reddit_post_and_comments(
        reddit_url,
        topic=topic,
        location=location
    )

    print("Saving post...")
    post_id = save_post_to_db(post)

    print(f"Saving {len(comments)} comments...")
    save_comments_to_db(post_id, comments)

    print("\n✅ Done! All data saved with post_id =", post_id)
