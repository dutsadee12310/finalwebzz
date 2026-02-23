from flask import Flask, render_template, request, jsonify, session, redirect
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "super-secret-key"

# ================= DATABASE =================
def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# ================= IMAGE FOLDER =================
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'images', 'products')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ================= PRODUCTS =================
PRODUCTS = [
    # ===== เมาส์ =====
    {'id': 1, 'name': 'Razer Viper V3 Pro', 'price': 4990, 'category': 'เมาส์', 'description': 'เมาส์ eSports น้ำหนักเบา'},
    {'id': 2, 'name': 'Logitech G Pro X Superlight 2', 'price': 5490, 'category': 'เมาส์', 'description': 'เมาส์ไร้สายระดับโปร'},
    {'id': 3, 'name': 'Finalmouse UltralightX', 'price': 6490, 'category': 'เมาส์', 'description': 'เมาส์สายแข่งขัน น้ำหนักเบาพิเศษ'},
    {'id': 4, 'name': 'Zowie EC2-CW', 'price': 4590, 'category': 'เมาส์', 'description': 'เมาส์ FPS ทรงยอดนิยม'},
    
    # ===== คีย์บอร์ด =====
    {'id': 5, 'name': 'Wooting 60HE+', 'price': 8000, 'category': 'คีย์บอร์ด', 'description': 'คีย์บอร์ด Hall Effect ปรับแรงกดได้'},
    {'id': 6, 'name': 'SteelSeries Apex Pro TKL', 'price': 6990, 'category': 'คีย์บอร์ด', 'description': 'คีย์บอร์ด OmniPoint'},
    {'id': 7, 'name': 'Corsair K70 RGB Pro', 'price': 5990, 'category': 'คีย์บอร์ด', 'description': 'Mechanical Keyboard ระดับพรีเมียม'},
    {'id': 8, 'name': 'Ducky One 3 Mini', 'price': 4290, 'category': 'คีย์บอร์ด', 'description': 'คีย์บอร์ด Custom ยอดนิยม'},

    # ===== หูฟัง =====
    {'id': 9, 'name': 'HyperX Cloud II', 'price': 3090, 'category': 'หูฟัง', 'description': 'หูฟังเกมมิ่งระดับตำนาน'},
    {'id': 10, 'name': 'HyperX Cloud Alpha Wireless', 'price': 6990, 'category': 'หูฟัง', 'description': 'แบต 300 ชั่วโมง'},
    {'id': 11, 'name': 'SteelSeries Arctis Nova Pro', 'price': 12900, 'category': 'หูฟัง', 'description': 'หูฟังเกมมิ่งระดับเรือธง'},
    {'id': 12, 'name': 'Logitech G Pro X 2', 'price': 8990, 'category': 'หูฟัง', 'description': 'หูฟัง eSports ไร้สาย'},

    # ===== ไมโครโฟน =====
    {'id': 13, 'name': 'HyperX SoloCast', 'price': 1990, 'category': 'ไมล์โครโฟน', 'description': 'ไมค์ USB เสียงใส'},
    {'id': 14, 'name': 'HyperX QuadCast S', 'price': 5690, 'category': 'ไมล์โครโฟน', 'description': 'ไมค์ RGB สำหรับสตรีมเมอร์'},
    {'id': 15, 'name': 'Shure MV7', 'price': 8990, 'category': 'ไมล์โครโฟน', 'description': 'ไมค์สายโปรระดับ Podcast'},

    # ===== แผ่นรองเมาส์ =====
    {'id': 16, 'name': 'Logitech G PowerPlay 2', 'price': 3590, 'category': 'แผ่นรองเมาส์', 'description': 'แผ่นรองเมาส์ชาร์จไร้สาย'},
    {'id': 17, 'name': 'Artisan FX Zero XL', 'price': 2490, 'category': 'แผ่นรองเมาส์', 'description': 'แผ่นรองเมาส์ eSports ญี่ปุ่น'},
    {'id': 18, 'name': 'SteelSeries QcK Heavy', 'price': 1490, 'category': 'แผ่นรองเมาส์', 'description': 'แผ่นรองเมาส์หนาพิเศษ'},

    # ===== อุปกรณ์เสริม =====
    {'id': 19, 'name': 'Elgato Stream Deck MK.2', 'price': 6290, 'category': 'อุปกรณ์เสริม', 'description': 'อุปกรณ์สำหรับสตรีมเมอร์'},
    {'id': 20, 'name': 'Razer Kiyo Pro', 'price': 6990, 'category': 'อุปกรณ์เสริม', 'description': 'เว็บแคมระดับโปร'},
]

CATEGORIES = [
    'ทั้งหมด',
    'เมาส์',
    'คีย์บอร์ด',
    'หูฟัง',
    'ไมล์โครโฟน',
    'แผ่นรองเมาส์',
    'อุปกรณ์เสริม'
]

