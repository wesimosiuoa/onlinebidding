import pymysql
from app.config import MYSQL_CONFIG
from flask import render_template

def get_db_connection():
    return pymysql.connect(**MYSQL_CONFIG)

def insert_user(user_type, name, email, password, phone, role_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO User (Name, Email, Password, roleID)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (name, email, password, role_id))
            user_id = cursor.lastrowid

            # Optionally insert into Seller or Bidder table
            if user_type == 'seller':
                cursor.execute("INSERT INTO Seller (USERID) VALUES (%s)", (user_id,))
            elif user_type == 'bidder':
                cursor.execute("INSERT INTO Bidder (USERID) VALUES (%s)", (user_id,))
            elif user_type == 'admin':
                cursor.execute("INSERT INTO Admin (USERID) VALUES (%s)", (user_id,))

            connection.commit()
            return user_id
    finally:
        connection.close()

def get_user_by_email(email):
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM User WHERE Email = %s"
            cursor.execute(sql, (email,))
            return cursor.fetchone()
    finally:
        connection.close()

def login_user(email, password):
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM User WHERE Email = %s AND Password = %s"
            cursor.execute(sql, (email, password))
            return cursor.fetchone()
        print("DEBUG: User returned from login_user:", user)
    finally:
        connection.close()

def insert_item(item_id, title, description, starting_price, end_time, is_auction_active, user_id, img):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO Item (ItemID, Title, Description, StartingPrice, EndTime, IsAuctionActive, UserID, Img)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (item_id, title, description, starting_price, end_time, is_auction_active, user_id, img))
            connection.commit()
    finally:
        connection.close()
        return True
def get_seller_items (user_id):
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM Item WHERE UserID = %s"
            cursor.execute(sql, (user_id,))
            return cursor.fetchall()
    finally:
        connection.close()

def all_items():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM `item` WHERE `isAuctionActive` = 1;")
            items = cursor.fetchall()
    finally:
        conn.close()
    
    return render_template('item_list.html', items=items)


def get_item_by_seller(user_id):
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM `item` WHERE USERID  = %s;", (user_id,))
            items = cursor.fetchall()
        return items
    finally:
        conn.close() 


#closed auction items
def get_closed_auction_items():
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM `item` WHERE `isAuctionActive` = 0;")
            items = cursor.fetchall()
        return items
    finally:
        conn.close()

# # CREATE TABLE `bid` (
#   `bidID` int(11) NOT NULL,
#   `itemID` int(11) NOT NULL,
#   `userID` int(11) NOT NULL,
#   `amount` decimal(10,2) NOT NULL,
#   `bidTime` datetime NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
def place_bid(item_id, user_id, amount):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO Bid (ItemID, UserID, Amount, BidTime)
                VALUES (%s, %s, %s, NOW())
            """
            cursor.execute(sql, (item_id, user_id, amount))
            connection.commit()
            print("DEBUG: Bid placed successfully for item:", item_id, "by user:", user_id)
    except pymysql.MySQLError as e:
        print(f"DEBUG: Error placing bid: {item_id}, {user_id}, {amount}", e)
        connection.rollback()
        return False
    finally:
        connection.close()
        return True
    #get_auction_by_item_and_seller
def get_auction_by_item_and_seller(user_id):
    connection = get_db_connection()
    try:
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        # cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT i.title, i.startingPrice, i.endTime, i.isAuctionActive, b.amount AS bidAmount, b.userID AS bidderID FROM item AS i LEFT JOIN bid AS b ON i.ItemID = b.ItemID where i.USERID = %s;", (user_id))
        items = cursor.fetchall()
        # with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        #     sql = """
        #         SELECT i.title, i.startingPrice, i.endTime, i.isAuctionActive, b.amount AS bidAmount, b.userID AS bidderID 
        #         FROM item AS i LEFT JOIN bid AS b ON i.ItemID = b.ItemID where i.USERID = %s;
        #     """
        # cursor.execute(sql, (user_id))
        return items
    except pymysql.MySQLError as e:
        print(f"DEBUG: Error fetching auction by item and seller for user {user_id}: {e}")
        return []
    finally:
        connection.close()                                                                                              
