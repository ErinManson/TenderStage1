import mariadb
import json
import os

# Database connection information
db_config = {
    'user': 'erinpy',
    'password': 'tendercode',
    'host': '192.168.111.250',
    'port': 3306,
    'database': 'ustenders'
}

def connect_to_database():
    try:
        conn = mariadb.connect(**db_config)
        cursor = conn.cursor()
        return conn, cursor
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        exit(1)

def process_files_in_directory(directory, cursor, conn):
    # Group files by their prefix
    file_groups = {}
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            prefix = filename.split('-')[0]
            if prefix not in file_groups:
                file_groups[prefix] = []
            file_groups[prefix].append(filename)

    # Loop through each group of files
    for prefix, files in file_groups.items():
        combined_data = []

        for filename in files:
            file_path = os.path.join(directory, filename)
            
            # Load the JSON file
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    json_data = json.load(file)
                    combined_data.append(json_data)
            else:
                raise FileNotFoundError(f"{file_path} does not exist")
        
        # Merge the JSON data
        merged_json_data = json.dumps(combined_data)
        
        # Update the JSON data in the rss_tenders table where id = prefix
        update_query = "UPDATE rss_tenders SET jsondata = ? WHERE id = ?"
        try:
            cursor.execute(update_query, (merged_json_data, prefix))
            conn.commit()
            print(f"Data for id {prefix} updated successfully")
            
            # Delete the original files
            for filename in files:
                file_path = os.path.join(directory, filename)
                os.remove(file_path)
                
        except mariadb.Error as e:
            print(f"Error updating data for id {prefix}: {e}")
            conn.rollback()

def cleanup_directory(directory):
    # Check if the directory is empty and delete it if it is
    if not os.listdir(directory):
        try:
            os.rmdir(directory)
            print(f"Directory '{directory}' has been deleted successfully.")
        except Exception as e:
            print(f"Error deleting directory '{directory}': {e}")
    else:
        print(f"Directory '{directory}' is not empty and will not be deleted.")

def main():
    # Directory containing the JSON files
    directory = 'JSONS'

    # Connect to the database
    conn, cursor = connect_to_database()

    # Process the files in the directory
    process_files_in_directory(directory, cursor, conn)

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Clean up the directory
    cleanup_directory(directory)

if __name__ == "__main__":
    main()
