# music_organizer.py

import datetime
from abc import ABC, abstractmethod
from typing import List

# --- Singleton ---
class SingletonMP(type):
    _instances = {}

    def __call__(cls):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__()
        return cls._instances[cls]

# --- Song ---
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

# --- Library ---
class Library:
    def __init__(self, l_name: str):
        self.l_name = l_name
        self.songs: List[Song] = []

    def add_song(self, song: Song):
        if not any(s.s_name == song.s_name and s.artist == song.artist for s in self.songs):
            self.songs.append(song)

class PublicLibrary(Library):
    pass

class PrivateLibrary(Library):
    def load_sample_songs(self):
        sample_files = [
            ("Apocalypse", "Cigarettes After Sex", 4.5),
            ("Local Track 2", "Local Artist B", 3.5),
        ]
        for name, artist, duration in sample_files:
            song = LocalSong(name, artist, duration)
            self.add_song(song)

# --- Encapsulation, composition ---
class User:
    def __init__(self, u_name: str, gmail: str, password: str, photo_path: str = "default_profile.png"):
        self.__u_name = u_name
        self.__gmail = gmail
        self.__password = password
        self.__photo_path = photo_path
        self.private_library = PrivateLibrary(f"{self.__u_name}'s Library")
        self.playlists: List[Playlist] = []

    def delete_profile(self):
        del self.private_library
        self.playlists.clear()
        print(f"User {self.__u_name}'s data has been deleted.")

    @property
    def name(self):
        return self.__u_name

# --- Aggregation ---
class Playlist:
    def __init__(self, p_name: str, picture_path: str = "default_picture.png", description: str = ""):
        self.p_name = p_name
        self.picture_path = picture_path
        self.description = description
        self.songs: List[Song] = []

    def add_song(self, song: Song):
        self.songs.append(song)

    def remove_song(self, index: int):
        if 0 <= index < len(self.songs):
            del self.songs[index]

# --- File R/W ---
class HistoryLogger:
    file_path = "Recently_Played.txt"

    @staticmethod
    def log_song(user_name: str, song: Song):
        date_played = datetime.date.today().isoformat()
        with open(HistoryLogger.file_path, 'a') as file:
            file.write(f"| User: {user_name} | Song: {song.s_name} | Artist: {song.artist} | Date: {date_played} |\n")

    @staticmethod
    def read_history():
        try:
            with open(HistoryLogger.file_path, 'r') as file:
                for line in file:
                    print(line.strip())
        except FileNotFoundError:
            print("No history found.")

# --- Music Player ---
class MusicPlayer(metaclass=SingletonMP):
    def __init__(self):
        self.volume = 50
        self.is_playing = False
        self.queue: List[Song] = []
        self.current_song = None

    def add_to_queue(self, song: Song):
        self.queue.append(song)

    def play_next(self, user: User):
        if self.queue:
            self.current_song = self.queue.pop(0)
            self.current_song.play()
            HistoryLogger.log_song(user.name, self.current_song)
            self.is_playing = True

    def play_song(self, user: User, song: Song):
        self.current_song = song
        song.play()
        HistoryLogger.log_song(user.name, song)
        self.is_playing = True

    def pause(self):
        if self.is_playing:
            print("Paused")
            self.is_playing = False

    def resume(self):
        if not self.is_playing and self.current_song:
            print("Resumed")
            self.is_playing = True

    def loop(self):
        if self.current_song:
            self.current_song.play()

    def set_volume(self, level: int):
        self.volume = max(0, min(level, 100))
        print(f"Volume set to {self.volume}")

public_library = PublicLibrary("Global Library")

public_library.add_song(PublicSong("Song A", "Artist X", 3.5))
public_library.add_song(PublicSong("Song B", "Artist Y", 4.0))

user = User("john_doe", "john@gmail.com", "securepassword")
user.private_library.load_sample_songs()

playlist = Playlist("My Favorites")
playlist.add_song(public_library.songs[0])
playlist.add_song(user.private_library.songs[0])
user.playlists.append(playlist)

player = MusicPlayer()
for song in playlist.songs:
    player.add_to_queue(song)

player.play_next(user)
player.pause()
player.resume()
player.play_next(user)

HistoryLogger.read_history()
