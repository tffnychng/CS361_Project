from dataclasses import dataclass
import os
from typing import Optional

@dataclass
class Song:
    file_path: str
    title: str
    artist: str
    album: str = "Unknown Album"
    genre: str = "Unknown Genre"
    duration: float = 0.0  
    cover_url: Optional[str] = None
    cover_path: str = "assets/placeholder_cover.png"
    
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
              'duration': self.duration,
              'cover_url': self.cover_url,
              'cover_path': self.cover_path
          }
    @classmethod
    def from_dict(cls, data: dict) -> 'Song':
      return cls(
          file_path=data['file_path'],
          title=data['title'],
          artist=data['artist'],
          album=data['album'],
          genre=data['genre'],
          duration=data['duration'],
          cover_url=data.get('cover_url', None),
          cover_path=data.get('cover_path', 'assets/placeholder_cover.png')
      )
    
    @classmethod
    def from_microservice_data(cls, file_path: str, microservice_data: dict) -> 'Song':
        return cls(
            file_path=file_path,
            title=microservice_data.get("name", "Unknown Title"),
            artist=microservice_data.get("artist", "Unknown Artist"),
            album=microservice_data.get("album", "Unknown Album"),
            genre=", ".join(microservice_data.get("genres", ["Unknown Genre"])),
            cover_url=microservice_data.get("image")
        )