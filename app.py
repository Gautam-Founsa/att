from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Admin, Student, Attendance
from face_utils import FaceRecognitionSystem
from werkzeug.security import generate_password_hash
from datetime import datetime, date, timedelta
import csv
import os
import logging
from functools import wraps
import os



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder="./templates", static_folder="./static")
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize face recognition system
face_system = FaceRecognitionSystem()

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# ===================== HELPER FUNCTIONS =====================

def admin_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def init_db():
    """Initialize database with default admin"""
    with app.app_context():
        db.create_all()
        
        # Check if admin exists
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            admin = Admin(username='admin')
            admin.set_password('admin123')  # Change this in production
            db.session.add(admin)
            db.session.commit()
            logger.info("Default admin created: username=admin, password=admin123")

# ===================== AUTHENTICATION ROUTES =====================

@app.route('/')
def index():
    """Home page - redirect to dashboard if logged in"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        print("USERNAME:", username)
        print("PASSWORD:", password)

        admin = Admin.query.filter_by(username=username).first()

        if admin:
            print("ADMIN FOUND")
        else:
            print("ADMIN NOT FOUND")

        if admin and admin.check_password(password):
            print("LOGIN SUCCESS")
            login_user(admin)
            return redirect(url_for('dashboard'))
        else:
            print("LOGIN FAILED")
            return "Invalid login"

    return render_template('login.html')
    

@app.route('/logout')
@login_required
def logout():
    """Admin logout"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

# ===================== DASHBOARD ROUTE =====================

@app.route('/dashboard')
@admin_required
def dashboard():
    """Main dashboard"""
    try:
        # Get statistics
        total_students = Student.query.count()
        today = date.today()
        today_attendance = Attendance.query.filter_by(date=today).count()
        
        # Get recent attendance
        recent_attendance = Attendance.query.order_by(Attendance.created_at.desc()).limit(10).all()
        
        return render_template('dashboard.html', 
                             total_students=total_students,
                             today_attendance=today_attendance,
                             recent_attendance=recent_attendance)
    except Exception as e:
        logger.error(f"Error in dashboard: {str(e)}")
        flash('Error loading dashboard', 'danger')
        return redirect(url_for('login'))

# ===================== STUDENT MANAGEMENT ROUTES =====================

@app.route('/add-student', methods=['GET', 'POST'])
@admin_required
def add_student():
    """Add new student"""
    if request.method == 'POST':
        try:
            student_id = request.form.get('student_id')
            name = request.form.get('name')
            course = request.form.get('course')
            email = request.form.get('email')
            
            # Check if student exists
            if Student.query.filter_by(student_id=student_id).first():
                flash('Student ID already exists', 'warning')
                return redirect(url_for('add_student'))
            
            # Create new student
            student = Student(
                student_id=student_id,
                name=name,
                course=course,
                email=email
            )
            db.session.add(student)
            db.session.commit()
            
            flash(f'Student {name} added successfully', 'success')
            return redirect(url_for('capture_faces', student_id=student_id))
        
        except Exception as e:
            logger.error(f"Error adding student: {str(e)}")
            flash('Error adding student', 'danger')
    
    return render_template('add_student.html')

