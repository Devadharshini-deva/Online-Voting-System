# Online-Voting-System
Face Recognition Voting System

This is a secure and interactive face-recognition-based voting system built with Python, Kivy, OpenCV, and Firebase. It captures the user's face via webcam, verifies it against a pre-stored voter image, and allows the user to vote once for one of two candidates.

Key Features

- Face Verification using DeepFace and OpenCV
- Firebase Firestore Integration to securely record votes
- Duplicate Voting Prevention
- Real-Time Vote Count Tracking
- User-Friendly GUI built with Kivy

Tech Stack

- Python 3.10+
- OpenCV – For webcam capture and image processing
- DeepFace – Facial recognition and verification
- Kivy – Cross-platform GUI framework
- Firebase Admin SDK – For backend Firestore database

Installation

 1. Clone the Repository
```bash
git clone https://github.com/yourusername/face-recognition-voting.git
cd face-recognition-voting

2.Set Up Virtual Environment (Optional but Recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

3. Install Required Packages
pip install -r requirements.txt

4.Add Firebase Credentials
Place your firebase.json (Firebase service account key) file in the root directory.

5.Run the Application
python voting.py

