from Storage import Storage
import pygame
from Song import Song

class MusicPlayer():
    def __init__(self, storage):
        pygame.mixer.init()
        self.current_song = None
        self.status = "stopped"
        self.storage = storage
        self.songs = storage.load_songs()
    
    def load_song(self, song: Song):
        try:
            pygame.mixer.music.load(song.file_path)
            self.current_song = song
            self.status = "stopped"
            print(f"Loaded: {song.file_path}")
            return True
        except Exception as e:
            print(f"Error loading song: {e}")
            return False
    
    def play(self):
        if not self.current_song:
            print("No song loaded")
            return
        if self.status == "stopped":
            pygame.mixer.music.play()
            self.status = "playing"
            print(f"Started: {self.current_song.title}")
        if self.status == "paused":
            pygame.mixer.music.unpause()
            self.status = "playing"
            print(f"Resumed: {self.current_song.title}")
    
    def pause(self):
        if self.status == "playing":
            pygame.mixer.music.pause()
            self.status = "paused"
            print(f"Paused: {self.current_song.title}")
    
    def stop(self):
        pygame.mixer.music.stop()
        self.player_state = "stopped"
    
    def add_song(self, song: Song):
        self.songs.append(song)

    def delete_current_song(self):
        if self.current_song:
            self.songs = self.storage.delete_song(self.current_song, self.songs)
            if self.current_song.file_path not in [s.file_path for s in self.songs]:
                self.stop()
                self.current_song = None
    
    def update_current_song(self, updated_song: Song):
        if self.current_song:
            original_song = self.current_song
            self.songs = self.storage.update_song(original_song, updated_song, self.songs)
            self.current_song = updated_song