@app.route('/students')
@admin_required
def view_students():
    """View all students"""
    try:
        students = Student.query.all()
        return render_template('students.html', students=students)
    except Exception as e:
        logger.error(f"Error viewing students: {str(e)}")
        flash('Error loading students', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/student/<student_id>/delete', methods=['POST'])
@admin_required
def delete_student(student_id):
    """Delete a student"""
    try:
        student = Student.query.filter_by(student_id=student_id).first()
        if student:
            db.session.delete(student)
            db.session.commit()
            flash(f'Student {student.name} deleted successfully', 'success')
        else:
            flash('Student not found', 'danger')
    except Exception as e:
        logger.error(f"Error deleting student: {str(e)}")
        flash('Error deleting student', 'danger')
    
    return redirect(url_for('view_students'))

# ===================== FACE CAPTURE & TRAINING ROUTES =====================

@app.route('/capture-faces/<student_id>')
@admin_required
def capture_faces(student_id):
    """Capture face images for a student"""
    try:
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            flash('Student not found', 'danger')
            return redirect(url_for('add_student'))
        
        return render_template('capture_faces.html', student=student)
    except Exception as e:
        logger.error(f"Error in capture_faces: {str(e)}")
        flash('Error loading capture page', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/api/capture-face', methods=['POST'])
@admin_required
def api_capture_face():
    """API endpoint to capture face (placeholder - manual capture via camera)"""
    try:
        student_id = request.json.get('student_id')
        student = Student.query.filter_by(student_id=student_id).first()
        
        if not student:
            return jsonify({'success': False, 'message': 'Student not found'}), 404
        
        # Start face capture
        face_count = face_system.get_face_count(student_id)
        
        return jsonify({
            'success': True,
            'message': 'Ready to capture faces. Use the capture button.',
            'current_count': face_count
        })
    except Exception as e:
        logger.error(f"Error in api_capture_face: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/start-capture', methods=['POST'])
@admin_required
def api_start_capture():
    """Start face capture from webcam"""
    try:
        student_id = request.json.get('student_id')
        num_images = request.json.get('num_images', 30)
        
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            return jsonify({'success': False, 'message': 'Student not found'}), 404
        
        # Capture faces using OpenCV
        success = face_system.capture_face_images(student_id, student.name, num_images)
        
        if success:
            # Update student face data count
            face_count = face_system.get_face_count(student_id)
            student.face_data_count = face_count
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Successfully captured {face_count} face images',
                'face_count': face_count
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to capture faces'}), 500
    
    except Exception as e:
        logger.error(f"Error in api_start_capture: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/train-model')
@admin_required
def train_model():
    """Train face recognition model"""
    try:
        return render_template('train_model.html')
    except Exception as e:
        logger.error(f"Error in train_model: {str(e)}")
        flash('Error loading train page', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/api/train-model', methods=['POST'])
@admin_required
def api_train_model():
    """Train the face recognition model"""
    try:
        success = face_system.train_model()
        
        if success:
            # Mark students as trained
            students = Student.query.all()
            for student in students:
                if face_system.get_face_count(student.student_id) > 0:
                    student.face_trained = True
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Model trained successfully with {len(face_system.known_face_encodings)} encodings'
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to train model'}), 500
    
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ===================== ATTENDANCE ROUTES =====================

@app.route('/attendance')
@admin_required
def attendance():
    """Take attendance using face recognition"""
    return render_template('attendance.html')

@app.route('/api/mark-attendance', methods=['POST'])
@admin_required
def api_mark_attendance():
    """Mark attendance from recognized face (API endpoint)"""
    try:
        data = request.json
        student_id = data.get('student_id')
        confidence = data.get('confidence', 0)
        
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            return jsonify({'success': False, 'message': 'Student not found'}), 404
        
        # Check if already marked today
        today = date.today()
        existing = Attendance.query.filter_by(
            student_id=student.id,
            date=today
        ).first()
        
        if existing:
            return jsonify({
                'success': False,
                'message': f'Attendance already marked for {student.name} today'
            })
        
        # Create attendance record
        now = datetime.now()
        attendance = Attendance(
            student_id=student.id,
            date=today,
            time=now.time(),
            status='Present',
            confidence=confidence
        )
        db.session.add(attendance)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Attendance marked for {student.name}',
            'student_name': student.name,
            'time': now.strftime('%H:%M:%S')
        })
    
    except Exception as e:
        logger.error(f"Error marking attendance: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/attendance-records', methods=['GET', 'POST'])
@admin_required
def attendance_records():
    """View attendance records"""
    try:
        # Get filter parameters
        student_filter = request.args.get('student', '')
        date_filter = request.args.get('date', '')
        
        query = Attendance.query
        
        if student_filter:
            query = query.filter(
                Student.name.ilike(f'%{student_filter}%')
            ).join(Student)
        
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                query = query.filter_by(date=filter_date)
            except:
                pass
        
        # Order by date and time
        records = query.order_by(Attendance.date.desc(), Attendance.time.desc()).all()
        students = Student.query.all()
        
        return render_template('attendance_records.html', 
                             records=records, 
                             students=students,
                             student_filter=student_filter,
                             date_filter=date_filter)
    
    except Exception as e:
        logger.error(f"Error in attendance_records: {str(e)}")
        flash('Error loading attendance records', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/export-attendance')
@admin_required
def export_attendance():
    """Export attendance as CSV"""
    try:
        # Get filter parameters
        student_filter = request.args.get('student', '')
        date_filter = request.args.get('date', '')
        
        query = Attendance.query
        
        if student_filter:
            query = query.filter(
                Student.name.ilike(f'%{student_filter}%')
            ).join(Student)
        
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                query = query.filter_by(date=filter_date)
            except:
                pass
        
        records = query.order_by(Attendance.date.desc(), Attendance.time.desc()).all()
        
        # Create CSV
        csv_filename = f'attendance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        attendance_dir = 'attendance'
        os.makedirs(attendance_dir, exist_ok=True)
        csv_path = os.path.join(attendance_dir, csv_filename)
        
        with open(csv_path, 'w', newline='') as csvfile:
            fieldnames = ['Student ID', 'Student Name', 'Course', 'Date', 'Time', 'Status', 'Confidence']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for record in records:
                writer.writerow({
                    'Student ID': record.student.student_id,
                    'Student Name': record.student.name,
                    'Course': record.student.course,
                    'Date': record.date.strftime('%Y-%m-%d'),
                    'Time': record.time.strftime('%H:%M:%S'),
                    'Status': record.status,
                    'Confidence': f'{record.confidence:.2f}' if record.confidence else 'N/A'
                })
        
        flash(f'Attendance exported to {csv_filename}', 'success')
        return redirect(url_for('attendance_records'))
    
    except Exception as e:
        logger.error(f"Error exporting attendance: {str(e)}")
        flash('Error exporting attendance', 'danger')
        return redirect(url_for('attendance_records'))

# ===================== API ROUTES FOR ATTENDANCE (Real-time) =====================

@app.route('/api/recognize-faces', methods=['POST'])
@admin_required
def api_recognize_faces():
    """Recognize faces from uploaded frame"""
    try:
        import base64
        import cv2
        import numpy as np
        
        data = request.json
        frame_data = data.get('frame')
        
        if not frame_data:
            return jsonify({'success': False, 'message': 'No frame provided'}), 400
        
        # Decode base64 frame
        frame_bytes = base64.b64decode(frame_data.split(',')[1])
        nparr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'success': False, 'message': 'Invalid frame'}), 400
        
        # Recognize faces
        results = face_system.recognize_faces(frame)
        
        recognized_faces = []
        for name, confidence, (top, right, bottom, left) in results:
            if name != "Unknown" and confidence >= 0.7:
                recognized_faces.append({
                    'name': name,
                    'confidence': float(confidence)
                })
        
        return jsonify({
            'success': True,
            'faces': recognized_faces
        })
    
    except Exception as e:
        logger.error(f"Error recognizing faces: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ===================== ERROR HANDLERS =====================

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return "page not found", 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(e)}")
    return "Internal server error", 500

# ===================== MAIN =====================

if __name__ == '__main__':
    # Initialize database and create default admin
    init_db()
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5005)