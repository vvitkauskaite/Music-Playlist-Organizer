from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory, session
import datetime
import os
from werkzeug.utils import secure_filename
from abc import ABC, abstractmethod
from typing import List

app = Flask(__name__, static_folder="../frontend/static", template_folder="../frontend")
app.secret_key = 'your_super_secret_key_here'

# Directories
UPLOAD_FOLDER = os.path.abspath(os.path.join(app.root_path, 'Downloaded_Songs'))
PUBLIC_FOLDER = os.path.abspath(os.path.join(app.root_path, 'public_songs'))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PUBLIC_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'mp3'}

users_db = {}

# --- Singleton ---
class SingletonMP(type):
    _instances = {}
    def __call__(cls):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__()
        return cls._instances[cls]

# --- OOP Abstraction ---
class Song(ABC):
    def __init__(self, s_name: str, artist: str, duration: float):
        self.s_name = s_name
        self.artist = artist
        self.duration = duration

    @abstractmethod
    def play(self):
        pass

class PublicSong(Song):
    def play(self):
        print(f"Playing public song: {self.s_name} by {self.artist}")

class LocalSong(Song):
    def play(self):
        print(f"Playing local song: {self.s_name} by {self.artist}")

# --- Inheritance ---
class Library:
    def __init__(self, l_name: str):
        self.l_name = l_name
        self.songs: List[Song] = []

    def add_song(self, song: Song):
        if not any(s.s_name == song.s_name and s.artist == song.artist for s in self.songs):
            self.songs.append(song)

class PublicLibrary(Library):
    def load_public_songs(self):
        for fname in os.listdir(PUBLIC_FOLDER):
            if fname.endswith('.mp3'):
                name = os.path.splitext(fname)[0]
                self.add_song(PublicSong(name, "Various", 3.0))

class PrivateLibrary(Library):
    def load_from_filesystem(self):
        for fname in os.listdir(UPLOAD_FOLDER):
            if fname.endswith('.mp3'):
                name = os.path.splitext(fname)[0]
                self.add_song(LocalSong(name, "Unknown Artist", 3.0))

# --- Aggregation ---
class Playlist:
    def __init__(self, p_name, picture_path="default_picture.png", description=""):
        self.p_name = p_name
        self.picture_path = picture_path
        self.description = description
        self.songs: List[Song] = []

    def add_song(self, song: Song):
        self.songs.append(song)

    def remove_song(self, index: int):
        if 0 <= index < len(self.songs):
            del self.songs[index]

    def to_dict(self):
        return {
            "name": self.p_name,
            "picture": self.picture_path,
            "description": self.description,
            "songs": [song.s_name for song in self.songs]
        }

# --- User Class ---
class User:
    def __init__(self, u_name, gmail, password, photo_path="default_profile.png"):
        self.__u_name = u_name
        self.__gmail = gmail
        self.__password = password
        self.__photo_path = photo_path
        self.private_library = PrivateLibrary(f"{self.__u_name}'s Library")
        self.private_library.load_from_filesystem()
        self.playlists: List[Playlist] = []

    def delete_profile(self):
        del self.private_library
        self.playlists.clear()

    @property
    def name(self):
        return self.__u_name

# --- History Logger ---
class HistoryLogger:
    file_path = os.path.join(os.getcwd(), "Recently_Played.txt")

    @staticmethod
    def log_song(user_name: str, song: Song):
        try:
            print(f"[DEBUG] Logging: {user_name} - {song.s_name}")
            with open(HistoryLogger.file_path, 'a', encoding='utf-8') as file:
                file.write(f"{user_name},{song.s_name},{datetime.date.today()}\n")
        except Exception as e:
            print(f"[ERROR] Failed to log song: {e}")

    @staticmethod
    def read_history():
        try:
            with open(HistoryLogger.file_path, 'r', encoding='utf-8') as file:
                return file.readlines()
        except FileNotFoundError:
            return ["No history found."]

    @staticmethod
    def clear_history():
        with open(HistoryLogger.file_path, 'w', encoding='utf-8') as file:
            file.write('')


# --- Singleton Music Player ---
class MusicPlayer(metaclass=SingletonMP):
    def __init__(self):
        self.volume = 50
        self.current_song = None
        self.is_playing = False

    def play_song(self, user: User, song: Song):
        self.current_song = song
        song.play()
        HistoryLogger.log_song(user.name, song)
        self.is_playing = True

# --- Utility ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template("register.html")

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    u_name = data['u_name']
    if u_name in users_db:
        return jsonify(message="Username already taken."), 400
    user = User(u_name, data['gmail'], data['password'], data.get('photo', 'default_profile.png'))
    users_db[u_name] = user
    session['username'] = u_name
    return jsonify(message="Registration successful!", redirect="/dashboard")

@app.route('/upload_song', methods=['POST'])
def upload_song():
    if 'file' not in request.files:
        return jsonify(message="No file part"), 400
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify(message="Invalid file"), 400
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return jsonify(message=f"Uploaded '{filename}' successfully!"), 200

@app.route('/songs')
def list_songs():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    mp3_files = [
        {"filename": f, "url": url_for('serve_mp3', filename=f)}
        for f in files if f.lower().endswith('.mp3')
    ]
    return jsonify(songs=mp3_files)

