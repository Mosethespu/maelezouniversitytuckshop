import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from firebase_admin import auth, initialize_app, credentials, firestore
from dotenv import load_dotenv
import os
import random

# Load environment variables
load_dotenv()
firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')

# Initialize Firebase Admin SDK
cred = credentials.Certificate(firebase_credentials)
initialize_app(cred)

ADMIN_EMAIL = 'admin'
ADMIN_PASSWORD = 'admin'

# Initialize Firestore DB
db = firestore.client()

# Dictionary to store user credentials
user_credentials = {}
cart_items = []
orders = {}

class MaelezoUniversityTuckshop(toga.App):

    def startup(self):
        self.main_window = toga.MainWindow(title=self.formal_name)
        
        self.username_input = toga.TextInput(placeholder='Email')
        self.password_input = toga.PasswordInput(placeholder='Password')
        self.login_button = toga.Button('Log In', on_press=self.validate_login)
        self.signup_button = toga.Button('Sign Up', on_press=self.signup_user)
        self.status_label = toga.Label('')
        
        self.login_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        self.login_box.add(self.username_input)
        self.login_box.add(self.password_input)
        self.login_box.add(self.login_button)
        self.login_box.add(self.signup_button)
        self.login_box.add(self.status_label)
        
        self.main_window.content = self.login_box
        self.main_window.show()

    def validate_login(self, widget):
        email = self.username_input.value
        password = self.password_input.value
        
        if not email or not password:
            self.status_label.text = 'Please enter both email and password.'
            return

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            self.status_label.text = 'Admin login successful!'
            self.show_admin_options(widget)
        elif email in user_credentials and user_credentials[email] == password:
            self.status_label.text = 'Login successful!'
            self.show_user_options(widget)
        else:
            self.status_label.text = 'Login failed. Please check your credentials.'

    def signup_user(self, widget):
        email = self.username_input.value
        password = self.password_input.value
        
        if not email or not password:
            self.status_label.text = 'Please enter both email and password.'
            return
        
        if email in user_credentials:
            self.status_label.text = 'User already exists. Please log in.'
        else:
            user_credentials[email] = password
            self.status_label.text = 'Sign up successful! Please log in.'

    
    def show_login_screen(self, widget): 
        self.main_window.content = self.login_box
    
    def show_admin_options(self, widget):
        add_stationery_button = toga.Button('Add Stationery', on_press=self.add_stationery)
        add_snacks_button = toga.Button('Add Snacks', on_press=self.add_snacks)
        view_orders_button = toga.Button('View Orders', on_press=self.view_orders)
        back_button = toga.Button('Back', on_press=self.show_login_screen)

        admin_options_box = toga.Box(style=Pack(direction=COLUMN, padding=10, alignment=CENTER))
        admin_options_box.add(add_stationery_button)
        admin_options_box.add(add_snacks_button)
        admin_options_box.add(view_orders_button)
        admin_options_box.add(back_button)
        
        self.main_window.content = admin_options_box

    def add_stationery(self, widget):
        self.show_product_form('stationery',widget)

    def add_snacks(self, widget):
        self.show_product_form('snacks',widget)

    def show_product_form(self, category, widgets):
        self.product_name_input = toga.TextInput(placeholder='Product Name')
        self.product_price_input = toga.NumberInput(min=0)
        self.product_quantity_input = toga.NumberInput(min=0)
        self.product_offer_input = toga.TextInput(placeholder="Offers available")
        self.add_product_button = toga.Button('Add Product', on_press=lambda w: self.save_product(category))
        self.back_button = toga.Button('Back', on_press=self.show_admin_options)

        product_form_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        product_form_box.add(toga.Label(f'Add {category.capitalize()}'))
        product_form_box.add(toga.Label('Product Name'))
        product_form_box.add(self.product_name_input)
        product_form_box.add(toga.Label('Price'))
        product_form_box.add(self.product_price_input)
        product_form_box.add(toga.Label('Quantity'))
        product_form_box.add(self.product_quantity_input)
        product_form_box.add(toga.Label('Offers Available'))
        product_form_box.add(self.product_offer_input)
        product_form_box.add(self.add_product_button)
        product_form_box.add(self.back_button)

        self.main_window.content = product_form_box
    
    def save_product(self, category):
        product_name = self.product_name_input.value
        product_price = self.product_price_input.value
        product_quantity = self.product_quantity_input.value

        # Validate the required fields
        if not product_name or product_price is None or product_quantity is None:
            self.main_window.info_dialog('Error', 'Please fill in all required fields: Product Name, Price, and Quantity.')
            return
        
        product_data = {
            'name': self.product_name_input.value,
            'price': float(self.product_price_input.value),
            'quantity': float(self.product_quantity_input.value),
            'offers': self.product_offer_input.value

        }

        try:
            db.collection(category).add(product_data)
            self.main_window.info_dialog('Success', f'{category.capitalize()} added successfully!')
        except Exception as e:
            self.main_window.info_dialog('Error', f'Failed to add {category}. Error: {e}')

    def show_user_options(self, widget):
        view_stationery_button = toga.Button('View Stationery', on_press=self.view_stationery)
        view_snacks_button = toga.Button('View Snacks', on_press=self.view_snacks)
        back_button = toga.Button('Back', on_press=self.show_login_screen)

        user_options_box = toga.Box(style=Pack(direction=COLUMN, padding=10, alignment=CENTER))
        user_options_box.add(view_stationery_button)
        user_options_box.add(view_snacks_button)
        user_options_box.add(back_button)

        self.main_window.content = user_options_box

    def view_stationery(self, widget):
        self.show_products('stationery')

    def view_snacks(self, widget):
        self.show_products('snacks')

    def show_products(self, category):
        products_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        products_box.add(toga.Label(f'{category.capitalize()} Products'))

    # Retrieve products from Firestore and display them
        products = db.collection(category).get()
        for product in products:
            product_data = product.to_dict()
        
            product_name_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
            product_name_box.add(toga.Label('Product Name'))
            product_name_box.add(toga.Label(f"{product_data['name']}"))

            price_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
            price_box.add(toga.Label('Price'))
            price_box.add(toga.Label(f"{product_data['price']}"))

            quantity_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
            quantity_box.add(toga.Label('Quantity'))
            quantity_box.add(toga.Label(f"{product_data['quantity']}"))

            offer_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
            offer_box.add(toga.Label('Offers'))
            offer_box.add(toga.Label(f"{product_data['offers']}"))

            add_to_cart_button = toga.Button('Add to Cart', on_press=lambda w, p=product_data:self.add_to_cart(p))

            product_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
            product_box.add(product_name_box)
            product_box.add(price_box)
            product_box.add(quantity_box)
            product_box.add(offer_box)
            product_box.add(add_to_cart_button)
            products_box.add(product_box)
        

        self.back_button = toga.Button('Back', on_press=self.show_user_options)
        self.checkout_button = toga.Button('Checkout', on_press=self.checkout)

        products_box.add(self.back_button)
        products_box.add(self.checkout_button)

        main_box = toga.Box(style=Pack(direction=COLUMN))
        main_box.add(products_box)

        # Make the entire page scrollable
        scrollable_main_box = toga.ScrollContainer(content=main_box, horizontal=False)

        self.main_window.content = scrollable_main_box 
    
    def add_to_cart(self, product):
        cart_items.append(product)
        self.main_window.info_dialog('Success', f'{product["name"]} added to cart!')

    def checkout(self, widget):
        checkout_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        checkout_box.add(toga.Label('Checkout'))

        # Display cart items
        for item in cart_items:
            item_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
            item_box.add(toga.Label('Product Name'))
            item_box.add(toga.Label(f"{item['name']}"))
            item_box.add(toga.Label('Price'))
            item_box.add(toga.Label(f"${item['price']}"))
            item_box.add(toga.Label('Quantity'))
            item_box.add(toga.Label(f"{item['quantity']}"))
            item_box.add(toga.Label('Offer'))
            item_box.add(toga.Label(f"{item['offers']}"))
            checkout_box.add(item_box)

        self.confirm_button = toga.Button('Confirm Order', on_press=self.confirm_order)
        self.back_button = toga.Button('Back', on_press=self.show_user_options)

        checkout_box.add(self.confirm_button)
        checkout_box.add(self.back_button)

        main_box = toga.Box(style=Pack(direction=COLUMN))
        main_box.add(checkout_box)

        # Make the entire page scrollable
        scrollable_main_box = toga.ScrollContainer(content=main_box, horizontal=False)

        self.main_window.content = scrollable_main_box 


    def confirm_order(self, widget):
        if not cart_items: # Check if cart is empty
            self.main_window.info_dialog('Error', 'Your cart is empty. Please add items to your cart before confirming your order.')
            return
        
        user_email = self.username_input.value  # Assuming the user's email is stored here
        order_items = [{'name': item['name'], 'price': item['price']} for item in cart_items]

        # Create an order data structure
        order_data = {
        'email': user_email,
        'items': order_items,
        'status': 'Pending'
        }

        try:
            db.collection('orders').add(order_data)  # Save order to Firestore
            delivery_time = random.randint(10, 60)  # Random time between 10 and 60 minutes
            self.main_window.info_dialog('Order Confirmed', f'Your order will be ready in {delivery_time} minutes. Congratulations!')
        except Exception as e:
            self.main_window.info_dialog('Error', f'Failed to confirm order. Error: {e}')
    
        cart_items.clear()  # Clear the cart
   

    def view_orders(self, widget):
        orders_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        orders_box.add(toga.Label('Orders'))

        try:
        # Retrieve all orders from Firestore
            orders = db.collection('orders').get()
            for order in orders:
                order_data = order.to_dict()
                orders_box.add(toga.Label(f"User: {order_data['email']}"))
                items = ', '.join([item['name'] for item in order_data['items']])
                orders_box.add(toga.Label(f"Items: {items}"))
                orders_box.add(toga.Label(f"Status: {order_data['status']}"))
        except Exception as e:
            self.main_window.info_dialog('Error', f'Failed to retrieve orders. Error: {e}')

        self.back_button = toga.Button('Back', on_press=self.show_admin_options)
        orders_box.add(self.back_button)

        scrollable_container = toga.ScrollContainer(content=orders_box, horizontal=False)
        self.main_window.content = scrollable_container

def main():
    return MaelezoUniversityTuckshop('Maelezo University Tuckshop', 'com.example.maelezouniversitytuckshop')

