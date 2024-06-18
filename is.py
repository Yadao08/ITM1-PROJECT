# app.py

from flask import Flask, render_template, redirect, request, url_for, flash
from werkzeug.utils import secure_filename
import mysql.connector
import os

app = Flask(__name__, static_url_path='/static')

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure 'uploads' directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'project_db',
}

def allowed_file(filename):
    # Check if the file has an allowed extension
    allowed_extensions = {'png', 'jpeg', 'jpg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def connect_db():
    return mysql.connector.connect(**db_config)

def insert_data(first_name, middle_name, last_name, contact, gender, birth_date, course,
                institutional_email, student_number, password, photo_path):
    conn = connect_db()
    cursor = conn.cursor()

    # Extract the file name from the photo_path
    photo_filename = os.path.basename(photo_path)

    cursor.execute('''
        INSERT INTO student_tbl (first_name, middle_name, last_name, contact, gender, birth_date, course,
                   institutional_email, student_number, password, photo_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (first_name, middle_name, last_name, contact, gender, birth_date, course,
          institutional_email, student_number, password, photo_filename))
    conn.commit()
    conn.close()

def get_all_data():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student_tbl")
    flask_data = cursor.fetchall()
    conn.close()
    print(flask_data) 
    return flask_data

@app.route("/registration")
def registration():
    return render_template('user_form.html')

@app.route("/form", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        first_name = request.form['fname']
        middle_name = request.form['midname']
        last_name = request.form['lname']
        contact = request.form['tel']
        gender = request.form['gen']
        birth_date = request.form['bdate']
        course = request.form['crsename']
        institutional_email = request.form['mail']
        student_number = request.form['studnum']
        password = request.form['pass']

        # Handle file upload
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename != '' and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                photo.save(photo_path)
            else:
                return render_template('user_form.html', error="Invalid file type. Please choose another file.")

        insert_data(first_name, middle_name, last_name, contact, gender, birth_date, course,
                    institutional_email, student_number, password, photo_path)

    flask_data = get_all_data()

    return render_template('user_login.html', htmldata=flask_data)

@app.route("/login")
def log():
    return render_template('user_login.html')

@app.route("/userlogin", methods=["POST", "GET"])
def loginuser():
    if request.method == 'POST':
        student_number = request.form.get('studnum')
        password = request.form.get('pass')

        # You need to query the database to check if the provided credentials are valid
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM student_tbl WHERE student_number = %s AND password = %s", (student_number, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            # Successful login, display the details of the logged-in user
            user_data = {
                'student_id': user[0],
                'first_name': user[1],
                'middle_name': user[2],
                'last_name': user[3],
                'contact': user[4],
                'gender': user[5],
                'birth_date': user[6],
                'institutional_email': user[7],
                'course': user[8],
                'student_number': user[9],
                'password': user[10],
                'photo_path': user[11],
            }
            # Successful login, you can redirect to a new page or do something else
            return render_template('user_home.html', user=user_data)
        else:
            # Failed login, you can render an error message or redirect to the login page
            return render_template('user_login.html', error="Invalid credentials")

    # If the request method is GET, render the login form
    return render_template('user_login.html')

@app.route("/admin")
def adminlog():
    return render_template('admin_login.html')

@app.route("/adminlogin", methods=["POST", "GET"])
def adminlogin():
    if request.method == 'POST':
        user_name = request.form.get('adname')
        password = request.form.get('adpass')

        # You need to query the database to check if the provided credentials are valid
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin_tbl WHERE user_name = %s AND password = %s", (user_name, password))
        user = cursor.fetchone()
        conn.close()
        
        return render_template('admin_display.html')
    else:
            # Failed login, you can render an error message or redirect to the login page
            return render_template('admin_login.html', error="Invalid credentials")

@app.route("/logout")
def logout():
    # You can perform additional logout logic here if needed
    return redirect(url_for('log'))  # Redirect to the login page

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
