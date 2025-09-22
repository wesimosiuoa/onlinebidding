from flask import Blueprint , current_app, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import os
from werkzeug.utils import secure_filename

from app.models import all_items, get_auction_by_item_and_seller, place_bid, get_closed_auction_items, insert_user, get_user_by_email, login_user, insert_item, get_item_by_seller, get_db_connection
from app.users import User
from app.item import Item
from app.models import get_db_connection
import pymysql 
from werkzeug.security import generate_password_hash
from app.db_helper import insert_user, user_login, get_user_by_email, get_role_name, get_item_by_seller


main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        confirm_password = request.form.get('confirm_password')
        # phone = request.form.get('phone')

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return render_template('register.html')

        # map user_type to role string
        role_map = {'seller': 'seller', 'bidder': 'buyer'}
        role = role_map.get(user_type)

        try:
            existing_user = get_user_by_email(email)
            if existing_user:
                flash("Email already registered!", "danger")
                return render_template('register.html')
            else : 
                        # hash password
                hashed_password = generate_password_hash(password)

                # create user object
                user = User(user_type, first_name, last_name, email, hashed_password, role)
                print("DEBUG: User object created:", user.__dict__)
                # insert into DB
                insert_user(user)
                flash("Registration successful!", "success")
                return redirect(url_for('main.index'))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
            return render_template('register.html')

    return render_template('register.html')


