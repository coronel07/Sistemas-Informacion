from flask import Flask, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from decimal import Decimal
import mercadopago


app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:cocoymati88@localhost:3306/pagoCobro'
sdk = mercadopago.SDK("TU_ACCESS_TOKEN")
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(db.Model, UserMixin):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    contraseña_usuario = db.Column(db.String(150), nullable=False)

    def get_id(self):
        return str(self.id_usuario)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    contraseña = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Registrar')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    contraseña = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')


class CheckoutForm(FlaskForm):
    payment_method = SelectField('Método de Pago', choices=[('tarjeta', 'Tarjeta de crédito'), ('mercado_pago', 'Mercado Pago')], validators=[DataRequired()])
    submit = SubmitField('Confirmar y Pagar')


class Producto(db.Model):
    __tablename__ = 'producto'
    id_producto = db.Column(db.Integer, primary_key=True)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    cantidad_producto = db.Column(db.Integer, nullable=False)
    id_carrito = db.Column(db.Integer, db.ForeignKey('carrito.id_carrito'))
    nombre_producto = db.Column(db.String(150), nullable=False)
    imagen_producto = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Producto {self.nombre_producto}>"


@app.route('/')
def index():
    return render_template('index.html')  # Solo renderizar la página principal


@app.route('/productos')
def productos():
    productos = Producto.query.all()  # Obtener todos los productos de la base de datos
    return render_template('productos.html', productos=productos)  # Pasar productos a la plantilla


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        nuevo_usuario = User(email=form.email.data, contraseña_usuario=form.contraseña.data)
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('Registro exitoso. Puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        usuario = User.query.filter_by(email=form.email.data).first()
        if usuario and usuario.contraseña_usuario == form.contraseña.data:
            login_user(usuario)
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('checkout'))
        else:
            flash('Credenciales inválidas.', 'danger')
    return render_template('login.html', form=form)


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    # Inicializa el carrito y el total
    carrito = []
    total_carrito = Decimal(0.0)  # Usar Decimal para mantener precisión

    # Verifica si hay un carrito en la sesión
    if 'carrito' in session:
        carrito_ids = session['carrito']
        # Obtener detalles de los productos
        for id_producto in carrito_ids:
            producto = Producto.query.get(id_producto)
            if producto:
                carrito.append(producto)
                total_carrito += Decimal(producto.precio)  # Sumar usando Decimal

    form = CheckoutForm()

    if form.validate_on_submit():
        # Inicializar el SDK de Mercado Pago con tu access token
        sdk = mercadopago.SDK("TU_ACCESS_TOKEN")
        
        # Crear preferencia de pago
        preference_data = {
            "items": [
                {
                    "title": producto.descripcion,
                    "quantity": 1,
                    "unit_price": float(producto.precio)
                } for producto in carrito
            ],
            "back_urls": {
                "success": url_for('pago_exitoso', _external=True),
                "failure": url_for('pago_fallido', _external=True),
                "pending": url_for('pago_pendiente', _external=True)
            },
            "auto_return": "approved",
        }

        preference_response = sdk.preference().create(preference_data)
        preference_id = preference_response["response"]["id"]

        # Redirigir al usuario a la página de pago de Mercado Pago
        return redirect(preference_response["response"]["init_point"])

    return render_template('checkout.html', form=form, carrito=carrito, total_carrito=total_carrito)


@app.route('/confirmacion_pago')
@login_required
def confirmacion_pago():
    # Aquí podrías agregar lógica para verificar el estado del pago
    return render_template('confirmacion_pago.html')


@app.route('/eliminar_producto/<int:id>', methods=['POST'])
@login_required
def eliminar_producto(id):
    # Verifica si hay un carrito en la sesión
    if 'carrito' in session:
        carrito = session['carrito']
        # Eliminar el producto del carrito si existe
        if id in carrito:
            carrito.remove(id)
            session['carrito'] = carrito  # Actualiza la sesión con el carrito modificado
    
    flash('Producto eliminado del carrito.', 'success')
    return redirect(url_for('checkout'))


@app.route('/agregar_al_carrito/<int:id_producto>', methods=['POST'])
def agregar_al_carrito(id_producto):
    if 'carrito' not in session:
        session['carrito'] = []

    session['carrito'].append(id_producto)

    return redirect(url_for('productos'))  # Redirigir a la página de productos después de agregar


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('index'))

@app.route('/pago_exitoso')
def pago_exitoso():
    flash('Pago procesado con éxito. ¡Gracias por tu compra!', 'success')
    return redirect(url_for('index'))

@app.route('/pago_fallido')
def pago_fallido():
    flash('El pago no se pudo procesar. Por favor, intenta nuevamente.', 'danger')
    return redirect(url_for('checkout'))

@app.route('/pago_pendiente')
def pago_pendiente():
    flash('Tu pago está pendiente de aprobación.', 'warning')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crear todas las tablas
    app.run(debug=True)
