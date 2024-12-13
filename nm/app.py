from flask import Flask, render_template, session, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# Initialize Flask App and Database
app = Flask(__name__)

# Set up the database URI and other configurations directly here
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:your_password@localhost/FreshBasketDb'  # Replace with your MySQL credentials
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # You can replace this with a stronger key

db = SQLAlchemy(app)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

# Define Database Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    description = db.Column(db.String(200), nullable=True)  # New field
    category = db.Column(db.String(50), nullable=True)  # New field

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    product = db.relationship('Product', backref='cart_items')

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending')  # Default status is "Pending"
    user_id = db.Column(db.Integer, nullable=False)
    product = db.relationship('Product', backref='orders')

    def __init__(self, product_id, quantity, total_price, user_id):
        self.product_id = product_id
        self.quantity = quantity
        self.total_price = total_price
        self.user_id = user_id
        self.status = 'OK'  # Default order status

# Create database tables
with app.app_context():
    db.create_all()

# Load user function (flask-login)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Automatically inject user_id into templates
@app.context_processor
def inject_user_id():
    return {'user_id': session.get('user_id')}

# Routes for Pages
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:  # Securely handle password hashing in production
            login_user(user)  # Log the user in
            session['user_id'] = user.id  # Store user ID in session
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid credentials', 400

    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()  # Log the user out
    session.pop('user_id', None)  # Clear user_id from session
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return 'Username already exists', 400

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/shop')
def shop():
    products = Product.query.all()
    return render_template('shop.html', products=products)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    product = Product.query.get(product_id)
    if product:
        if 'cart' not in session:
            session['cart'] = []
        cart_items = session['cart']
        for item in cart_items:
            if item['product_id'] == product_id:
                item['quantity'] += 1
                break
        else:
            cart_items.append({'product_id': product_id, 'quantity': 1})
        session['cart'] = cart_items
    return redirect(url_for('cart_page'))

@app.route('/cart')
def cart_page():
    cart_items = session.get('cart', [])
    cart_product_details = []
    for item in cart_items:
        product = Product.query.get(item['product_id'])
        if product:
            cart_product_details.append({'product': product, 'quantity': item['quantity']})
    return render_template('cart.html', cart_items=cart_product_details)

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart_items = session.get('cart', [])
    cart_items = [item for item in cart_items if item['product_id'] != product_id]
    session['cart'] = cart_items
    return redirect(url_for('cart_page'))

@app.route('/checkout')
def checkout():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    cart_items = session.get('cart', [])
    cart_product_details = []
    for item in cart_items:
        product = Product.query.get(item['product_id'])
        if product:
            cart_product_details.append({'product': product, 'quantity': item['quantity']})
    return render_template('checkout.html', cart_items=cart_product_details)

@app.route('/profile')
@login_required
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    orders = Order.query.filter_by(user_id=user_id).all()
    return render_template('profile.html', orders=orders)

@app.route('/confirm_order', methods=['POST'])
@login_required
def confirm_order():
    user_id = session.get('user_id')
    cart_items = session.get('cart', [])
    if cart_items:
        for item in cart_items:
            product = Product.query.get(item['product_id'])
            if product:
                total_price = product.price * item['quantity']
                new_order = Order(
                    user_id=user_id,
                    product_id=item['product_id'],
                    quantity=item['quantity'],
                    total_price=total_price
                )
                db.session.add(new_order)
        db.session.commit()
        session.pop('cart', None)
        return "Order confirmed! Thank you for shopping."
    else:
        return "Your cart is empty. Please add items to your cart first."

if __name__ == '__main__':
    app.run(debug=True)
