from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from email_validator import validate_email, EmailNotValidError
import os
import mercadopago

# Configuración de la aplicación
app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bd.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Definición de modelos
class Usuario(db.Model):
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre_apellido = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    codigo_postal = db.Column(db.Integer)
    contraseña_usuario = db.Column(db.String(60), nullable=False)
    telefono = db.Column(db.Integer)
    carrito = db.relationship('Carrito', backref='usuario', lazy=True)

class Rol(db.Model):
    id_rol = db.Column(db.Integer, primary_key=True)
    tipo_rol = db.Column(db.String(50), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)

class Carrito(db.Model):
    id_carrito = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    status_carrito = db.Column(db.String(50))
    metodo_pago = db.Column(db.String(50))
    fecha_pago = db.Column(db.Date)
    productos = db.relationship('Producto', backref='carrito', lazy=True)

class Producto(db.Model):
    id_producto = db.Column(db.Integer, primary_key=True)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    descripcion = db.Column(db.Text)
    cantidad_producto = db.Column(db.Integer, nullable=False)
    id_carrito = db.Column(db.Integer, db.ForeignKey('carrito.id_carrito'))

# Formularios
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    contraseña = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6, max=60)])
    submit = SubmitField('Iniciar sesión')

class RegisterForm(FlaskForm):
    nombre_apellido = StringField('Nombre Completo', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    contraseña = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6, max=60)])
    confirm_contraseña = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('contraseña')])
    submit = SubmitField('Registrar')

class CheckoutForm(FlaskForm):
    payment_method = SelectField('Método de pago', choices=[
        ('tarjeta', 'Tarjeta de crédito'),
        ('mercado_pago', 'Mercado Pago')
    ], validators=[DataRequired()])
    submit = SubmitField('Pagar')

# Rutas
@app.route('/')
def index():
    return render_template('base.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        contraseña = form.contraseña.data
        user = Usuario.query.filter_by(email=email, contraseña_usuario=contraseña).first()
        if user:
            session['user_id'] = user.id_usuario
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('index'))
        else:
            flash('Email o contraseña incorrectos', 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        nombre_apellido = form.nombre_apellido.data
        email = form.email.data
        contraseña = form.contraseña.data
        confirm_contraseña = form.confirm_contraseña.data
        if contraseña != confirm_contraseña:
            flash('Las contraseñas no coinciden', 'danger')
            return redirect(url_for('register'))
        try:
            validate_email(email)
        except EmailNotValidError as e:
            flash(str(e), 'danger')
            return redirect(url_for('register'))
        if Usuario.query.filter_by(email=email).first():
            flash('El email ya está registrado', 'danger')
            return redirect(url_for('register'))
        new_user = Usuario(
            nombre_apellido=nombre_apellido,
            email=email,
            contraseña_usuario=contraseña
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registro exitoso', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/cart')
def cart():
    user_id = session.get('user_id')
    if user_id:
        carrito = Carrito.query.filter_by(id_usuario=user_id).first()
        productos = Producto.query.filter_by(id_carrito=carrito.id_carrito).all() if carrito else []
        return render_template('cart.html', productos=productos)
    else:
        flash('Debes iniciar sesión para ver el carrito', 'warning')
        return redirect(url_for('login'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    form = CheckoutForm()
    if form.validate_on_submit():
        payment_method = form.payment_method.data
        
        if payment_method == 'mercado_pago':
            return redirect(url_for('mercado_pago_payment'))
        elif payment_method == 'tarjeta':
            flash('Pago con tarjeta procesado', 'success')
            return redirect(url_for('index'))
        else:
            flash('Método de pago no válido', 'danger')
            return redirect(url_for('checkout'))
    
    return render_template('checkout.html', form=form)

@app.route('/mercado_pago_payment')
def mercado_pago_payment():
    sdk = mercadopago.SDK("YOUR_ACCESS_TOKEN")

    # Crear preferencia de pago
    preference_data = {
        "items": [
            {
                "title": "Producto de ejemplo",
                "quantity": 1,
                "unit_price": 19.99
            }
        ],
        "back_urls": {
            "success": url_for('payment_success', _external=True),
            "failure": url_for('payment_failure', _external=True),
            "pending": url_for('payment_pending', _external=True)
        },
        "auto_return": "approved"
    }

    preference = sdk.preference().create(preference_data)
    preference_id = preference['response']['id']

    return redirect(preference['response']['init_point'])

@app.route('/payment_success')
def payment_success():
    flash('Pago realizado con éxito', 'success')
    return redirect(url_for('index'))

@app.route('/payment_failure')
def payment_failure():
    flash('Pago fallido', 'danger')
    return redirect(url_for('index'))

@app.route('/payment_pending')
def payment_pending():
    flash('Pago pendiente', 'warning')
    return redirect(url_for('index'))

# Inicialización de la base de datos
def init_db():
    with app.app_context():
        if not os.path.exists('bd.sqlite3'):
            db.create_all()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
