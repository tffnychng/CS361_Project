import os
from Song import Song
import json

class Storage():
    def __init__(self):
      self.songs_file = "data/songs.json"
      os.makedirs("data", exist_ok=True)

    def load_songs(self):
      loaded_songs = []
      try:
          with open(self.songs_file, 'r') as f:
              loaded_songs = json.load(f)
      except FileNotFoundError:
          print("Missing data/songs.json")
      return [Song.from_dict(song) for song in loaded_songs]

    def save_songs(self, songs):
      songs_to_json = [song.to_dict() for song in songs]
      with open(self.songs_file, 'w') as f:
          json.dump(songs_to_json, f, indent=4)
    
    def add_song(self, song):
      try:
        with open(self.songs_file, "r") as file:
          song_list = json.load(file)
      except FileNotFoundError:
        song_list  = [] 
      song_list.append(song.to_dict())
      with open(self.songs_file, "w") as f:
        json.dump(song_list, f, indent=4)

    def delete_song(self, deleted_song, songs):
        updated_songs = [s for s in songs if s.file_path != deleted_song.file_path]
        self.save_songs(updated_songs)
        try:
            if os.path.exists(deleted_song.file_path):
                os.remove(deleted_song.file_path)
        except Exception as e:
            print(f"Warning: Could not delete audio file: {e}")
        return updated_songs
    
    def update_song(self, og_song, updated_song, songs):
        updated_songs = []
        for song in songs:
            if song.file_path == og_song.file_path:
                updated_songs.append(updated_song)
            else:
                updated_songs.append(song)
        self.save_songs(updated_songs)
        return updated_songs
    