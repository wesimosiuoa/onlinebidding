import pymysql

class User:
    def __init__(self, user_type, name, email, password, phone, role_id):
        self._user_type = user_type
        self._name = name
        self._email = email
        self._password = password
        self._phone = phone
        self._role_id = role_id

    # Getters
    @property
    def user_type(self):
        return self._user_type

    @property
    def name(self):
        return self._name

    @property
    def email(self):
        return self._email

    @property
    def password(self):
        return self._password

    @property
    def phone(self):
        return self._phone

    @property
    def role_id(self):
        return self._role_id

    # Setters
    @user_type.setter
    def user_type(self, value):
        self._user_type = value

    @name.setter
    def name(self, value):
        self._name = value

    @email.setter
    def email(self, value):
        self._email = value

    @password.setter
    def password(self, value):
        self._password = value

    @phone.setter
    def phone(self, value):
        self._phone = value

    @role_id.setter
    def role_id(self, value):
        self._role_id = value

    def __repr__(self):
        return f'<User {self.name}>'

    def save_to_db(self, connection):
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO User (Name, Email, Password, roleID)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (self.name, self.email, self.password, self.role_id))
            connection.commit()
