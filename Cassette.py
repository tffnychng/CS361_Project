from dataclasses import dataclass
from typing import Optional
import os
from Song import Song

@dataclass
class Cassette:
    name: str
    songs: list[Song]  
    notes: dict[str, str] = None
    cover: str = "assets/placeholder_conver.png"
    
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
              'notes': self.notes,
              'cover_path': self.cover_path
          }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Song':
      return cls(
          name=data['name'],
          songs=data['songs'],
          notes=data['notes']
      )