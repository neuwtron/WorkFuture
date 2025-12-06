import mysql.connector
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

BATCH_SIZE = 500  # tune based on DB size

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="workfuture"
    )

def get_sentiment_score(text):
    """Return the VADER compound sentiment float (-1 to +1)."""
    analyzer = SentimentIntensityAnalyzer()
    return analyzer.polarity_scores(text)["compound"]

def process_batch(offset):
    db = connect_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, texts FROM scrape_results LIMIT %s OFFSET %s",
        (BATCH_SIZE, offset)
    )
    rows = cursor.fetchall()

    if not rows:
        print("No more rows.")
        return False

    for row in rows:
        score = get_sentiment_score(row["texts"])  # <-- now a float, not a label

        update_sql = """
            UPDATE scrape_results
            SET sentiment_score = %s
            WHERE id = %s
        """
        cursor.execute(update_sql, (score, row["id"]))
        print(f"Updated id={row['id']} -> {score}")

    db.commit()
    cursor.close()
    db.close()
    return True

if __name__ == "__main__":
    offset = 0
    while process_batch(offset):
        offset += BATCH_SIZE

    print("Sentiment analysis complete — float scores stored successfully!")
