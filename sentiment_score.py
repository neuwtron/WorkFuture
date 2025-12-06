import mysql.connector
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

BATCH_SIZE = 500  #based on db size

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="workfuture"
    )

def label_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    score = analyzer.polarity_scores(text)["compound"]

    if score >= 0.05:
        return "positive"
    elif score <= -0.05:
        return "negative"
    else:
        return "neutral"

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
        return False  # end

    for row in rows:
        sentiment = label_sentiment(row["texts"])

        update_sql = """
            UPDATE scrape_results
            SET sentiment_score = %s
            WHERE id = %s
        """
        cursor.execute(update_sql, (sentiment, row["id"]))
        print(f"Updated id={row['id']} -> {sentiment}")

    db.commit()
    cursor.close()
    db.close()
    return True

if __name__ == "__main__":
    offset = 0
    while process_batch(offset):
        offset += BATCH_SIZE

    print("Sentiment analysis complete — labels stored successfully!")
