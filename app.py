# import library 
from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api 
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy 
from functools import wraps

# import library lain
import jwt 
import os 
import datetime 

# inisiasi objek flask dll
app = Flask(__name__)
api = Api(app)
CORS(app)

# konfigurasi database membuat file db.sqlite 
filename = os.path.dirname(os.path.abspath(__file__))
database = 'sqlite:///' + os.path.join(filename, 'db.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = database 
db = SQLAlchemy(app)
app.app_context().push()
# konfigurasi secret key 
app.config['SECRET_KEY'] = "inirahasianegara"

# membuat model database authentikasi (login, register)
class AuthModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    password = db.Column(db.String(100))

# create model database ke dalam file db.sqlite
db.create_all()

# membuat decorator
def pakai_token(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.args.get('datatoken') 
        if not token:
            return make_response(jsonify({"msg":"Token tidak ada"}), 401)
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return make_response(jsonify({"msg":"Token invalid"}), 401)
        return f(*args, **kwargs)
    return decorator

# membuat routing endpoint 
# routing authentikasi  register
class RegisterUser(Resource):
    def post(self):
        dataEmail = request.form.get('email')
        dataPassword = request.form.get('password')

        # cek apakah email & password ada
        if dataEmail and dataPassword:
            # tulis data authentikasi ke db.sqlite
            dataModel = AuthModel(email=dataEmail, password=dataPassword)
            db.session.add(dataModel)
            db.session.commit()
            return make_response(jsonify({"msg":"Registrasi berhasil"}), 200)
        return jsonify({"msg":"Username / password tidak boleh kosong"})

# routing untuk authentikasi login 
class LoginUser(Resource):
    def post(self):
        dataEmail = request.form.get('email')
        dataPassword = request.form.get('password')

        # cek email dan password 
        queryEmail = [data.email for data in AuthModel.query.all()]
        queryPassword = [data.password for data in AuthModel.query.all()]
        if dataEmail in queryEmail and dataPassword in queryPassword :
            # klo login sukses
            # generate token authentikasi untuk user
            token = jwt.encode(
                {
                    "email":queryEmail, "exp":datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
                }, app.config['SECRET_KEY'],  algorithm="HS256"
            )
            return make_response(jsonify({"msg":"Login Berhasil", "token":token}), 200)

        # klo login gagal
        return jsonify({"msg":"Login gagal, username / password salah"})

# endpoint home pakai token
class HomePage(Resource):
    @pakai_token
    def get(self):
        return jsonify({"msg":"ini adalah halaman home"})

        
# inisiasi resource api 
api.add_resource(RegisterUser, "/api/register", methods=["POST"])
api.add_resource(LoginUser, "/api/login", methods=["POST"])
api.add_resource(HomePage, "/api/home", methods=["GET"])


# jalankan aplikasi app.py 
if __name__ == "__main__":
    app.run(debug=True)