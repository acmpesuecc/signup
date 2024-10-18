import sqlite3
 
def is_table_empty(table_name):
    # Connect to the SQLite database
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()

    # Query to count the number of rows in the table
    query = f"SELECT COUNT(*) FROM {table_name}"
    
    try:
        # Execute the count query
        c.execute(query)
        count = c.fetchone()[0]  # Fetch the result of the count query
        
        # Query to select all rows from the table
        c.execute(f"SELECT * FROM {table_name}")
        rows = c.fetchall()
        
        # Print all rows
        for row in rows:
            print(row)
        
        # Check if the table is empty or not
        if count == 0:
            print(f"The table '{table_name}' is empty.")
        else:
            print(f"The table '{table_name}' contains {count} record(s).")
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
    
    # Close the connection
    conn.close()

# Example usage:
is_table_empty('users')  # Replace 'users' with the desired table name
