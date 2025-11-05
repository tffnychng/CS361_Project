import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QStackedWidget,
                             QFileDialog, QTextEdit, QScrollArea, QListWidget, 
                             QListWidgetItem, QLineEdit, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont, QKeyEvent
import pygame
import shutil
from custom_classes import Song, Cassette
import json


LARGEFONT = QFont("Verdana", 30)

class CassetteApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cassette Archive")
        self.setFixedSize(400,500)
        storage = Storage()
        self.music_player = MusicPlayer(storage)
        print(self.music_player.songs)

        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #CBC9FD;
            }
            QPushButton {
                background-color: #FFDB78;
                border-radius: 10px;
                padding: 8px 16px;
                font-size: 14px;
                color: black;
            }
            QPushButton:hover {
                background-color: #DEBE64;
            }
            QPushButton:pressed {
                background-color: #DEBE64;
            }
            QLabel {
                font-size: 14px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        self.stk = QStackedWidget()
        main_layout.addWidget(self.stk)
        
        self.pages = {}
        self.pages['start'] = StartPage(self)
        self.pages['addsong'] = AddSong(self)
        self.pages['playsong'] = PlaySong(self)
        self.pages['songview'] = SongView(self)
        self.pages['help'] = HelpPage(self)
        
        for _, page in self.pages.items():
            self.stk.addWidget(page)
        
        self.show_page('start')
    
    def show_page(self, pgName):
        if pgName in self.pages:
            self.stk.setCurrentWidget(self.pages[pgName])

class StartPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        title_label = QLabel("Cassette Archive")
        title_label.setFont(LARGEFONT)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        image_label = QLabel()
        img = QPixmap("assets/welcome.png")
        if not img.isNull():
            img = img.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(img)
        else:
            image_label.setText("Image not found")
        image_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(image_label)
        description = QLabel("Keep all your audio files in one place, create customizable mixtapes, and listen offline anytime")
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignCenter)
        layout.addWidget(description)
        
        start_button = QPushButton("Get Started")
        start_button.setFixedSize(120, 40)
        start_button.clicked.connect(lambda: self.parent.show_page('songview'))
        layout.addWidget(start_button, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)

class AddSong(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
        self.file_path = None
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
      
        title_label = QLabel("Add a Song")
        title_label.setFont(LARGEFONT)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        nav_layout = QHBoxLayout()
        song_view = QPushButton("Song View")
        song_view.clicked.connect(lambda: self.parent.show_page('songview'))
        nav_layout.addWidget(song_view)
        
        addsong = QPushButton("Add a Song")
        addsong.clicked.connect(lambda: self.parent.show_page('addsong'))
        nav_layout.addWidget(addsong)
        
        help = QPushButton("Help")
        help.clicked.connect(lambda: self.parent.show_page('help'))
        nav_layout.addWidget(help)
        
        layout.addLayout(nav_layout)
        
        
        self.song_name = QTextEdit()
        self.song_name.setPlaceholderText("Song Name...")
        layout.addWidget(self.song_name)
        
        self.artist_name = QTextEdit()
        self.artist_name.setPlaceholderText("Artist Name...")
        layout.addWidget(self.artist_name)

        self.import_button = QPushButton("Import Audio File")
        self.import_button.clicked.connect(self.import_file)
        layout.addWidget(self.import_button)

        l2 = QHBoxLayout()

        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.cancel)
        l2.addWidget(cancel)
        layout.addLayout(l2)

        add_song = QPushButton("Confirm")
        add_song.clicked.connect(self.add_song)
        l2.addWidget(add_song)
        
        self.setLayout(layout)

    def import_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Audio File", 
            "", 
            "Audio Files (*.mp3 *.wav *.flac *.ogg);;All Files (*.*)"
        )
        if file_path:
            print("Selected file:", file_path)
            self.file_path = file_path
        self.import_button.setStyleSheet("background-color: #DEBE64;")

    def add_song(self):
        if self.file_path:
            source = self.file_path
            file_name = os.path.basename(source)
            dest_path = 'data/songs'
            os.makedirs(dest_path, exist_ok=True)
            try:
                shutil.copy(source, dest_path)
                print(f"File '{source}' successfully copied to '{dest_path}'")
                title = self.song_name.toPlainText()
                artist = self.artist_name.toPlainText()
                new_song = Song(f"data/songs/{file_name}", title, artist)
                self.parent.music_player.add_song(new_song)
                #move this into a seperate function later
                try:
                    with open("data/songs.json", "r") as file:
                        data = json.load(file)
                except FileNotFoundError:
                    data = [] 
                data.append(new_song.to_dict())
                with open("data/songs.json", "w") as file:
                    json.dump(data, file, indent=4)
                self.file_path = None
                self.song_name.clear()
                self.artist_name.clear()
            except FileNotFoundError:
                print(f"Error: Source file not found.")
            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            print("No file selected, please retry")
    def cancel(self):
        self.file_path = None
        self.song_name.clear()
        self.artist_name.clear()
        self.import_button.setStyleSheet("background-color: #FFDB78;")


