import mariadb
import sys
import json

def sql_main():
    # Connect to MariaDB Platform
    try:
        conn = mariadb.connect(
            user="erinpy",
            password="tendercode",
            host="192.168.111.250",
            port=3306,
            database="ustenders"
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    # Get Cursor
    cur = conn.cursor()

    # SQL Query to execute
    query = "SELECT pdflinks FROM rss_tenders rt WHERE rt.pdflinks != '[]' AND rt.score >= 4"

    # Execute the query
    try:
        cur.execute(query)
        # Fetch all results from the executed query
        results = cur.fetchall()
        # Process and return the results as a list of lists containing only PDF links
        pdf_urls = []
        for row in results:
            pdflinks = row[0]
            # Check if pdflinks is a JSON string
            if isinstance(pdflinks, str):
                try:
                    pdflinks = json.loads(pdflinks)
                except json.JSONDecodeError:
                    pass
            # Ensure it's a list
            if not isinstance(pdflinks, list):
                pdflinks = [pdflinks]
            pdf_urls.append(pdflinks)
        return pdf_urls        

    except mariadb.Error as e:
        print(f"Error: {e}")
        return []

    finally:
        # Close the connection
        conn.close()

# Example usage
if __name__ == "__main__":
    pdf_urls = sql_main()
    for i in pdf_urls:
        for j in i:
            print(j)
