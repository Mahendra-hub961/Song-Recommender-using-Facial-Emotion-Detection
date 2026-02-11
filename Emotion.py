from flask import Flask, render_template, Response, jsonify, request
import cv2
from fer import FER
import pygame  # For playing music
import random

# Initialize Flask app
app = Flask(__name__)

# Initialize pygame mixer for music
pygame.mixer.init()

# Sample music library (stored in 'static' folder)
music_library = {
    'happy': ['static/happy_song1.mp3', 'static/happy_song2.mp3', 'static/happy_song3.mp3', 'static/happy_song4.mp3', 'static/happy_song5.mp3', 'static/happy_song6.mp3','static/happy_song7.mp3','static/happy_song8.mp3','static/happy_song9.mp3'],
    'sad': ['static/sad_song1.mp3', 'static/sad_song2.mp3','static/sad_song3.mp3','static/sad_song4.mp3','static/sad_song5.mp3','static/sad_song6.mp3','static/sad_song7.mp3','static/sad_song8.mp3','static/sad_song9.mp3','static/sad_song10.mp3','static/sad_song11.mp3'],
    'angry': ['static/angry_song1.mp3', 'static/angry_song2.mp3','static/angry_song3.mp3','static/angry_song4.mp3','static/angry_song5.mp3','static/angry_song6.mp3','static/angry_song7.mp3','static/angry_song8.mp3'],
    'neutral': ['static/neutral_song1.mp3','static/neutral_song2.mp3','static/neutral_song3.mp3','static/neutral_song4.mp3','static/neutral_song5.mp3','static/neutral_song6.mp3','static/neutral_song7.mp3','static/neutral_song8.mp3','static/neutral_song9.mp3','static/neutral_song10.mp3','static/neutral_song11.mp3']
}

# Initialize webcam (video capture)
cap = cv2.VideoCapture(0)

# Variable to track current playing music
current_song = None

# Emotion detection function
def detect_emotion(frame):
    emotion_detector = FER()
    emotions = emotion_detector.detect_emotions(frame)
    if emotions:
        dominant_emotion = max(emotions[0]['emotions'], key=emotions[0]['emotions'].get)
        return dominant_emotion
    return None

# Function to play music based on detected emotion
def play_music(emotion):
    global current_song
    if pygame.mixer.music.get_busy():
        return  # If music is already playing, do nothing
    
    if emotion in music_library:
        song = random.choice(music_library[emotion])
        print(f"Playing {song} for emotion: {emotion}")
        pygame.mixer.music.load(song)
        pygame.mixer.music.play()
        current_song = song

# Route to fetch current emotion (for frontend use)
@app.route('/emotion')
def get_emotion():
    ret, frame = cap.read()  # Capture frame for emotion detection
    if not ret:
        return jsonify({'emotion': 'none'})
    
    emotion = detect_emotion(frame)  # Get detected emotion
    return jsonify({'emotion': emotion})

# Route for video feed (shows webcam stream in HTML)
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Route to serve the main page
@app.route('/')
def index():
    return render_template('index.html')  # Render index.html page

# Route to handle playing music based on emotion
@app.route('/play_music')
def play_emotion_music():
    emotion = request.args.get('emotion')
    play_music(emotion)
    return jsonify({'song': current_song})

# Route to toggle play/pause
@app.route('/toggle_music')
def toggle_music():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        return jsonify({'isPlaying': False, 'song': current_song})
    else:
        pygame.mixer.music.unpause()
        return jsonify({'isPlaying': True, 'song': current_song})

# Route for video feed frames
def generate_frames():
    while True:
        ret, frame = cap.read()  # Capture frame from webcam
        if not ret:
            break
        
        emotion = detect_emotion(frame)  # Detect emotion from the frame
        if emotion:
            play_music(emotion)  # Play music based on detected emotion
        
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

if __name__ == '__main__':
    app.run(debug=True)