class PlaySong(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.edit_mode = False
        self.init_ui()
        self.setFocusPolicy(Qt.StrongFocus) 
    
    def init_ui(self):
        layout = QVBoxLayout()

        nav_layout = QHBoxLayout()
        song_view = QPushButton("Song View")
        song_view.clicked.connect(lambda: self.parent.show_page('songview'))
        nav_layout.addWidget(song_view)
        
        addsong = QPushButton("Add a Song")
        addsong.clicked.connect(lambda: self.parent.show_page('addsong'))
        nav_layout.addWidget(addsong)
        
        help = QPushButton("Help")
        help.clicked.connect(lambda: self.parent.show_page('help'))
        nav_layout.addWidget(help)
        
        layout.addLayout(nav_layout)

        self.song_info = QLabel("No song loaded")
        self.song_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.song_info)
        
        self.edit_layout = QVBoxLayout()
        
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Song Title")
        self.edit_layout.addWidget(QLabel("Title:"))
        self.edit_layout.addWidget(self.title_edit)
        
        self.artist_edit = QLineEdit()
        self.artist_edit.setPlaceholderText("Artist")
        self.edit_layout.addWidget(QLabel("Artist:"))
        self.edit_layout.addWidget(self.artist_edit)
        
        self.album_edit = QLineEdit()
        self.album_edit.setPlaceholderText("Album")
        self.edit_layout.addWidget(QLabel("Album:"))
        self.edit_layout.addWidget(self.album_edit)
        
        self.edit_widget = QWidget()
        self.edit_widget.setLayout(self.edit_layout)
        self.edit_widget.hide()
        layout.addWidget(self.edit_widget)
        
        controls_layout = QHBoxLayout()
        self.play_button = QPushButton()
        self.play_button.setText("Play")
        self.play_button.clicked.connect(self.play_current_song)
        controls_layout.addWidget(self.play_button)
        layout.addLayout(controls_layout)
        
        layout.addLayout(controls_layout)
        
        update_layout = QHBoxLayout()
        
        self.delete_button = QPushButton("Delete Song")
        self.delete_button.clicked.connect(self.delete_song)
        update_layout.addWidget(self.delete_button)

        self.edit_button = QPushButton("Edit Details")
        self.edit_button.clicked.connect(self.toggle_edit_mode)
        update_layout.addWidget(self.edit_button)

        self.cancel_button = QPushButton("Cancel Changes")
        self.cancel_button.clicked.connect(self.cancel_changes)
        self.cancel_button.hide() 
        update_layout.addWidget(self.cancel_button)

        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_changes)
        self.save_button.hide() 
        update_layout.addWidget(self.save_button)
        
        layout.addLayout(update_layout)
        
        self.setLayout(layout)
        self.update_display()
    
    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        
        if self.edit_mode:
            self.edit_widget.show()
            self.cancel_button.show()
            self.save_button.show()
            self.edit_button.hide()
            self.delete_button.hide()
            
            if self.parent.music_player.current_song:
                song = self.parent.music_player.current_song
                self.title_edit.setText(song.title)
                self.artist_edit.setText(song.artist)
                self.album_edit.setText(song.album)
        else:
            self.edit_widget.hide()
            self.save_button.hide()
            self.edit_button.show()
        
        self.update_display()
    
    def save_changes(self):
        if self.parent.music_player.current_song:
            original_song = self.parent.music_player.current_song
            
            updated_song = Song(
                file_path=original_song.file_path,  
                title=self.title_edit.text().strip() or original_song.title,
                artist=self.artist_edit.text().strip() or original_song.artist,
                album=self.album_edit.text().strip() or original_song.album,
                genre=original_song.genre, 
                duration=original_song.duration  
            )

            self.parent.music_player.update_current_song(updated_song)

            self.toggle_edit_mode()
            self.update_display()
    def cancel_changes(self):
        self.toggle_edit_mode()
        self.cancel_button.hide()
        self.delete_button.show()
        self.edit_button.show()
        self.update_display()
    
    def delete_song(self):
        if self.parent.music_player.current_song:
            song = self.parent.music_player.current_song
            reply = QMessageBox.question(
                self, 'Confirm Delete',
                f"Are you sure you want to delete '{song.title}' by {song.artist}?\n\nThis will permanently remove the audio file from storage.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.parent.music_player.delete_current_song()
                self.parent.show_page('songview')

    def play_current_song(self):
        if self.parent.music_player.status == "paused" or self.parent.music_player.status == "stopped":
            self.play_button.setText("Pause")
            self.parent.music_player.play()
        elif self.parent.music_player.status == "playing":
            self.play_button.setText("Play")
            self.parent.music_player.pause()
        self.update_display()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            print("Spacebar pressed - toggling play/pause")
            self.play_current_song()
            event.accept()  
        else:
            super().keyPressEvent(event)
            
    def update_display(self):
        player = self.parent.music_player
        
        if player.current_song:
            song = player.current_song
            
            if self.edit_mode:
                self.song_info.setText("Editing Song")
            else:
                display_text = f"Title: {song.title}\nArtist: {song.artist}\nAlbum: {song.album}\nGenre: {song.genre}"
                self.song_info.setText(display_text)
        else:
            self.song_info.setText("No song loaded")
    
    def showEvent(self, event):
        super().showEvent(event)
        self.update_display()
   

class SongView(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        title_label = QLabel("Song Catalog")
        title_label.setFont(LARGEFONT)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        nav_layout = QHBoxLayout()
        song_view = QPushButton("Song View")
        song_view.clicked.connect(lambda: self.parent.show_page('songview'))
        nav_layout.addWidget(song_view)
        
        addsong = QPushButton("Add a Song")
        addsong.clicked.connect(lambda: self.parent.show_page('addsong'))
        nav_layout.addWidget(addsong)
        
        help = QPushButton("Help")
        help.clicked.connect(lambda: self.parent.show_page('help'))
        nav_layout.addWidget(help)
        
        layout.addLayout(nav_layout)
        self.song_list = QListWidget()
        layout.addWidget(self.song_list)
        self.setLayout(layout)
        self.refresh_list()

    def refresh_list(self):
        self.song_list.clear()
        for s in self.parent.music_player.songs:
            item = QListWidgetItem(f"{s.title} - {s.artist}")
            item.setData(Qt.UserRole, s)
            self.song_list.addItem(item)
        self.song_list.itemClicked.connect(self.on_item_clicked)

    def on_item_clicked(self, item):
        selected = item.data(Qt.UserRole)
        current = self.parent.music_player.current_song
        if (current and current.file_path == selected.file_path):
            self.parent.show_page('playsong')
        else:
            self.parent.music_player.load_song(selected)
            self.parent.show_page('playsong')
    
    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_list()

class HelpPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        title_label = QLabel("Help")
        title_label.setFont(LARGEFONT)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        nav_layout = QHBoxLayout()
        song_view = QPushButton("Song View")
        song_view.clicked.connect(lambda: self.parent.show_page('songview'))
        nav_layout.addWidget(song_view)
        
        addsong = QPushButton("Add a Song")
        addsong.clicked.connect(lambda: self.parent.show_page('addsong'))
        nav_layout.addWidget(addsong)
        
        help = QPushButton("Help")
        help.clicked.connect(lambda: self.parent.show_page('help'))
        nav_layout.addWidget(help)
        
        layout.addLayout(nav_layout)
        layout.addStretch(1)
        p1 = QLabel()
        p1.setText("Add a new song by navigating to the 'Add Song' page and uploading your file\n\n" \
                    "Tap on a song to view more info\n\n" \
                    "You can edit song data, play the song, or delete a song from the song view")
        p1.setAlignment(Qt.AlignCenter)
        p1.setWordWrap(True)
        layout.addWidget(p1)
        layout.addStretch(2)

        self.setLayout(layout)

class MusicPlayer:
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
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setFont(QFont("Verdana", 10))
    
    window = CassetteApp()
    window.show()
    
    sys.exit(app.exec_())
