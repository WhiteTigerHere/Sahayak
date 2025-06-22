import mysql.connector

# Database connection details
DB_CONFIG = {
    "host": "localhost",      # Change if using a remote server
    "user": "root",           # Change to your MySQL username
    "password": "",# Change to your MySQL password
    "database": "UserDB"
}

def connect_db():
    """Establishes a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("Connected to the database successfully!")
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    

def python_to_sql_datetime(python_datetime):
    """Converts a Python datetime object to MySQL compatible datetime format (YYYY-MM-DD HH:MM:SS)."""
    if isinstance(python_datetime, datetime):
        return python_datetime.strftime('%Y-%m-%d %H:%M:%S')
    else:
        raise ValueError("Input must be a datetime object")

def create_user(username, email, phone_number, password_hash, dob, gender):
    """Inserts a new user into the users table."""
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        query = """
        INSERT INTO users (username, email, phone_number, password_hash, date_of_birth, gender)
        VALUES (%s, %s, %s, %s, %s,%s)
        """
        try:
            cursor.execute(query, (username, email, phone_number, password_hash, dob, gender))
            conn.commit()
            print("User created successfully!")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

def get_user(user_id):
    """Fetches user details from the database based on user_id."""
    conn = connect_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT username, email, phone_number, date_of_birth, gender FROM users WHERE id = %s"
        try:
            cursor.execute(query, (user_id,))
            user = cursor.fetchone()
            if user:
                # Convert 'date_of_birth' from datetime.date to a string in 'YYYY-MM-DD' format
                user["date_of_birth"] = user["date_of_birth"].strftime("%Y-%m-%d")
                return user
            return None
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None
        finally:
            cursor.close()
            conn.close()
    return None

def insert_chat(chat_id, user_id, message, sender):
    """Inserts a chat message into the chats table."""
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        query = """
        INSERT INTO chats (chat_id, user_id, message, sender)
        VALUES (%s, %s, %s, %s)
        """
        try:
            cursor.execute(query, (chat_id, user_id, message, sender))
            conn.commit()
            print("Chat message inserted successfully!")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()
import mysql.connector



def schedule_event(user_id, event_name, timestamp, duration, color="#ffc107", description=None, every_year=False):
    """Schedules an event for a specific user."""
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        query = """
            INSERT INTO events (user_id, event_name, timestamp, duration, color, description, everyYear)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        try:
            cursor.execute(query, (user_id, event_name, timestamp, duration, color, description, every_year))
            conn.commit()
            print("Event scheduled successfully!")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()


# Function to delete a scheduled event
def delete_event_by_id(event_id):
    """Deletes a scheduled event."""
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        query = "DELETE FROM events WHERE event_id = %s"
        try:
            cursor.execute(query, (event_id,))
            conn.commit()
            print(f"Event {event_id} deleted successfully!")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()


