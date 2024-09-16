from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import mercadopago

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['MERCADO_PAGO_ACCESS_TOKEN'] = 'YOUR_ACCESS_TOKEN'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('El nombre de usuario ya está en uso. Elige otro.', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Usuario creado con éxito. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('home'))

        flash('Nombre de usuario o contraseña incorrectos', 'danger')

    return render_template('login.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/cart')
@login_required
def cart():
    return render_template('cart.html')

@app.route('/checkout')
@login_required
def checkout():
    return render_template('checkout.html')

@app.route('/checkout_mercado_pago', methods=['GET', 'POST'])
@login_required
def checkout_mercado_pago():
    sdk = mercadopago.SDK(app.config['MERCADO_PAGO_ACCESS_TOKEN'])

    if request.method == 'POST':
        preference_data = {
            "items": [
                {
                    "title": "Test Product",
                    "quantity": 1,
                    "unit_price": 100.00
                }
            ],
            "back_urls": {
                "success": url_for('payment_success', _external=True),
                "failure": url_for('payment_failure', _external=True),
                "pending": url_for('payment_pending', _external=True)
            },
            "auto_return": "approved",
        }
        
        try:
            preference = sdk.preference().create(preference_data)
            print('Preferencia creada:', preference)  # Imprimir la respuesta completa
            if 'id' in preference['response']:
                preference_id = preference['response']['id']
                return redirect(preference['response']['init_point'])
            else:
                flash('Error en la creación de la preferencia de pago.', 'danger')
                return redirect(url_for('checkout'))

        except Exception as e:
            # Manejo de errores
            flash(f'Ocurrió un error al procesar el pago: {str(e)}', 'danger')
            return redirect(url_for('checkout'))

    return render_template('checkout_mercado_pago.html')

@app.route('/payment_success')
def payment_success():
    return render_template('payment_success.html')

@app.route('/payment_failure')
def payment_failure():
    return render_template('payment_failure.html')

@app.route('/payment_pending')
def payment_pending():
    return render_template('payment_pending.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('home'))

def create_db():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    create_db()  # Asegúrate de crear las tablas antes de iniciar la aplicación
    app.run(debug=True)
