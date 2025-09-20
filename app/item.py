from app.models import insert_item, get_db_connection
from werkzeug.utils import secure_filename
import pymysql
class Item:
    def __init__(self, item_id, title, description, starting_price, end_time, 
                 is_auction_active=1, user_id=None, img=None):
        self._item_id = item_id
        self._title = title
        self._description = description
        self._starting_price = starting_price
        self._end_time = end_time
        self._is_auction_active = is_auction_active
        self._user_id = user_id
        self._img = img
   
    # Getters
    def get_item_id(self):
        return self._item_id

    def get_title(self):
        return self._title

    def get_description(self):
        return self._description

    def get_starting_price(self):
        return self._starting_price

    def get_end_time(self):
        return self._end_time

    def get_is_auction_active(self):
        return self._is_auction_active

    def get_user_id(self):
        return self._user_id

    def get_img(self):
        return self._img

    # Setters
    def set_item_id(self, item_id):
        self._item_id = item_id

    def set_title(self, title):
        self._title = title

    def set_description(self, description):
        self._description = description

    def set_starting_price(self, starting_price):
        self._starting_price = starting_price

    def set_end_time(self, end_time):
        self._end_time = end_time

    def set_is_auction_active(self, is_auction_active):
        self._is_auction_active = is_auction_active

    def set_user_id(self, user_id):
        self._user_id = user_id

    def set_img(self, img):
        self._img = img
        
# Methods 
        insert_item(
            self._title,
            self._description,
            self._starting_price,
            self._end_time,
            self._is_auction_active,
            self._user_id,
            self._img
        )




