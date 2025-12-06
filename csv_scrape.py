import pandas as pd
import mysql.connector


# ------------------------------------
# CONNECT TO MYSQL
# ------------------------------------
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",      # change this
        database="workfuture"
    )


# ------------------------------------
# CHECK IF TWEET URL ALREADY EXISTS
# ------------------------------------
def is_duplicate(tweet_link):
    db = connect_db()
    cursor = db.cursor()

    # We check duplicates by URL in the "texts" or create a separate "url" column.
    # Safer to search by text pattern match:
    sql = "SELECT COUNT(*) FROM scrape_results WHERE texts LIKE %s"
    cursor.execute(sql, (f"%{tweet_link}%",))

    count = cursor.fetchone()[0]
    cursor.close()
    db.close()

    return count > 0


# ------------------------------------
# INSERT A TWEET ROW INTO THE DATABASE
# ------------------------------------
def insert_tweet(row, topic=None, location=None):
    tweet_link = row["Tweet Link"]

    # skip if already inserted
    if is_duplicate(tweet_link):
        print(f"⏩ Skipped duplicate: {tweet_link}")
        return

    db = connect_db()
    cursor = db.cursor()

    sql = """
        INSERT INTO scrape_results
        (dates, platform, texts, sentiment_score, topic, location, engagement)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    # text = Tweet Content + URL included for tracking if needed
    full_text = f"{row['Tweet Content']}\n\nLink: {row['Tweet Link']}"

    values = (
        row["Tweet Creation Date"],   # dates
        "Twitter",                    # platform
        full_text,                    # texts
        None,                         # sentiment_score
        topic,                        # topic
        location,                     # location
        None,                         # engagement (unused)
    )

    cursor.execute(sql, values)
    db.commit()

    print(f"✅ Inserted: {tweet_link}")

    cursor.close()
    db.close()


# ------------------------------------
# IMPORT WHOLE CSV FILE
# ------------------------------------
def import_csv(csv_path, topic=None, location=None):
    df = pd.read_csv(csv_path)

    total = len(df)
    print(f"Found {total} tweets in CSV.\n")

    for i, row in df.iterrows():
        insert_tweet(row, topic, location)

    print("\n🔥 ALL DONE — CSV imported with duplicate skipping.")


# ------------------------------------
# MAIN
# ------------------------------------
if __name__ == "__main__":
    csv_path = input("Enter Twitter CSV file path: ").strip()
    topic = input("Topic (optional): ").strip() or None
    location = input("Location (optional): ").strip() or None

    import_csv(csv_path, topic, location)
