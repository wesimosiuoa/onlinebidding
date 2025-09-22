# utils/db_helper.py
import pymysql
from app.config import MYSQL_CONFIG
import app.users as users
from werkzeug.security import check_password_hash

def get_db_connection():
    conn = pymysql.connect(
        host=MYSQL_CONFIG['host'],
        user=MYSQL_CONFIG['user'],
        password=MYSQL_CONFIG['password'],
        db=MYSQL_CONFIG['database'],
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

def get_user_by_email(email):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM users WHERE email=%s"
            cursor.execute(sql, (email,))
            return cursor.fetchone()
    finally:
        conn.close()

# dbhelper.py
def insert_user(users: users.User):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO `users`
                (`user_id`, `first_name`, `last_name`, `email`, `password_hash`, `role`, `is_banned`, `created_at`)
                VALUES (NULL, %s, %s, %s, %s, %s, '0', current_timestamp())
            """
            cursor.execute(sql, (
                users.first_name,
                users.last_name,
                users.email,
                users.password,    # hashed password
                users.role_id      # here we use role_id property (seller/buyer)
            ))
        conn.commit()
    finally:
        conn.close()

def user_login(users: users.User):
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 1. Get user row by email
            sql = "SELECT * FROM users WHERE email = %s"
            cursor.execute(sql, (users.email,))
            user_row = cursor.fetchone()

            if user_row:  # user exists
                # 2. Check the hashed password against the entered one
                if check_password_hash(user_row['password_hash'], users.password):
                    return user_row  # login success
                else:
                    return None  # wrong password
            else:
                return None  # no such email
    finally:
        connection.close()

def get_user_by_email(email):
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM users WHERE email = %s"
            cursor.execute(sql, (email,))
            return cursor.fetchone()
    finally:
        connection.close()

def get_role_name(users : users.User):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT role FROM users WHERE email = %s"
            cursor.execute(sql, (users.email,))
            result = cursor.fetchone()
            if result:
                return result['role']
            else:
                return None
    finally:
        conn.close()

def get_item_by_seller(user_id):
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM `items` WHERE seller_id  = %s;", (user_id,))
            items = cursor.fetchall()
        return items
    finally:
        conn.close()