# ================= IMAGE GENERATOR =================
def generate_product_images():
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F']
    for idx, product in enumerate(PRODUCTS):
        image_path = os.path.join(UPLOAD_FOLDER, f'product_{product["id"]}.png')
        if not os.path.exists(image_path):
            img = Image.new('RGB', (400, 400), color=colors[idx % len(colors)])
            draw = ImageDraw.Draw(img)

            try:
                font = ImageFont.truetype("arial.ttf", 28)
                price_font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
                price_font = ImageFont.load_default()

            text = product['name']
            price_text = f"฿{product['price']:,}"

            bbox = draw.textbbox((0, 0), text, font=font)
            text_x = (400 - (bbox[2] - bbox[0])) // 2

            pbbox = draw.textbbox((0, 0), price_text, font=price_font)
            price_x = (400 - (pbbox[2] - pbbox[0])) // 2

            draw.text((text_x, 140), text, fill='white', font=font)
            draw.text((price_x, 240), price_text, fill='#FFD700', font=price_font)

            img.save(image_path)

# ================= AUTH =================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return "กรอกข้อมูลไม่ครบ"

        hash_pw = generate_password_hash(password)

        try:
            db = get_db()
            db.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hash_pw)
            )
            db.commit()
            db.close()
        except:
            return "username ซ้ำ"

        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        db.close()

        if user is None or not check_password_hash(user["password"], password):
            return "username หรือ password ไม่ถูกต้อง"

        session["user_id"] = user["id"]
        session["username"] = user["username"]

        return redirect("/")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ================= STORE =================
@app.route('/')
def index():
    category = request.args.get('category', 'ทั้งหมด')
    filtered_products = PRODUCTS if category == 'ทั้งหมด' else [
        p for p in PRODUCTS if p['category'] == category
    ]
    cart_count = len(session.get('cart', []))
    return render_template(
        'index.html',
        products=filtered_products,
        categories=CATEGORIES,
        current_category=category,
        cart_count=cart_count
    )

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    if 'cart' not in session:
        session['cart'] = []

    cart = session['cart']
    existing_item = next((item for item in cart if item['product_id'] == product_id), None)

    if existing_item:
        existing_item['quantity'] += quantity
    else:
        cart.append({'product_id': product_id, 'quantity': quantity})

    session.modified = True
    return jsonify(success=True, cart_count=len(cart))

@app.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    data = request.json
    product_id = data.get('product_id')

    if 'cart' in session:
        session['cart'] = [
            item for item in session['cart']
            if item['product_id'] != product_id
        ]
        session.modified = True

    return jsonify(success=True)

@app.route('/api/cart/update', methods=['POST'])
def update_cart():
    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    if 'cart' in session:
        item = next((item for item in session['cart'] if item['product_id'] == product_id), None)
        if item:
            if quantity <= 0:
                session['cart'] = [
                    i for i in session['cart']
                    if i['product_id'] != product_id
                ]
            else:
                item['quantity'] = quantity
            session.modified = True

    return jsonify(success=True)

@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    cart_items = []

    for item in cart:
        product = next((p for p in PRODUCTS if p['id'] == item['product_id']), None)
        if product:
            cart_items.append({
                **product,
                'quantity': item['quantity'],
                'total': product['price'] * item['quantity']
            })

    subtotal = sum(item['total'] for item in cart_items)
    shipping = 50 if subtotal > 0 else 0
    total = subtotal + shipping

    return render_template(
        'cart.html',
        cart_items=cart_items,
        subtotal=subtotal,
        shipping=shipping,
        total=total
    )

@app.route('/checkout')
@login_required
def checkout():
    cart = session.get('cart', [])
    cart_items = []

    for item in cart:
        product = next((p for p in PRODUCTS if p['id'] == item['product_id']), None)
        if product:
            cart_items.append({
                **product,
                'quantity': item['quantity'],
                'total': product['price'] * item['quantity']
            })

    subtotal = sum(item['total'] for item in cart_items)
    shipping = 50 if subtotal > 0 else 0
    total = subtotal + shipping

    return render_template(
        'checkout.html',
        cart_items=cart_items,
        subtotal=subtotal,
        shipping=shipping,
        total=total
    )

@app.route('/api/order/place', methods=['POST'])
@login_required
def place_order():
    order_data = {
        'order_id': f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'cart': session.get('cart', []),
        'created_at': datetime.now().isoformat()
    }

    session['cart'] = []
    session.modified = True

    return jsonify(success=True, order_id=order_data['order_id'])

@app.route('/success/<order_id>')
def order_success(order_id):
    return render_template('success.html', order_id=order_id)

# ================= RUN =================
if __name__ == '__main__':
    generate_product_images()
    app.run(debug=True, host='localhost', port=5000)