import cv2
import os
import numpy as np
import face_recognition
import pickle
from pathlib import Path
import logging
import time

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaceRecognitionSystem:
    def __init__(self, dataset_path='dataset', model_path='trainer'):
        self.dataset_path = dataset_path
        self.model_path = model_path

        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        self.known_face_encodings = []
        self.known_face_names = []
        self.student_data = {}

        Path(dataset_path).mkdir(parents=True, exist_ok=True)
        Path(model_path).mkdir(parents=True, exist_ok=True)

        self.load_model()

    # ===================== CAPTURE FACES (UPDATED FOR STABILITY) =====================

    def capture_face_images(self, student_id, student_name, num_images=30):
        cap = None
        try:
            student_dir = os.path.join(self.dataset_path, student_id)
            Path(student_dir).mkdir(parents=True, exist_ok=True)

            # Mac camera fix: CAP_AVFOUNDATION is correct for macOS
            cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
            time.sleep(2)  # Give camera time to initialize

            if not cap.isOpened():
                logger.error("❌ Cannot open webcam")
                return False

            count = 0
            logger.info(f"Capturing {num_images} images for {student_name}")

            # Added a timeout to prevent infinite loops if no faces are found
            start_time = time.time()
            timeout = 60  # 60 seconds max

            while count < num_images and (time.time() - start_time) < timeout:
                ret, frame = cap.read()

                if not ret or frame is None:
                    logger.warning("⚠️ Frame error, retrying...")
                    continue

                frame = cv2.flip(frame, 1)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

                for (x, y, w, h) in faces:
                    roi = gray[y:y + h, x:x + w]
                    
                    # Fix: Ensure ROI is valid and not empty before writing
                    if roi is not None and roi.size > 0:
                        img_path = os.path.join(student_dir, f'{student_id}_{count}.jpg')
                        cv2.imwrite(img_path, roi)
                        count += 1
                        logger.info(f"✅ Captured {count}/{num_images}")
                        
                        # Stop if we hit the limit during this detection
                        if count >= num_images:
                            break
                    
                    # Small sleep to prevent overwhelming disk I/O
                    time.sleep(0.1)

                # IMPORTANT: Removed cv2.imshow and cv2.waitKey to avoid macOS C++ exceptions

            if count < num_images:
                logger.warning(f"Capture timed out. Only {count} images saved.")

            return count > 0

        except Exception as e:
            logger.error(f"Error capturing face images: {str(e)}")
            return False
        finally:
            if cap:
                cap.release()
            # cv2.destroyAllWindows() is removed as no windows are created

    # ===================== TRAIN MODEL =====================

    def train_model(self):
        try:
            logger.info("Training model...")
            self.known_face_encodings = []
            self.known_face_names = []

            for student_id in os.listdir(self.dataset_path):
                student_path = os.path.join(self.dataset_path, student_id)
                if not os.path.isdir(student_path):
                    continue

                for image_name in os.listdir(student_path):
                    image_path = os.path.join(student_path, image_name)
                    if not image_path.lower().endswith(('.jpg', '.png', '.jpeg')):
                        continue

                    try:
                        image = face_recognition.load_image_file(image_path)
                        encodings = face_recognition.face_encodings(image)
                        if encodings:
                            self.known_face_encodings.append(encodings[0])
                            self.known_face_names.append(student_id)
                    except Exception as e:
                        logger.warning(f"Skipping {image_path}: {e}")

            self.save_model()
            logger.info("✅ Training completed")
            return True

        except Exception as e:
            logger.error(f"Training error: {str(e)}")
            return False

    # ===================== RECOGNITION =====================

    def recognize_faces(self, frame):
        try:
            if not self.known_face_encodings:
                return []

            small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
            locations = face_recognition.face_locations(rgb)
            encodings = face_recognition.face_encodings(rgb, locations)

            results = []
            for encoding, loc in zip(encodings, locations):
                matches = face_recognition.compare_faces(self.known_face_encodings, encoding)
                distances = face_recognition.face_distance(self.known_face_encodings, encoding)
                name, confidence = "Unknown", 0

                if len(distances) > 0:
                    best = np.argmin(distances)
                    if matches[best]:
                        name = self.known_face_names[best]
                        confidence = 1 - distances[best]
                results.append((name, confidence, loc))
            return results
        except Exception as e:
            logger.error(f"Recognition error: {str(e)}")
            return []

    # ===================== SAVE / LOAD =====================

    def save_model(self):
        try:
            data = {'encodings': self.known_face_encodings, 'names': self.known_face_names}
            with open(os.path.join(self.model_path, 'face_model.pkl'), 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            logger.error(f"Save error: {str(e)}")

    def load_model(self):
        try:
            path = os.path.join(self.model_path, 'face_model.pkl')
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    data = pickle.load(f)
                self.known_face_encodings = data['encodings']
                self.known_face_names = data['names']
                logger.info("Model loaded")
        except Exception as e:
            logger.error(f"Load error: {str(e)}")

    def get_face_count(self, student_id):
        try:
            student_dir = os.path.join(self.dataset_path, student_id)
            if os.path.exists(student_dir):
                return len([f for f in os.listdir(student_dir) if f.endswith('.jpg')])
            return 0
        except:
            return 0