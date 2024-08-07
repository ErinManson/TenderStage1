import mariadb
import sys

def update_manual_check(id):
    # Database connection information
    db_config = {
        'user': 'erinpy',
        'password': 'tendercode',
        'host': '192.168.111.250',
        'port': 3306,
        'database': 'ustenders'
    }

    # Connect to the database
    try:
        conn = mariadb.connect(**db_config)
        cursor = conn.cursor()
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        sys.exit(1)

    # Update the manual_check attribute to 1 for the given id
    update_query = "UPDATE rss_tenders SET manual_check = ? WHERE id = ?"
    try:
        cursor.execute(update_query, (1, id))
        conn.commit()
        print(f"manual_check for id {id} updated successfully")
    except mariadb.Error as e:
        print(f"Error updating manual_check for id {id}: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        id = int(sys.argv[1])
        update_manual_check(id)
"""     else:
        print("Usage: python update_manual_check.py <id>")
        
        # Test line for manual testing
        # Uncomment the line below to test without command-line arguments
        update_manual_check(228) """
