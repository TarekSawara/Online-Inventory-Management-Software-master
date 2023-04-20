from orders import db, app, login_manager
import datetime
from flask_login import UserMixin
import phonenumbers


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), nullable=False, unique=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    date_creation = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    roles = db.Column(db.String(120))
    order = db.relationship('Orders', cascade="all,delete", backref='user_order', lazy=True)


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_amount = db.Column(db.String(80), nullable=False)
    date_creation = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    orders = db.relationship('Orders_items', cascade="all,delete", backref='Orders_items', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Orders_items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.String(80), nullable=False)
    total = db.Column(db.String(80), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    barcode = db.Column(db.String(80), nullable=False, unique=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.String(80), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)

    # supplier = db.relationship('Suppliers', backref=db.backref('products', lazy=True), lazy=True, cascade="all,delete")


class Suppliers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    address = db.Column(db.String(80), nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    note = db.Column(db.String(80), nullable=False)
    products = db.relationship('Products', backref='supplier', lazy=True, cascade="all,delete")


    @staticmethod
    def is_valid_phone_number(number):
        """
        Returns True if the given string is a valid phone number
        """
        try:
            parsed_number = phonenumbers.parse(number, None)
            return phonenumbers.is_valid_number(parsed_number)
        except phonenumbers.NumberParseException:
            return False

    @staticmethod
    def is_valid_address(address):
        """
        Returns True if the given string is a valid address
        """
        return any(char.isdigit() for char in address) and any(char.isalpha() for char in address.split())

    def __init__(self, name, address, contact, note):
        if not self.is_valid_phone_number(contact):
            raise ValueError("Invalid phone number")

        if not self.is_valid_address(address):
            raise ValueError("Invalid address")

        self.name = name
        self.address = address
        self.contact = contact
        self.note = note


def init_db():
    with app.app_context():
        db.create_all()

        # Create a test user
        new_user = Users(email='tarek.sawara@gmail.com', username='tarek', password='Aa123456')
        # new_user = Users('a@a.com', 'aaaaaaaa')
        new_user.display_name = 'Nathan'
        db.session.add(new_user)
        db.session.commit()

        new_user.datetime_subscription_valid_until = datetime.datetime(2019, 1, 1)
        db.session.commit()