def delete_event_by_name(user_id, event_name):
    """Deletes an event based on the event_name and user_id."""
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        query = """
            DELETE FROM events
            WHERE user_id = %s AND event_name = %s
        """
        try:
            cursor.execute(query, (user_id, event_name))
            conn.commit()
            if cursor.rowcount > 0:
                print(f"Event '{event_name}' deleted successfully!")
            else:
                print(f"No event found with the name '{event_name}' for user {user_id}.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()


# Function to list events for a user within a specific time period
def list_user_events(user_id, start_time, end_time):
    """Lists all events for a user within a specific time period."""
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        query = """
            SELECT event_id, event_name, timestamp, duration
            FROM events
            WHERE user_id = %s AND timestamp BETWEEN %s AND %s
            ORDER BY timestamp ASC
        """
        try:
            cursor.execute(query, (user_id, start_time, end_time))
            events = cursor.fetchall()
            if events:
                for event in events:
                    print(f"Event ID: {event[0]}, Name: {event[1]}, Time: {event[2]}, Duration: {event[3]} minutes")
            else:
                print("No events found for the specified time period.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()
            



def get_user_events_today(user_id):
    """Fetches all events for a specific user that are scheduled for the current day."""
    conn = connect_db()
    events_data = []
    
    if conn:
        cursor = conn.cursor()
        query = """
            SELECT event_id, event_name, timestamp, duration, color, description, everyYear
            FROM events
            WHERE user_id = %s AND DATE(timestamp) = CURDATE()
            ORDER BY timestamp ASC
        """
        try:
            cursor.execute(query, (user_id,))
            events = cursor.fetchall()

            if events:
                for event in events:
                    event_details = {
                        "event_id": event[0],
                        "event_name": event[1],
                        "timestamp": event[2].strftime('%Y-%m-%d %H:%M:%S'),
                        "duration": event[3],
                        "color": event[4],
                        "description": event[5] if event[5] else "",
                        "everyYear": event[6]
                    }
                    events_data.append(event_details)
            else:
                print(f"No events found for user {user_id} today.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    return events_data


def get_user_id(username):
    """
    Fetches the user ID from the database based on the username.
    """
    try:
        # Connect to the database
        conn = connect_db()
        cursor = conn.cursor()

        # Query to find the user ID
        query = "SELECT id FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()  # Get the first matching record

        # Close the connection
        cursor.close()
        conn.close()

        # Return user ID if found, else None
        return result[0] if result else None

    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return None

def delete_chat_from_db(chat_id, user_id):
    """
    Deletes a chat from the database based on chat_id and user_id.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Query to delete the chat for the given user_id and chat_id
        query = "DELETE FROM chats WHERE chat_id = %s AND user_id = %s"
        cursor.execute(query, (chat_id, user_id))
        conn.commit()

        cursor.close()
        conn.close()

        return True

    except mysql.connector.Error as e:
        print(f"Error deleting chat: {e}")
        return False


def get_distinct_chat_ids(user_id):
    """
    Fetches all distinct chat IDs for a given user ID from the database.
    """
    try:
        # Connect to the database
        conn = connect_db()
        cursor = conn.cursor()

        # Query to find distinct chat IDs
        query = "SELECT DISTINCT chat_id FROM chats WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()  # Fetch all matching records

        # Close the connection
        cursor.close()
        conn.close()

        # Return a list of distinct chat IDs if found, else an empty list
        return [row[0] for row in results] if results else []

    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return []
    
def get_latest_free_chat_id(user_id):
    """
    Finds and returns the latest free chat ID for a given user, which is 1 greater than the highest chat ID.
    """
    # Fetch all distinct chat IDs for the user
    chat_ids = get_distinct_chat_ids(user_id)

    if chat_ids:
        # Find the highest chat ID
        highest_chat_id = max(chat_ids)
        # Return the next available chat ID (one greater than the highest)
        return highest_chat_id + 1
    else:
        # If no chat IDs exist for the user, return the first available ID (e.g., 1)
        return 1

def get_chats_by_chat_id_and_user_id(chat_id, user_id):
    """
    Fetches all chat messages for a given chat ID and user ID from the database.
    """
    try:
        # Connect to the database
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)  # Fetch results as dictionaries

        # Query to find all chats for the given chat_id and user_id
        query = """
            SELECT message_id, user_id, message, sender, timestamp 
            FROM chats 
            WHERE chat_id = %s AND user_id = %s 
            ORDER BY timestamp ASC
        """
        cursor.execute(query, (chat_id, user_id))
        results = cursor.fetchall()  # Fetch all matching records

        # Close the connection
        cursor.close()
        conn.close()

        # Return chat messages or an empty list if no messages found
        return results if results else []




# Example usage
if __name__ == "__main__":
    # Scheduling an event
    user_id = 1  # Replace with an actual user_id
    # event_name = "Team Meeting 2"
    # timestamp = python_to_sql_datetime(datetime.now())  # Make sure this is in 'YYYY-MM-DD HH:MM:SS' format
    # duration = 60  # Duration in minutes
    # schedule_event(user_id, event_name, timestamp, duration)

    # # Deleting an event


    create_user("JohnDoe", "john@example.com", "1234567890", "hashed_password","2004-01-01","Male")
    # insert_chat(1, "Hello, bot!", "user")
   
