import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QStackedWidget,
                             QFileDialog, QTextEdit, QScrollArea, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
import pygame
import shutil
from custom_classes import Song, Cassette
import json


LARGEFONT = QFont("Verdana", 24)

class CassetteApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cassette Archive")
        self.setFixedSize(400,500)
        self.music_player = MusicPlayer()
        self.load_songs()
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
                background-color: #FFF2D0;
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
        
        for _, page in self.pages.items():
            self.stk.addWidget(page)
        
        self.show_page('songview')
    
    def show_page(self, pgName):
        if pgName in self.pages:
            self.stk.setCurrentWidget(self.pages[pgName])
    def load_songs(self):
        filepath = "data/songs.json"
        loaded_songs = []
        try:
            with open(filepath, 'r') as f:
                loaded_songs = json.load(f)
        except FileNotFoundError:
            print("Missing data/songs.json")
        for dict in loaded_songs:
            song = Song.from_dict(dict)
            self.music_player.add_song(song)

    

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
        start_button.clicked.connect(lambda: self.parent.show_page('addsong'))
        layout.addWidget(start_button, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)

class AddSong(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
        self.file_path = None
    
    def init_ui(self):
        p1 = QVBoxLayout()
        p1.setSpacing(20)
      
        title_label = QLabel("Add a Song")
        title_label.setFont(LARGEFONT)
        title_label.setAlignment(Qt.AlignCenter)
        p1.addWidget(title_label)
        
        nav_layout = QHBoxLayout()
        
        start_button = QPushButton("Start Page")
        start_button.clicked.connect(lambda: self.parent.show_page('start'))
        nav_layout.addWidget(start_button)
        
        page2_button = QPushButton("See Songs")
        page2_button.clicked.connect(lambda: self.parent.show_page('songview'))
        nav_layout.addWidget(page2_button)
        
        p1.addLayout(nav_layout)
        
        
        self.song_name = QTextEdit()
        self.song_name.setPlaceholderText("Song Name...")
        p1.addWidget(self.song_name)
        
        self.artist_name = QTextEdit()
        self.artist_name.setPlaceholderText("Artist Name...")
        p1.addWidget(self.artist_name)

        import_button = QPushButton("Import Audio File")
        import_button.clicked.connect(self.import_file)
        p1.addWidget(import_button)

        add_song = QPushButton("Confirm")
        add_song.clicked.connect(self.add_song)
        p1.addWidget(add_song)
        
        self.setLayout(p1)

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

class PlaySong(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        title_label = QLabel("Play a Song")
        title_label.setFont(LARGEFONT)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        nav_layout = QHBoxLayout()
        
        start_button = QPushButton("See Songs")
        start_button.clicked.connect(lambda: self.parent.show_page('songview'))
        nav_layout.addWidget(start_button)
        
        page1_button = QPushButton("Add Song")
        page1_button.clicked.connect(lambda: self.parent.show_page('addsong'))
        nav_layout.addWidget(page1_button)
        
        layout.addLayout(nav_layout)
        play_view = QVBoxLayout()

        cover_art = QLabel()
        if self.parent.music_player.current_song:
            img = QPixmap(self.parent.music_player.current_song.cover)
            if not img.isNull():
                img = img.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                cover_art.setPixmap(img)
            else:
                cover_art.setText("Image not found")
        else:
            img = QPixmap("assets/placeholder_cover.png")
            img = img.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            cover_art.setPixmap(img)
        cover_art.setAlignment(Qt.AlignCenter)
        play_view.addWidget(cover_art, stretch=2)
        
        if self.parent.music_player.current_song:
            self.now_playing_label = QLabel(f"Playing: {self.parent.music_player.current_song.title}")
        else:
            self.now_playing_label = QLabel(f"No Song Selected")
        self.now_playing_label.setAlignment(Qt.AlignCenter)
        play_view.addWidget(self.now_playing_label)
        layout.addLayout(play_view)

        controls_layout = QHBoxLayout()
        play_button = QPushButton("Play")
        play_button.clicked.connect(self.play_current_song)
        controls_layout.addWidget(play_button)
        layout.addLayout(controls_layout)
        
        self.setLayout(layout)

    def play_current_song(self):
        if self.parent.music_player.status == "paused" or self.parent.music_player.status == "stopped":
            self.parent.music_player.play()
        elif self.parent.music_player.status == "playing":
            self.parent.music_player.pause()
   

class SongView(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        nav_layout = QHBoxLayout()
        song_view = QPushButton("Add a Song")
        song_view.clicked.connect(lambda: self.parent.show_page('addsong'))
        nav_layout.addWidget(song_view)
        
        mixtape_view = QPushButton("Start Page")
        mixtape_view.clicked.connect(lambda: self.parent.show_page('start'))
        nav_layout.addWidget(mixtape_view)
        
        layout.addLayout(nav_layout)



        self.song_list = QListWidget()

        for i, s in enumerate(self.parent.music_player.songs):
            item = QListWidgetItem(f"{s.title} - {s.artist}")
            item.setData(Qt.UserRole, s)
            self.song_list.addItem(item)
        self.song_list.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.song_list)

        self.setLayout(layout)

    def on_item_clicked(self, item):
        selected = item.data(Qt.UserRole)
        current = self.parent.music_player.current_song
        if not (current and current.file_path == selected.file_path):
            self.parent.music_player.load_song(selected)
            self.parent.show_page('playsong')


class MusicPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.current_song = None
        self.status = "stopped"
        self.songs = []  
    
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
    
    def add_song(self, song: Song):
        self.songs.append(song)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setFont(QFont("Verdana", 10))
    
    window = CassetteApp()
    window.show()
    
    sys.exit(app.exec_())
