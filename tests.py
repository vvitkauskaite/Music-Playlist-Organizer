import unittest
from backend.app import Playlist, LocalSong, PublicSong, User, HistoryLogger, MusicPlayer

class TestPlaylist(unittest.TestCase):
    def test_add_song(self):
        playlist = Playlist("Test Playlist")
        song = LocalSong("Song 1", "Artist 1", 3.0)
        playlist.add_song(song)
        self.assertEqual(len(playlist.songs), 1)
        self.assertEqual(playlist.songs[0].s_name, "Song 1")

    def test_remove_song(self):
        playlist = Playlist("Test Playlist")
        song = LocalSong("Song to Remove", "Artist 2", 3.0)
        playlist.add_song(song)
        playlist.remove_song(0)
        self.assertEqual(len(playlist.songs), 0)

class TestUser(unittest.TestCase):
    def test_user_creation(self):
        user = User("vaidile", "test@example.com", "12345")
        self.assertEqual(user.name, "vaidile")
        self.assertTrue(user.private_library)
        self.assertIsInstance(user.playlists, list)

class TestSongPolymorphism(unittest.TestCase):
    def test_public_song_play(self):
        song = PublicSong("Public Track", "Various", 3.0)
        self.assertEqual(song.s_name, "Public Track")
        self.assertEqual(song.artist, "Various")

    def test_local_song_play(self):
        song = LocalSong("Local Track", "Unknown", 3.0)
        self.assertEqual(song.s_name, "Local Track")
        self.assertEqual(song.artist, "Unknown")

class TestHistoryLogger(unittest.TestCase):
    def test_log_and_read_history(self):
        song = LocalSong("History Song", "Tester", 3.0)
        HistoryLogger.log_song("test_user", song)
        lines = HistoryLogger.read_history()
        self.assertTrue(any("History Song" in line for line in lines))

class TestMusicPlayerSingleton(unittest.TestCase):
    def test_singleton_instance(self):
        player1 = MusicPlayer()
        player2 = MusicPlayer()
        self.assertIs(player1, player2)

if __name__ == "__main__":
    unittest.main()
