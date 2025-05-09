import cv2
import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from deepface import DeepFace
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics.texture import Texture
from kivy.clock import Clock

# Initialize Firebase Admin SDK
cred = credentials.Certificate('firebase.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

class FaceVoteApp(App):
    def build(self):
        # Initial setup
        self.current_user_id = "user123"  # Example user ID for testing
        self.user_voted = False  # Track if user has voted to prevent duplicates
        self.voter_id_image_path = "Devadharshini.jpg"  # Path to pre-stored voter ID image for comparison
        self.candidate_votes = {"Candidate 1": 0, "Candidate 2": 0}  # Vote count dictionary
        
        # Main layout
        self.layout = BoxLayout(orientation='vertical')

        # Camera feed
        self.image = Image()
        self.layout.add_widget(self.image)

        # Buttons for actions
        self.capture_button = Button(text="Capture Image")
        self.capture_button.bind(on_press=self.capture_image)
        self.layout.add_widget(self.capture_button)

        # Voting buttons, disabled until authentication
        self.vote_button_1 = Button(text="Vote for Candidate 1")
        self.vote_button_1.bind(on_press=lambda x: self.cast_vote("Candidate 1"))
        self.vote_button_1.disabled = True
        self.layout.add_widget(self.vote_button_1)

        self.vote_button_2 = Button(text="Vote for Candidate 2")
        self.vote_button_2.bind(on_press=lambda x: self.cast_vote("Candidate 2"))
        self.vote_button_2.disabled = True
        self.layout.add_widget(self.vote_button_2)

        # Message label
        self.message_label = Label(text="Ready to capture image")
        self.layout.add_widget(self.message_label)

        # OpenCV capture setup
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0 / 30.0)

        return self.layout

    def update(self, dt):
        # Capture frame from OpenCV and display in Kivy
        ret, frame = self.capture.read()
        if ret:
            buf = cv2.flip(frame, 0).tostring()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.image.texture = texture
        else:
            self.message_label.text = "Error: Unable to capture frame"

    def capture_image(self, instance):
        # Capture an image from the camera and authenticate user
        ret, frame = self.capture.read()
        if ret:
            self.message_label.text = "Verifying identity..."
            authorized = self.authenticate_user(frame)
            if authorized:
                self.message_label.text = "Face recognized. Authentication successful!"
                self.vote_button_1.disabled = False
                self.vote_button_2.disabled = False
            else:
                self.message_label.text = "Face does not match voter ID. Access denied."
        else:
            self.message_label.text = "Failed to capture image."

    def authenticate_user(self, frame):
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = DeepFace.verify(rgb_frame, self.voter_id_image_path, model_name="VGG-Face")
            return result["verified"]
        except Exception as e:
            print(f"Error during face authentication: {e}")
            self.message_label.text = "Error during face authentication."
            return False

    def cast_vote(self, candidate):
        # Prevent duplicate voting
        if self.user_voted:
            self.message_label.text = "Duplicate vote attempt detected! Vote not counted."
            print("Duplicate voting attempt reported.")
            return

        # Record the vote in Firebase Firestore
        vote_data = {
            "userId": self.current_user_id,
            "vote": candidate,
            "timestamp": datetime.datetime.now()
        }
        try:
            # Use .add() to auto-generate a unique ID for each vote document to avoid overwriting
            db.collection("votes").add(vote_data)
            
            # Update UI and output upon successful voting
            self.message_label.text = f"Vote for {candidate} submitted successfully!"
            print("Voting Successful")
            print("Thank You for Voting")
            
            # Update candidate vote count
            self.candidate_votes[candidate] += 1

            # Disable both vote buttons to prevent further voting
            self.vote_button_1.disabled = True
            self.vote_button_2.disabled = True
            self.user_voted = True  # Mark user as having voted

        except Exception as e:
            # Display the error message on the app interface and in the console
            error_message = f"Error submitting vote: {str(e)}"
            self.message_label.text = error_message
            print(error_message)

    def reset_for_next_user(self):
        # Reset user state and UI for next voter
        self.user_voted = False
        self.vote_button_1.disabled = True
        self.vote_button_2.disabled = True
        self.message_label.text = "Ready for next voter. Capture image to start."

    def display_vote_counts(self):
        # Display vote counts for each candidate in the output
        print(f"Total votes for Candidate 1: {self.candidate_votes['Candidate 1']}")
        print(f"Total votes for Candidate 2: {self.candidate_votes['Candidate 2']}")

    def on_stop(self):
        # Release the camera and display final vote counts when app closes
        self.capture.release()
        self.display_vote_counts()
        print("Application closed. Final vote counts displayed.")
        
# Run the app
if __name__ == '__main__':
    FaceVoteApp().run()
