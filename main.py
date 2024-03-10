import os
from flask import Flask, request, jsonify, render_template
import mysql.connector
from storagemgmtserv import StorageMgmtServ
from idntyaccmgmtserv import IdentityAccessManagementService
from usagemntrserv import UsageMonitorService
from viewgeneratorserv import ViewGeneratorService
from werkzeug.utils import secure_filename
from flask import session
import logging

logging.basicConfig(filename='application.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.secret_key = '0492325ebca2094b1df9a58947be957c'

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'osintRoot@786',
    'database': 'aws_cloud2'
}

def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

def get_authenticated_user_id():
    return session.get('user_id')

def is_admin():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return False
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT is_admin FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user and user['is_admin']


@app.route('/')
def index():
    return render_template('index.html')
@app.route('/admin')
def admin_dashboard():
    # Optional: Check if the user is an admin before rendering the dashboard
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    return render_template('admin.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'User logged out successfully'})

@app.route('/protected-resource')
def protected_resource():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'message': 'Access granted to protected resource'})

@app.route('/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM files WHERE id = %s AND user_id = %s", (file_id, user_id))
    file = cursor.fetchone()
    if file is None:
        return jsonify({'error': 'File not found or access denied'}), 404

    cursor.execute("DELETE FROM files WHERE id = %s", (file_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'message': 'File deleted successfully'})

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    try:
        IdentityAccessManagementService.signup(username, email, password)
        return jsonify({"message": "User registered successfully", "status": "success"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/signin', methods=['POST'])
def signin():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    try:
        user_id, is_successful = IdentityAccessManagementService.signin(username, password)
        if is_successful:
            session['user_id'] = user_id
            return jsonify({"message": "User signed in successfully", "user_id": user_id, "redirect": "/upload-page"})
        else:
            return jsonify({"message": "Invalid username or password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload-page')
def upload_page():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({'error': 'Unauthorized'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if not StorageMgmtServ.check_storage_limit(user_id, file_size):
        return jsonify({'error': 'Storage limit exceeded'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join('Users_data', filename)
    
    file.save(file_path)
    
    StorageMgmtServ.update_storage_usage(user_id, file_size)
    UsageMonitorService.track_usage(user_id, file_size)
    
    StorageMgmtServ.save_file_info(user_id, filename, file_size, file_path)
    
    return jsonify({'message': 'File uploaded successfully'}), 201

@app.route('/files', methods=['GET'])
def list_files():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, filename, filesize, upload_date FROM files WHERE user_id = %s", (user_id,))
    files = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(files)

# Admin routes
@app.route('/admin/users')
def list_users():
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT users.id, users.username, users.email, storage.storage_used
        FROM users
        LEFT JOIN storage ON users.id = storage.user_id
    """)
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users)

@app.route('/admin/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'User deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)
