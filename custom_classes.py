from dataclasses import dataclass
from typing import Optional
import os
from datetime import datetime

@dataclass
class Song:
    file_path: str
    title: str
    artist: str
    album: str = "Unknown Album"
    genre: str = "Unknown Genre"
    duration: float = 0.0  
    
    def __post_init__(self):
        if not self.title:
            self.title = os.path.basename(self.file_path)
        if not self.artist:
            self.artist = "Unknown Artist"
    
    def to_dict(self) -> dict:
          return {
              'file_path': self.file_path,
              'title': self.title,
              'artist': self.artist,
              'album': self.album,
              'genre': self.genre,
              'duration': self.duration
          }
    def from_dict(cls, data: dict) -> 'Song':
      return cls(
          file_path=data['file_path'],
          title=data['title'],
          artist=data['artist'],
          album=data['album'],
          genre=data['genre'],
          duration=data['duration']
      )
    
    

@dataclass
class Cassette:
    name: str
    songs: list[Song]  
    notes: dict[str, str] = None
    
    def __post_init__(self):
      if self.notes is None:
          self.notes = {}

    def add_song(self, song: Song, note: str = ""):
        if song not in self.songs:
            self.songs.append(song)
            if note:
                self.notes[song.file_path] = note
    
    def remove_song(self, song: Song):
        if song in self.songs:
            self.songs.remove(song)
            self.notes.pop(song.file_path, None)
    
    def get_note(self, song: Song) -> str:
        return self.notes.get(song.file_path, "")
    
    def set_note(self, song: Song, note: str):
        self.notes[song.file_path] = note
    
    def total_duration(self):
        return sum(song.duration for song in self.songs)
    
    def to_dict(self) -> dict:
          return {
              'name': self.name,
              'songs': self.songs,
              'notes': self.notes
          }
    
    def from_dict(cls, data: dict) -> 'Song':
      return cls(
          name=data['name'],
          songs=data['songs'],
          notes=data['notes']
      )