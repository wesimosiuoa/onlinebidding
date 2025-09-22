class User:
    def __init__(self, user_type, first_name, last_name, email, password, role_id):
        self._user_type = user_type
        self._first_name = first_name   # this sets the private var directly
        self._last_name = last_name
        self._email = email
        self._password = password
        self._role_id = role_id

    @property
    def first_name(self):
        return self._first_name

    @first_name.setter
    def first_name(self, value):
        self._first_name = value

    @property
    def last_name(self):
        return self._last_name

    @last_name.setter
    def last_name(self, value):
        self._last_name = value

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        self._email = value

    # etc. for password, role_id
    @property
    def password(self):
        return self._password
    @password.setter
    def password(self, value):
        self._password = value
    @property
    def role_id(self):
        return self._role_id
    @role_id.setter
    def role_id(self, value):
        self._role_id = value
    @property
    def user_type(self):
        return self._user_type
    @user_type.setter
    def user_type(self, value):
        self._user_type = value 