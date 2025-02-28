# import os
# import psycopg2
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# # Get database connection string from environment variables
# db_connection_string = os.getenv("DATABASE_URL")


# def delete_all_songs():
#     """
#     Delete all records from the songs table while preserving the table structure.
#     """
#     try:
#         # Connect to the PostgreSQL database
#         conn = psycopg2.connect(db_connection_string)

#         # Create a cursor object
#         cur = conn.cursor()

#         # Execute DELETE statement to remove all records from songs table
#         cur.execute("DELETE FROM songs;")

#         # Get the count of deleted rows (optional, for confirmation)
#         row_count = cur.rowcount

#         # Commit the transaction
#         conn.commit()

#         print(f"Successfully deleted {row_count} records from the songs table")

#     except psycopg2.Error as e:
#         print(f"An error occurred: {e}")
#         if conn:
#             conn.rollback()

#     finally:
#         # Close cursor and connection
#         if "cur" in locals():
#             cur.close()
#         if "conn" in locals():
#             conn.close()


# if __name__ == "__main__":
#     delete_all_songs()
