import mysql.connector
import re

# ------------------------------
# CONNECT TO DATABASE
# ------------------------------
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="workfuture"
    )

# ------------------------------
# TOPIC RULES
# ------------------------------
LIVING_KEYWORDS = ["rent", "housing", "apartment", "homeless", "eviction", "living", "city", "train"]
JOB_KEYWORDS = ["jobs", "hiring", "career", "employment", "salary", "wages", "work", "job", "business"]

def detect_topic(text):
    text = text.lower()

    if any(word in text for word in LIVING_KEYWORDS):
        return "Living"
    if any(word in text for word in JOB_KEYWORDS):
        return "Jobs"
    return None  # remain NULL if no match

# ------------------------------
# PROCESS BATCH
# ------------------------------
BATCH_SIZE = 500

def process_batch(offset):
    db = connect_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, texts
        FROM scrape_results
        WHERE topic IS NULL
        LIMIT %s OFFSET %s
    """, (BATCH_SIZE, offset))

    rows = cursor.fetchall()
    if not rows:
        return False

    for row in rows:
        topic = detect_topic(row["texts"])

        cursor.execute("""
            UPDATE scrape_results
            SET topic = %s
            WHERE id = %s
        """, (topic, row["id"]))

        print(f"Updated id={row['id']} → topic={topic}")

    db.commit()
    cursor.close()
    db.close()
    return True

# ------------------------------
# MAIN
# ------------------------------
if __name__ == "__main__":
    offset = 0
    while process_batch(offset):
        offset += BATCH_SIZE

    print("🎉 Topic assignment complete!")