@app.route('/public_songs')
def list_public():
    files = os.listdir(PUBLIC_FOLDER)
    mp3_files = [
        {"filename": f, "url": url_for('serve_public', filename=f)}
        for f in files if f.lower().endswith('.mp3')
    ]
    return jsonify(songs=mp3_files)

@app.route('/Downloaded_Songs/<filename>')
def serve_mp3(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/public_songs/<filename>')
def serve_public(filename):
    return send_from_directory(PUBLIC_FOLDER, filename)

@app.route('/play_song', methods=['POST'])
def play_song():
    username = session.get('username')
    if not username:
        return jsonify(message="No user logged in"), 403
    user = users_db.get(username)
    if not user:
        return jsonify(message="User not found"), 404
    data = request.get_json()
    filename = data.get('filename')
    is_public = data.get('is_public', False)
    if not filename:
        return jsonify(message="Filename required"), 400
    if is_public:
        song = PublicSong(os.path.splitext(filename)[0], "Various", 3.0)
    else:
        song = LocalSong(os.path.splitext(filename)[0], "Unknown Artist", 3.0)
    player = MusicPlayer()
    player.play_song(user, song)
    return jsonify(message="Song played")

@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    username = session.get('username')
    if not username:
        return jsonify(message="No user session found."), 403

    user = users_db.get(username)
    if not user:
        return jsonify(message="User not found."), 404

    data = request.get_json()
    name = data.get('name', '').strip()
    if not name:
        return jsonify(message="Missing playlist name."), 400

    user.playlists.append(Playlist(name))
    return jsonify(message="Playlist created."), 200

@app.route('/playlists')
def get_playlists():
    username = session.get('username')
    user = users_db.get(username)
    return jsonify(playlists=[pl.to_dict() for pl in user.playlists])

@app.route('/playlist/add_song', methods=['POST'])
def add_to_playlist():
    username = session.get('username')
    user = users_db.get(username)
    data = request.get_json()
    pl_name = data['playlist'].strip().lower()
    song_name = os.path.splitext(data['song'])[0]
    is_public = data.get('is_public', False)
    song = PublicSong(song_name, "Various", 3.0) if is_public else LocalSong(song_name, "Unknown Artist", 3.0)
    for pl in user.playlists:
        if pl.p_name.strip().lower() == pl_name:
            pl.add_song(song)
            return jsonify(message="Added to playlist"), 200
    return jsonify(message="Playlist not found"), 404

@app.route('/playlist/remove_song', methods=['POST'])
def remove_from_playlist():
    username = session.get('username')
    user = users_db.get(username)
    data = request.get_json()

    pl_name = data.get('playlist', '').strip().lower()
    song_name = data.get('song')
    is_public = data.get('is_public', False)

    if not song_name:
        return jsonify(message="Missing song filename"), 400

    for pl in user.playlists:
        if pl.p_name.strip().lower() == pl_name:
            for i, song in enumerate(pl.songs):
                # Match full filename
                if song.s_name == os.path.splitext(song_name)[0]:
                    pl.remove_song(i)
                    return jsonify(message="Song removed from playlist"), 200

    return jsonify(message="Playlist or song not found"), 404

@app.route('/playlist/update_title', methods=['POST'])
def update_title():
    username = session.get('username')
    user = users_db.get(username)
    data = request.get_json()
    old = data['old']
    new = data['new']
    for pl in user.playlists:
        if pl.p_name == old:
            pl.p_name = new
            return jsonify(message="Title updated")
    return jsonify(message="Playlist not found"), 404

@app.route('/playlist/update_description', methods=['POST'])
def update_description():
    username = session.get('username')
    user = users_db.get(username)
    data = request.get_json()
    name = data['name']
    desc = data['desc']
    for pl in user.playlists:
        if pl.p_name == name:
            pl.description = desc
            return jsonify(message="Description updated")
    return jsonify(message="Playlist not found"), 404

@app.route('/playlist/update_image', methods=['POST'])
def update_image():
    username = session.get('username')
    user = users_db.get(username)
    if 'image' not in request.files:
        return jsonify(message="No image uploaded"), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify(message="Empty filename"), 400
    playlist_name = request.form.get("playlist")
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.static_folder, filename))
    for pl in user.playlists:
        if pl.p_name == playlist_name:
            pl.picture_path = filename
            return jsonify(message="Image updated")
    return jsonify(message="Playlist not found"), 404

@app.route('/history')
def get_history():
    lines = HistoryLogger.read_history()
    table = "<table border='1'><tr><th>User</th><th>Song</th><th>Date</th></tr>"
    for line in lines:
        parts = line.strip().split(',')
        if len(parts) == 3:
            table += f"<tr><td>{parts[0]}</td><td>{parts[1]}</td><td>{parts[2]}</td></tr>"
    table += "</table>"
    return jsonify(history=[table])

@app.route('/clear_history', methods=['POST'])
def clear_history():
    HistoryLogger.clear_history()
    return jsonify(message="History cleared")

@app.route('/delete_account', methods=['POST'])
def delete_account():
    username = session.get('username')
    user = users_db.pop(username, None)
    if user:
        user.delete_profile()
        session.pop('username', None)
        return jsonify(message="Account deleted", redirect="/")
    return jsonify(message="User not found"), 404

if __name__ == '__main__':
    app.run(debug=True)
