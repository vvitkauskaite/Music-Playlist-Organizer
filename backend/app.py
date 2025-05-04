from flask import Flask
from abc import ABC, abstractmethod
from typing import List
import os
import datetime

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)
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

if __name__ == '__main__':
    from route import *
    app.run(debug=True)

    