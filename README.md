# Velora – AI Attendance System

Velora is an AI-powered attendance management system designed to make classroom attendance faster and more convenient using **face recognition and voice recognition**.

Instead of manually taking attendance, teachers can create subjects/classes, enroll students, and record attendance using a classroom image. The system identifies registered students and records their attendance automatically.

---

## 🚀 Features

### 👨‍🏫 Teacher Dashboard

- Teacher registration and login
- Create and manage subjects
- Share subject/class access with students
- View enrolled students
- Take attendance using a classroom photo
- View attendance results
- Voice-based attendance support

### 👨‍🎓 Student Dashboard

- Student registration
- Student login
- Join subjects/classes
- Face registration
- Voice registration
- View attendance-related information

### 🤖 AI-Based Attendance

Velora uses:

- **Face Recognition** to identify students from classroom images
- **Voice Recognition** for voice-based attendance
- Face embeddings for student identification
- Voice embeddings for speaker identification

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Core programming language |
| Streamlit | Web application and UI |
| Supabase | Database and backend services |
| dlib | Face detection and face embeddings |
| face_recognition_models | Face recognition model |
| Resemblyzer | Voice recognition |
| NumPy | Numerical operations |
| scikit-learn | Machine learning |
| Pandas | Data processing |
| Pillow | Image processing |

---

## 🏗️ Project Structure

```text
velora-AI_auto_attendance/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── assets/
│   ├── logo.png
│   ├── footer.png
│   ├── studenet_login.png
│   └── teacher_login.png
│
└── src/
    │
    ├── components/
    │   ├── dialog_add_photo.py
    │   ├── dialog_attendance_results.py
    │   ├── dialog_auto_enroll.py
    │   ├── dialog_create_subject.py
    │   ├── dialog_enroll.py
    │   ├── dialog_share_subject.py
    │   ├── dialog_voice_attendance.py
    │   ├── footer.py
    │   ├── header.py
    │   └── subject_card.py
    │
    ├── database/
    │   ├── config.py
    │   └── db.py
    │
    ├── pipelines/
    │   ├── face_pipeline.py
    │   └── voice_pipeline.py
    │
    ├── screens/
    │   ├── home_screen.py
    │   ├── student_screen.py
    │   └── teacher_screen.py
    │
    └── ui/
        └── base_layout.py
```
🔄 How Velora Works
1. Teacher Registration

A teacher creates an account using the teacher registration system.

2. Create a Subject

After logging in, the teacher can create a subject/class.

3. Student Enrollment

Students can register and join the appropriate subject.

During registration, the system can collect:

Student information
Face data
Voice data
4. Attendance

The teacher can use the attendance system to capture a classroom image.

Velora processes the image and compares detected faces with registered student face embeddings.

5. Attendance Result

The system identifies registered students and generates an attendance result showing whether students are:

✅ Present
❌ Absent

Attendance records are stored in the database.

🧠 Face Recognition Pipeline

The face recognition pipeline uses dlib to:

Detect faces
Extract facial landmarks
Generate face embeddings
Compare the detected embedding with registered student embeddings
Identify the matching student
Mark attendance when the similarity is within the configured threshold
🎙️ Voice Recognition

Velora also includes voice-based attendance using Resemblyzer.

The voice pipeline generates voice embeddings and compares them with registered voice data to identify the speaker.

🗄️ Database

Velora uses Supabase for storing application data.

The database manages information related to:

Teachers
Students
Subjects
Enrollments
Attendance logs
Face embeddings
Voice-related data

Database schema and credentials are not included in this repository.
```
⚙️ Installation
1. Clone the repository
git clone https://github.com/Kunalthakur01/velora-AI_auto_attendance.git
cd velora-AI_auto_attendance
2. Create a virtual environment

Windows:

python -m venv .venv

Activate it:

.venv\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
🔐 Environment Configuration
```
Velora requires Supabase configuration.

Create:

.streamlit/secrets.toml

Example:
```
SUPABASE_URL = "your_supabase_url"
SUPABASE_KEY = "your_supabase_key"
```
Do not commit your secrets.toml file to GitHub.

It is already excluded through .gitignore.

▶️ Run the Application

Start the Streamlit application:

streamlit run app.py

The application will open in your browser.

📸 Application Flow
```
                    ┌─────────────────┐
                    │     Velora      │
                    │  Home Dashboard  │
                    └────────┬────────┘
                             │
                 ┌───────────┴───────────┐
                 │                       │
          ┌──────▼──────┐         ┌──────▼──────┐
          │   Teacher   │         │   Student   │
          │   Portal    │         │   Portal    │
          └──────┬──────┘         └──────┬──────┘
                 │                       │
          Create Subject            Register
                 │                       │
          Enroll Students          Face + Voice
                 │                       │
                 └───────────┬───────────┘
                             │
                     ┌───────▼────────┐
                     │   Attendance   │
                     │     System     │
                     └───────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Face / Voice AI │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │    Attendance   │
                    │     Result      │
                    └─────────────────┘
```
🔒 Security

The following files and information should remain private:

Supabase credentials
API keys
.streamlit/secrets.toml
Environment variables
Private student biometric data

Never commit credentials or sensitive biometric information to GitHub.

🎯 Project Goals

Velora aims to reduce the time and manual effort required for classroom attendance while providing a centralized system for managing students, subjects, and attendance records.

👨‍💻 Developer

Kunal Singh

BCA Student | AI/ML Enthusiast

GitHub:
```
https://github.com/Kunalthakur01
```