@main.route('/item/new', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        try:
            item_id = request.form.get('item_id')
            title = request.form.get('title')
            description = request.form.get('description')
            starting_price = request.form.get('starting_price')
            end_time = request.form.get('end_time')
            is_auction_active = request.form.get('is_auction_active', 1)
            user_id = session.get('user_id')
            img = request.files.get('img')

            print("DEBUG: Received 2form data:", item_id, title, description, starting_price, end_time, is_auction_active, user_id, img)

            # Validation
            if not title or not description or not starting_price or not end_time:
                flash("All fields are required!", "danger")
                return render_template('add_item.html')
            if not user_id:
                flash("You must be logged in to add an item!", "danger")
                return redirect(url_for('main.login'))

            # Handle image upload
            img_path = None
            if img:
                filename = secure_filename(f"{item_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
                upload_folder = current_app.config['UPLOAD_FOLDER']  # FIXED: use current_app
                os.makedirs(upload_folder, exist_ok=True)
                img.save(os.path.join(upload_folder, filename))
                img_path = os.path.join('static', 'uploads', filename)

            # Insert into DB
            # item = Item(item_id, title, description, starting_price, end_time, is_auction_active, user_id, img_path)
            # print("DEBUG: Item object created:", item)
            
            insert_item(item_id, title, description, starting_price, end_time, is_auction_active, user_id, img_path)
            flash("Item added successfully!", "success")
            return redirect(url_for('main.seller_dashboard'))

        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
            return render_template('register.html')

    return render_template('add_item.html')
       
        
    
                
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Create a temporary User object
        user = User(None, None, None, email, password, None)
        user_row = user_login(user)
        role = get_role_name(user) if user_row else None

        if user_row:
            session['user_id'] = user_row['user_id']
            session['role_id'] = user_row['role']
            session['role_name'] = role  # Helper function

            flash(f"Welcome, {user_row['first_name']}! You are logged in as {session['role_name']}.", "success")

            # Redirect based on role
            if session['role_name'] == 'seller':
                return redirect(url_for('main.seller_dashboard'))
            elif session['role_name'] == 'bidder':
                return redirect(url_for('main.bidder_dashboard'))
            elif session['role_name'] == 'admin':
                return redirect(url_for('main.admin_dashboard'))
            else:
                return redirect(url_for('main.index'))
        else:
            flash("Invalid email or password!", "danger")
            return render_template('index.html')

    return render_template('index.html')




@main.route('/seller/dashboard')
def seller_dashboard():
    return render_template('seller_dashboad.html')
@main.route('/bidder/dashboard')
def bidder_dashboard():
    return render_template('bidder_dashboard.html')

@main.route('/item_list')
def item_list():
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM `item`;")
            items = cursor.fetchall()
        print("DEBUG: Items fetched from database:", items)
    finally:
        conn.close()
    
    return render_template('item_list.html', items=items)

@main.route('/item_details/<int:item_id>')
def item_detail(item_id):
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM `item` WHERE ItemID = %s;", (item_id,))
            item = cursor.fetchone()
        print("DEBUG: Single item fetched from database:", item)
    finally:
        conn.close()
    
    if not item:
        return "Item not found", 404

    return render_template('item_detail.html', item=item)
@main.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('main.index'))

@main.route('/seller/user_items')
def user_items():
    items = []
    user_id = session.get('user_id')
    print("DEBUG: User ID from session:", user_id)
    print("DEBUG: Fetching items for user ID:", user_id)
    if not user_id:
        flash("You must be logged in to view your items.", "warning")
        return redirect(url_for('main.login'))
    # Fetch items for the logged-in user
    items = get_item_by_seller(user_id) if user_id else []
    if not items:
        print("DEBUG: No items found for user ID:", user_id)
        flash("No items found for this user.", "info")
    else:
        flash(f"Found {len(items)} items for this user.", "success")
        print("DEBUG: User ID:", user_id)
    print("DEBUG: User items fetched:", items)
    
    return render_template('user_items.html', items=items)

@main.route('/update_item/<int:item_id>', methods=['GET', 'POST'])
def update_item(item_id):
    conn = get_db_connection()
    item = None
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        starting_price = request.form.get('starting_price')
        end_time = request.form.get('end_time')
        is_auction_active = request.form.get('is_auction_active', 1)
        user_id = session.get('user_id')

        if not title or not description or not starting_price or not end_time:
            flash("All fields are required!", "danger")
            return redirect(url_for('main.update_item', item_id=item_id))

        try:
            with conn.cursor() as cursor:
                sql = """
                    UPDATE Item
                    SET Title=%s, Description=%s, StartingPrice=%s, EndTime=%s, IsAuctionActive=%s
                    WHERE ItemID=%s AND UserID=%s
                """
                cursor.execute(sql, (title, description, starting_price, end_time, is_auction_active, item_id, user_id))
                conn.commit()
            flash("Item updated successfully!", "success")
            return redirect(url_for('main.user_items'))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(url_for('main.update_item', item_id=item_id))
    
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM Item WHERE ItemID = %s", (item_id,))
            item = cursor.fetchone()
    finally:
        conn.close()

    if not item:
        flash("Item not found!", "danger")
        return redirect(url_for('main.user_items'))

    return render_template('update_item.html', item=item)
@main.route('//seller/close')
def closed_auctions():
    items = get_closed_auction_items()
    if not items:
        flash("No closed auctions found.", "info")
    return render_template('closed_auctions.html', items=items)

@main.route('/delete_item/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "DELETE FROM Item WHERE ItemID = %s"
            cursor.execute(sql, (item_id,))
            conn.commit()
        flash("Item deleted successfully!", "success")
    except Exception as e:
        flash(f"An error occurred while deleting the item: {str(e)}", "danger")
    finally:
        conn.close()

    return redirect(url_for('main.user_items'))
@main.route('/close_item/<int:item_id>', methods=['POST'])
def close_item(item_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "UPDATE Item SET IsAuctionActive = 0 WHERE ItemID = %s"
            cursor.execute(sql, (item_id,))
            conn.commit()
        flash("Item auction closed successfully!", "success")
    except Exception as e:
        flash(f"An error occurred while closing the item auction: {str(e)}", "danger")
    finally:
        conn.close()


@main.route('/bidder/item_listed')
def item_listed():
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM `item`;")
            items = cursor.fetchall()
        print("DEBUG: Items fetched from database:", items)
    finally:
        conn.close()
    
    return render_template('bidder_items.html', items=items)


@main.route('/place_bid_new/<int:item_id>', methods=['GET', 'POST'])
def place_bid_new(item_id):
    if request.method == 'POST':
        bid_amount = request.form.get('bid_amount')
        user_id = session.get('user_id')
        if not bid_amount or not user_id:
            print("DEBUG: Bid amount or user ID is missing")
            flash("Bid amount and user ID are required!", "danger")
            return redirect(url_for('main.item_listed'))
        try:
            if place_bid(item_id, user_id, bid_amount):
                flash(f"Bid of {bid_amount} placed on item {item_id} by user {user_id}!", "success")
            else:
                flash("Failed to place bid. Please try again.", "danger")
        except Exception as e:
            flash(f"An error occurred while placing the bid: {str(e)}", "danger")
            print("DEBUG: Exception occurred while placing bid:", str(e))
        print("DEBUG: Placing bid for item:", item_id)
    else:
        print("DEBUG: GET request for placing bid on item:", item_id)
        flash("Bid amount and user ID are required!", "danger")
        # bid_amount = request.form.get('bid_amount')
        # user_id = session.get('user_id')



        # # Here you would typically insert the bid into the database
        # # For now, we just flash a success message
        # print(f"DEBUG: Placing bid of {bid_amount} for item {item_id} by user {user_id}")
        # flash(f"Bid of {bid_amount} placed on item {item_id} by user {user_id}!", "success")
        # return redirect(url_for('main.item_listed'))
    

    return redirect(url_for('main.item_listed'))

#/seller/auctions
@main.route('/seller/auctions')
def seller_auctions():
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to view your auctions.", "warning")
        return redirect(url_for('main.login'))

    # Get all auctions for the seller
    items = get_auction_by_item_and_seller(user_id)

    if not items:
        flash("No auctions found for your items.", "info")
        return render_template('auctions.html', items=[])

    # Highlight highest bid per item
    highest_bids = {}
    for item in items:
        title = item.get('title')
        bid_amount = item.get('bidAmount', 0) or 0
        if title not in highest_bids or bid_amount > highest_bids[title]:
            highest_bids[title] = bid_amount

    # Mark each item with highest bid flag
    for item in items:
        bid_amount = item.get('bidAmount', 0) or 0
        item['isHighest'] = bid_amount == highest_bids[item.get('title')]

    return render_template('auctions.html', items=items)

