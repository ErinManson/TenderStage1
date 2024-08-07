import mariadb
import sys

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
    query = "SELECT id FROM rss_tenders rt WHERE rt.pdflinks != '[]' AND rt.score >= 4"

    # Execute the query
    try:
        cur.execute(query)
        # Fetch all results from the executed query
        results = cur.fetchall()
        # Process and return the results as a list of ids
        ids = [row[0] for row in results]
        return ids        

    except mariadb.Error as e:
        print(f"Error: {e}")
        return []

    finally:
        # Close the connection
        conn.close()

# Example usage
if __name__ == "__main__":
    ids = sql_main()
    print(ids)


