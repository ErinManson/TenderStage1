import mariadb
import sys
from transformers import pipeline

def connect_to_db():
    try:
        conn = mariadb.connect(
            user="erinpy",
            password="tendercode",
            host="192.168.111.250",
            port=3306,
            database="ustenders"
        )
        return conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

def fetch_tenders():
    conn = connect_to_db()
    cur = conn.cursor()

    query = "SELECT id, title, description FROM rss_tenders WHERE pdflinks != '[]'"
    try:
        cur.execute(query)
        results = cur.fetchall()
        tenders = [(row[0], row[1], row[2]) for row in results]
        return tenders
    except mariadb.Error as e:
        print(f"Error: {e}")
        return []
    finally:
        conn.close()

def score_tenders(tenders):
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    label = "purchase of office furniture pieces"
    
    scored_tenders = []
    for tender_id, title, description in tenders:
        text = f"Title: {title}\nDescription: {description}"
        result = classifier(text, candidate_labels=[label])
        score = result['scores'][0] * 10  # Scale the score to be out of 10
        scored_tenders.append((tender_id, score))
    
    return scored_tenders

def update_scores(scored_tenders):
    conn = connect_to_db()
    cur = conn.cursor()

    try:
        for tender_id, score in scored_tenders:
            cur.execute("UPDATE rss_tenders SET score = ? WHERE id = ?", (score, tender_id))
        conn.commit()
    except mariadb.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()

# Main function to fetch, score, and update tenders
def main():
    tenders = fetch_tenders()
    scored_tenders = score_tenders(tenders)
    update_scores(scored_tenders)

# Example usage
if __name__ == "__main__":
    main()
    print("Scores have been updated.")
