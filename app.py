import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QStackedWidget,
                             QFileDialog, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
import shutil
from custom_classes import Song, Cassette
import json


LARGEFONT = QFont("Verdana", 24)
songs = []

class CassetteApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cassette Archive")
        self.setGeometry(100, 100, 400, 500)
        
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
                color: #333333;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        self.stk = QStackedWidget()
        main_layout.addWidget(self.stk)
        
        self.pages = {}
        self.pages['start'] = StartPage(self)
        self.pages['page1'] = Page1(self)
        self.pages['page2'] = Page2(self)
        
        for _, page in self.pages.items():
            self.stk.addWidget(page)
        
        self.show_page('page1')
    
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
        
        start_button = QPushButton("Get Started")
        start_button.setFixedSize(120, 40)
        start_button.clicked.connect(lambda: self.parent.show_page('page1'))
        layout.addWidget(start_button, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)

class Page1(QWidget):
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
        
        page2_button = QPushButton("Play a Song")
        page2_button.clicked.connect(lambda: self.parent.show_page('page2'))
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
    
    def update_song_list(self):
        pass

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
                new_song = Song(f"songs/{file_name}", title, artist)
                songs.append(new_song)
                print(songs)
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
        

    


class Page2(QWidget):
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
    
        
        self.setLayout(layout)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setFont(QFont("Verdana", 10))
    
    window = CassetteApp()
    window.show()
    
    sys.exit(app.exec_())