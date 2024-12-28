# import mysql.connector
import psycopg2


class Database:
    @staticmethod

    def get_bearer_token(session_id):
        # conn = get_db_connection()
        try:
            conn = psycopg2.connect(
              dbname='chatbot-database',
              password='$TT_Postgres_^2023$',
              user='postgres',
              host='tt-postgres-instance.c894lrepeoma.ap-south-1.rds.amazonaws.com',
              port='5432'
)
            cursor = conn.cursor()
            sql = "SELECT vendure_token FROM message_store WHERE session_id = %s"
            cursor.execute(sql, (session_id,))
            result = cursor.fetchone()
            # cursor.close()
            conn.close()
            return result[0] if result else None
        except Exception as e:
        # Handle any other exceptions
            print(f"An error occurred: {e}")
            return None
        # return result[0] if result else None

    @staticmethod
    def update_bearer_token(session_id, bearer_token):
        # conn = get_db_connection()
        try:
            conn = psycopg2.connect(
              dbname='chatbot-database',
              password='$TT_Postgres_^2023$',
              user='postgres',
              host='tt-postgres-instance.c894lrepeoma.ap-south-1.rds.amazonaws.com',
              port='5432'
)
            cursor = conn.cursor()
            sql = "UPDATE message_store SET vendure_token = %s WHERE session_id = %s"
            print("sql query",sql)
            print("eeeeeeeeeeeeeee",bearer_token,session_id)
            cursor.execute(sql, (bearer_token, session_id))
            print("DOOOOOONNNNEEEEEE",cursor)
            conn.commit()
            # cursor.close()
            conn.close()
        except Exception as e:
        # Handle any other exceptions
            print(f"An error occurred: {e}")



