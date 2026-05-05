import pymysql
from app.config import settings

def create_db_if_not_exists():
    try:
        # Connect to MySQL server (without specifying a database)
        connection = pymysql.connect(
            host=settings.MYSQL_SERVER,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            port=int(settings.MYSQL_PORT)
        )
        
        try:
            with connection.cursor() as cursor:
                # Create database if it doesn't exist
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.MYSQL_DB}")
                print(f"✅ Database '{settings.MYSQL_DB}' checked/created successfully.")
        finally:
            connection.close()
            
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        exit(1)

if __name__ == "__main__":
    create_db_if_not_exists()
