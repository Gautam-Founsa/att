# AI-Based Attendance System using Face Recognition

A complete, fully functional web-based attendance system that uses face recognition to automatically mark student attendance.

## 🎯 Features

- **Admin Authentication**: Secure login/logout system for administrators
- **Student Management**: Add students, capture face images, manage student data
- **Face Recognition**: Real-time face detection and recognition using OpenCV
- **Automated Attendance**: Automatically mark attendance when faces are recognized
- **Attendance Dashboard**: View, filter, and export attendance records
- **Model Training**: Train face recognition model with captured images
- **Live Camera Feed**: Real-time camera feed with face detection
- **CSV Export**: Export attendance records in CSV format
- **Responsive UI**: Clean, modern, and mobile-friendly interface

## 📋 Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Backend**: Python Flask, Flask-SQLAlchemy, Flask-Login
- **AI/ML**: OpenCV, face_recognition library
- **Database**: SQLite (production-ready, can use MySQL)
- **Storage**: Local file system for face images

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Webcam (for capturing face images and taking attendance)
- Modern web browser

### Installation

1. **Clone or download the project**
   ```bash
   cd attendance_system
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   **Note**: If you encounter issues with face_recognition:
   - **Windows**: Use pre-compiled wheel or install Visual Studio C++ build tools
   - **macOS**: `pip install face_recognition`
   - **Linux**: Install required system packages first:
     ```bash
     sudo apt-get install build-essential cmake python3-dev
     pip install face_recognition
     ```

5. **Create necessary directories**
   ```bash
   mkdir -p dataset trainer attendance logs
   ```

## ▶️ Running the Application

1. **Activate virtual environment** (if not already activated)

2. **Run the Flask app**
   ```bash
   python app.py
   ```

3. **Open in browser**
   - Navigate to: `http://localhost:5000`

4. **Login with default credentials**
   - **Username**: `admin`
   - **Password**: `admin123`
   - **⚠️ Change these in production!**

## 📚 How to Use

### Step 1: Add Students
1. Click "Add Student" in the sidebar
2. Fill in student details (ID, Name, Course, Email)
3. Submit the form

### Step 2: Capture Face Images
1. You'll be redirected to "Capture Faces" page
2. Click "Start Face Capture (30 Images)"
3. Allow camera access when prompted
4. Position your face clearly in front of the camera
5. System will automatically capture 30 images
6. Repeat for all students (minimum 20-30 images per student recommended)

### Step 3: Train the Model
1. Go to "Train Model" from sidebar
2. Click "Train Model Now"
3. Wait for training to complete (1-5 minutes depending on number of images)
4. Success message will appear when done

### Step 4: Take Attendance
1. Go to "Take Attendance" from sidebar
2. Click "Start Camera"
3. Allow camera access
4. Students will be automatically recognized and marked present
5. Each student is marked only once per day
6. View recognized students in the list on the right

### Step 5: View Records
1. Go to "View Records" from sidebar
2. Filter by student name or date if needed
3. Click "Export as CSV" to download attendance data

## 📁 Project Structure

```
attendance_system/
├── app.py                      # Main Flask application
├── models.py                   # Database models
├── face_utils.py               # Face recognition utilities
├── config.py                   # Configuration file
├── requirements.txt            # Python dependencies
├── attendance.db               # SQLite database (auto-created)
├── templates/
│   ├── base.html              # Base template with navigation
│   ├── login.html             # Login page
│   ├── dashboard.html         # Main dashboard
│   ├── add_student.html       # Add student form
│   ├── students.html          # View all students
│   ├── capture_faces.html     # Face capture page
│   ├── train_model.html       # Model training page
│   ├── attendance.html        # Real-time attendance
│   ├── attendance_records.html # View records
│   └── error.html             # Error page
├── static/
│   ├── css/
│   │   └── style.css          # Main stylesheet
│   └── js/
│       └── script.js          # Main JavaScript
├── dataset/                    # Face images for each student
│   └── {student_id}/          # One folder per student
├── trainer/                    # Trained model files
│   └── face_model.pkl         # Trained face encodings
├── attendance/                 # Exported CSV files
└── logs/                       # Application logs
```

## 🔧 Configuration

Edit `config.py` to customize:
- Database URI
- Face recognition settings (tolerance, confidence)
- Upload limits
- Session timeout
- Secret key for production

## 🖥️ System Requirements

### Minimum
- CPU: Intel Core i5 or equivalent
- RAM: 4 GB
- Webcam: 720p or higher resolution

### Recommended
- CPU: Intel Core i7 or higher
- RAM: 8 GB+
- Webcam: 1080p or higher
- Good lighting conditions

## 📊 Performance Tips

1. **Image Quality**: Capture faces in good lighting conditions
2. **Image Count**: 30+ images per student for better accuracy
3. **Face Position**: Ensure faces are front-facing and clearly visible
4. **Model Retraining**: Retrain after adding new students
5. **Database**: Use MySQL in production for better performance

## 🔒 Security Notes

- Change default admin credentials immediately
- Use HTTPS in production
- Set strong SECRET_KEY in config
- Restrict database file permissions
- Use environment variables for sensitive config

## 🐛 Troubleshooting

### Camera not working
- Check browser permissions for camera access
- Try refreshing the page
- Ensure no other application is using the camera

### Face not detected
- Ensure good lighting conditions
- Position face directly in front of camera
- Retrain the model if new students are added

### Low accuracy
- Capture more face images (50+ recommended)
- Capture faces in different lighting conditions
- Adjust FACE_CONFIDENCE_THRESHOLD in config.py

### Import errors
- Reinstall dependencies: `pip install -r requirements.txt`
- For Windows, install Visual Studio C++ build tools
- On Linux, install build-essential: `sudo apt-get install build-essential`

### Database errors
- Delete `attendance.db` and restart app to reinitialize
- Check database permissions
- Ensure `trainer/face_model.pkl` is deleted before adding new students

## 📈 Future Enhancements

- [ ] Multi-face recognition per frame
- [ ] Liveness detection to prevent spoofing
- [ ] Email notifications for absent students
- [ ] Mobile app for on-the-go attendance
- [ ] Biometric authentication
- [ ] Advanced analytics and reports
- [ ] Integration with student management systems
- [ ] QR code based attendance backup
- [ ] Automated notifications to parents/guardians
- [ ] Attendance percentage calculator

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or report issues.

## 📧 Support

For support, please contact the development team or create an issue in the repository.

## 🙏 Acknowledgments

- OpenCV for computer vision capabilities
- face_recognition library by Adam Geitgey
- Bootstrap for UI framework
- Flask for web framework

---

**Note**: This system is designed for educational purposes. For production use, additional security measures, compliance checks, and optimizations are recommended.

**Version**: 1.0.0
**Last Updated**: 2024