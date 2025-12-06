import mysql.connector
import re
import nltk
from nltk.corpus import stopwords

# ------------------------------------
# CONNECT
# ------------------------------------
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="workfuture"
    )

# ------------------------------------
# CLEANUP FUNCTION (modify this as needed)
# ------------------------------------
def clean_text(text):
    if text is None:
        return text

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", "", text)

    # Remove emojis
    text = text.encode('ascii', 'ignore').decode()

    # Lowercase
    text = text.lower()

    # Remove stopwords (English)
    stop_words = set(stopwords.words('english'))
    text = " ".join(word for word in text.split() if word not in stop_words)

    return text.strip()

# ------------------------------------
# MAIN CLEANER
# ------------------------------------
def clean_database_texts():
    db = connect_db()
    cursor = db.cursor(buffered=True)

    # Retrieve ONLY id + texts column
    cursor.execute("SELECT id, texts FROM scrape_results")

    rows = cursor.fetchall()
    print(f"Found {len(rows)} rows to clean.\n")

    update_sql = "UPDATE scrape_results SET texts = %s WHERE id = %s"

    for record in rows:
        row_id, original_text = record

        cleaned = clean_text(original_text)

        # Only update if text truly changed
        if cleaned != original_text:
            cursor.execute(update_sql, (cleaned, row_id))
            print(f"Updated row {row_id}")

    db.commit()
    cursor.close()
    db.close()

    print("\n🔥 DONE — All texts cleaned.")

# ------------------------------------
# RUN
# ------------------------------------
if __name__ == "__main__":
    clean_database_texts()
