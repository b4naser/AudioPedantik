# -*- coding: utf-8 -*-

#FIXME If there is no itunes data filename_edit = actual filename
#FIXME Defocusing search phrase edit set all itunes tags to ""
#FIXME nie zmienia się filename_edit
#FIXME Odklikiwanie overwrite'a

import os
import json
import shutil
import configparser
from urllib.request import urlopen
from urllib.parse import urlencode
from PyQt5.QtWidgets import \
    QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QListWidget, QComboBox, QGroupBox, QPushButton, QFileDialog, QCheckBox
from PyQt5.QtGui import QIcon, QPixmap, QImage
from mutagen import File
from mutagen.id3 import ID3, PictureType, APIC, TPE1, TIT2, TCON, TALB, TYER, TRCK
from mutagen.id3 import _util

class AudioPedantik(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.title = "AudioPedantik"
        self.top = 100
        self.left = 100
        self.width = 700
        self.height = 500

        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

        self.search_dir = ""
        self.dest_dir = ""

        self.audio_id3 = None
        self.results = []
        self.artwork_bytes = None

        self.init_ui()

    def init_ui(self):
        # Main widgets declaration
        search_dir_button = QPushButton("Select search directory")

        dest_dir_button = QPushButton("Select destination directory")

        self.search_dir_edit = QLineEdit()
        self.search_dir_edit.setText(self.config["Last"]["search_dir"])
        self.search_dir = self.config["Last"]["search_dir"]
        self.search_dir_edit.setReadOnly(True)

        self.dest_dir_edit = QLineEdit()
        self.dest_dir_edit.setText(self.config["Last"]["dest_dir"])
        self.dest_dir = self.config["Last"]["dest_dir"]
        self.dest_dir_edit.setReadOnly(True)

        self.listbox = QListWidget()
        self.listbox.setMaximumWidth(250)

        self.combobox = QComboBox()

        # ID3 group widgets declarations
        file_name_label = QLabel("File name: ")

        self.artwork_id3_label = QLabel()
        self.artwork_id3_label.setPixmap(QPixmap("default.jpg"))

        artist_id3_label = QLabel("Artist: ")
        title_id3_label = QLabel("Title: ")
        genre_id3_label = QLabel("Genre: ")
        album_id3_label = QLabel("Album: ")
        release_year_id3_label = QLabel("Release year: ")
        track_no_id3_label = QLabel("Track number: ")

        self.file_name_edit = QLineEdit()

        self.artist_id3_edit = QLineEdit()
        self.artist_id3_edit.setReadOnly(True)

        self.title_id3_edit = QLineEdit()
        self.title_id3_edit.setReadOnly(True)

        self.genre_id3_edit = QLineEdit()
        self.genre_id3_edit.setReadOnly(True)

        self.album_id3_edit = QLineEdit()
        self.album_id3_edit.setReadOnly(True)

        self.release_year_id3_edit = QLineEdit()
        self.release_year_id3_edit.setReadOnly(True)

        self.track_no_id3_edit = QLineEdit()
        self.track_no_id3_edit.setReadOnly(True)

        # iTunes group widgets declarations
        search_phrase_label = QLabel("Search phrase: ")

        self.checkbox = QCheckBox("Don't overwrite artwork")

        self.artwork_itunes_label = QLabel()
        self.artwork_itunes_label.setPixmap(QPixmap("default.jpg"))

        artist_itunes_label = QLabel("Artist: ")
        title_itunes_label = QLabel("Title: ")
        genre_itunes_label = QLabel("Genre: ")
        genre_itunes_label = QLabel("Genre: ")
        album_itunes_label = QLabel("Album: ")
        release_year_itunes_label = QLabel("Release year: ")
        track_no_itunes_label = QLabel("Track number: ")

        self.search_phrase_edit = QLineEdit()
        self.artist_itunes_edit = QLineEdit()
        self.title_itunes_edit = QLineEdit()
        self.genre_itunes_edit = QLineEdit()
        self.album_itunes_edit = QLineEdit()
        self.release_year_itunes_edit = QLineEdit()
        self.track_no_itunes_edit = QLineEdit()

        load_artwork_button = QPushButton("Load custom artwork")

        self.save_button = QPushButton("Save")
        self.save_button.setMaximumWidth(50)
        self.save_button.setDisabled(True)

        # Layout
        main_layout = QGridLayout()

        main_layout.addWidget(search_dir_button, 0, 0)
        main_layout.addWidget(dest_dir_button, 1, 0)
        main_layout.addWidget(self.search_dir_edit , 0, 1)
        main_layout.addWidget(self.dest_dir_edit, 1, 1)
        main_layout.addWidget(self.listbox, 2, 0, 3, 1)
        main_layout.addWidget(self.combobox, 2, 1)

        # Group box for mp3 data
        id3_data_group_box = QGroupBox("MP3 data: ")
        id3_data_group_layout = QGridLayout()

        id3_data_group_layout.addWidget(file_name_label, 0, 0)

        id3_data_group_layout.addWidget(self.artwork_id3_label, 1, 0, 5, 1)


        id3_data_group_layout.addWidget(artist_id3_label, 1, 2)
        id3_data_group_layout.addWidget(title_id3_label, 2, 2)
        id3_data_group_layout.addWidget(genre_id3_label, 3, 2)
        id3_data_group_layout.addWidget(album_id3_label, 4, 2)
        id3_data_group_layout.addWidget(release_year_id3_label, 5, 2)
        id3_data_group_layout.addWidget(track_no_id3_label, 6, 2)

        id3_data_group_layout.addWidget(self.file_name_edit, 0, 2, 1, 2)

        id3_data_group_layout.addWidget(self.artist_id3_edit, 1, 3)
        id3_data_group_layout.addWidget(self.title_id3_edit, 2, 3)
        id3_data_group_layout.addWidget(self.genre_id3_edit, 3, 3)
        id3_data_group_layout.addWidget(self.album_id3_edit, 4, 3)
        id3_data_group_layout.addWidget(self.release_year_id3_edit, 5, 3)
        id3_data_group_layout.addWidget(self.track_no_id3_edit, 6, 3)

        id3_data_group_box.setLayout(id3_data_group_layout)

        main_layout.addWidget(id3_data_group_box, 3, 1)

        # Group box for iTunes data
        itunes_data_group_box = QGroupBox("iTunes data: ")
        itunes_data_group_layout = QGridLayout()

        itunes_data_group_layout.addWidget(search_phrase_label, 0, 0)

        itunes_data_group_layout.addWidget(self.artwork_itunes_label, 1, 0, 5, 1)
        itunes_data_group_layout.addWidget(self.checkbox, 6, 0)

        itunes_data_group_layout.addWidget(artist_itunes_label, 1, 2)
        itunes_data_group_layout.addWidget(title_itunes_label, 2, 2)
        itunes_data_group_layout.addWidget(genre_itunes_label, 3, 2)
        itunes_data_group_layout.addWidget(album_itunes_label, 4, 2)
        itunes_data_group_layout.addWidget(release_year_itunes_label, 5, 2)
        itunes_data_group_layout.addWidget(track_no_itunes_label, 6, 2)
        itunes_data_group_layout.addWidget(track_no_itunes_label, 6, 2)

        itunes_data_group_layout.addWidget(self.search_phrase_edit, 0, 2, 1, 2)

        itunes_data_group_layout.addWidget(self.artist_itunes_edit, 1, 3)
        itunes_data_group_layout.addWidget(self.title_itunes_edit, 2, 3)
        itunes_data_group_layout.addWidget(self.genre_itunes_edit, 3, 3)
        itunes_data_group_layout.addWidget(self.album_itunes_edit, 4, 3)
        itunes_data_group_layout.addWidget(self.release_year_itunes_edit, 5, 3)
        itunes_data_group_layout.addWidget(self.track_no_itunes_edit, 6, 3)

        itunes_data_group_layout.addWidget(load_artwork_button, 7, 0)
        itunes_data_group_layout.addWidget(self.save_button, 7, 3)

        itunes_data_group_box.setLayout(itunes_data_group_layout)

        main_layout.addWidget(itunes_data_group_box, 4, 1)

        self.setLayout(main_layout)

        # Bindings
        dest_dir_button.pressed.connect(self.choose_dest_dir)
        search_dir_button.pressed.connect(self.choose_search_dir)
        load_artwork_button.pressed.connect(self.load_custom_artwork)
        self.save_button.pressed.connect(self.save)
        self.search_phrase_edit.editingFinished.connect(self.search_itunes)
        self.combobox.currentIndexChanged.connect(self.combobox_selected)

        # Window settings
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.setWindowTitle(self.title)
        self.show()

        self.refresh_listbox()
        self.save_button.setDisabled(False)

    def refresh_listbox(self):

        self.listbox.disconnect()
        self.listbox.clear()
        try:
            self.listbox.addItems([file for file in os.listdir(self.search_dir) if file.endswith(".mp3")])
        except FileNotFoundError:
            # FIXME:
            pass

        self.listbox.currentItemChanged.connect(self.listbox_selected)

    def choose_search_dir(self):

        self.search_dir = QFileDialog.getExistingDirectory(self, "Select Search Directory")
        self.search_dir_edit.setText(self.search_dir)
        self.config["Last"]["search_dir"] = self.search_dir

        with open("config.ini", "w") as configfile:
            self.config.write(configfile)

        self.refresh_listbox()

    def choose_dest_dir(self):

        self.dest_dir = QFileDialog.getExistingDirectory(self, "Select destination directory")
        self.dest_dir_edit.setText(self.dest_dir)
        self.config["Last"]["dest_dir"] = self.dest_dir

        with open("config.ini", "w") as configfile:
            self.config.write(configfile)

        self.save_button.setDisabled(False)

    def listbox_selected(self):

        file_name = self.listbox.currentItem().text()

        self.search_phrase_edit.setText(file_name[:-4])
        self.file_name_edit.setText(file_name)

        self.get_id3_tags(file_name)
        self.search_itunes()

    def get_id3_tags(self, file_name):
        try:
            self.audio_id3 = ID3(self.search_dir + "/" + file_name, v2_version=3)
        except _util.ID3NoHeaderError:
            file = File(self.search_dir + "/" + file_name)
            file.add_tags()
            file.save()

            self.audio_id3 = ID3(self.search_dir + "/" + file_name, v2_version=3)

        for tag in self.audio_id3:
            if tag.startswith("APIC") and (PictureType.COVER_FRONT == 3):
                image = QImage()
                image.loadFromData(self.audio_id3[tag].data)
                self.artwork_id3_label.setPixmap(QPixmap(image).scaled(150, 150))
                break

        else:
            #TODO: default image should be stored as raw data
            self.artwork_id3_label.setPixmap(QPixmap("default.jpg"))

        if "TPE1" in self.audio_id3:
            self.artist_id3_edit.setText(str(self.audio_id3["TPE1"]))
        else:
            self.artist_id3_edit.clear()

        if "TIT2" in self.audio_id3:
            self.title_id3_edit.setText(str(self.audio_id3["TIT2"]))
        else:
            self.title_id3_edit.clear()

        if "TCON" in self.audio_id3:
            self.genre_id3_edit.setText(str(self.audio_id3["TCON"]))
        else:
            self.genre_id3_edit.clear()

        if "TALB" in self.audio_id3:
            self.album_id3_edit.setText(str(self.audio_id3["TALB"]))
        else:
            self.album_id3_edit.clear()

        if "TYER" in self.audio_id3:
            self.release_year_id3_edit.setText(str(self.audio_id3["TYER"]))
        else:
            self.release_year_id3_edit.clear()

        if "TRCK" in self.audio_id3:
            self.track_no_id3_edit.setText(str(self.audio_id3["TRCK"]))
        else:
            self.track_no_id3_edit.clear()

    def search_itunes(self):

        params = {
                "term": self.search_phrase_edit.text(),
                "media": "music",
                "limit": 10
            }

        json_data = json.loads(urlopen("https://itunes.apple.com/search?" + urlencode(params)).read().decode('utf8'))


        self.combobox.clear()
        self.combobox.disconnect()

        self.results = []

        for result in json_data["results"]:
            # Prepare icon
            image_data = urlopen(result["artworkUrl30"]).read()
            image = QPixmap()
            image.loadFromData(image_data)

            self.combobox.addItem(QIcon(image), result["artistName"] + " - " + result["trackName"])
            self.results.append(result)

        self.combobox.currentIndexChanged.connect(self.combobox_selected)

        if len(self.results) > 0:
            self.combobox.setCurrentIndex(0)
            self.combobox_selected()
        else:
            self.artwork_itunes_label.setPixmap(QPixmap("default.jpg"))
            self.artwork_bytes = None

            self.artist_itunes_edit.clear()
            self.title_itunes_edit.clear()
            self.genre_itunes_edit.clear()
            self.album_itunes_edit.clear()
            self.release_year_itunes_edit.clear()

    def combobox_selected(self):

        current_combobox_index = self.combobox.currentIndex()

        artwork_url = self.results[current_combobox_index]["artworkUrl30"].split("/")
        artwork_url[-1] = "600x600bb.jpg"
        artwork_url = "/".join(artwork_url)

        self.artwork_bytes = urlopen(artwork_url).read()
        artwork = QPixmap()
        artwork.loadFromData(self.artwork_bytes)

        self.artwork_itunes_label.setPixmap(artwork.scaled(150, 150))

        self.artist_itunes_edit.setText(self.results[current_combobox_index]["artistName"])
        self.title_itunes_edit.setText(self.results[current_combobox_index]["trackName"])
        self.genre_itunes_edit.setText(self.results[current_combobox_index]["primaryGenreName"])

        if "collectionName" in self.results[current_combobox_index]:
            self.album_itunes_edit.setText(self.results[current_combobox_index]["collectionName"])

        self.release_year_itunes_edit.setText(self.results[current_combobox_index]["releaseDate"][:4])

        if "trackNumber" in self.results[current_combobox_index]:
            self.track_no_itunes_edit.setText(str(self.results[current_combobox_index]["trackNumber"]))

        self.file_name_edit.setText(self.results[current_combobox_index]["artistName"] + " - " + self.results[current_combobox_index]["trackName"] + ".mp3")

    def load_custom_artwork(self):
        image_file_name, _ = QFileDialog.getOpenFileName(self, "Select Artwork File", None, "Images (*.png *.jpg)")

        with open(image_file_name, 'rb') as f:
            self.artwork_bytes = f.read()

            artwork = QPixmap()
            artwork.loadFromData(self.artwork_bytes)

        self.artwork_itunes_label.setPixmap(artwork.scaled(150, 150))

    def save(self):
        audio_path = self.search_dir + "/" + self.listbox.currentItem().text()
        audio_save_path = self.dest_dir + "/" + self.file_name_edit.text()

        if not self.artwork_bytes == None:
            if not self.checkbox.isChecked():
                found = 0
                for tag in self.audio_id3:
                    if tag.startswith("APIC") and (PictureType.COVER_FRONT == 3):
                        self.audio_id3[tag].data = self.artwork_bytes
                        break

                if not found:
                    self.audio_id3.add(APIC(encoding=3, mime='image/jpeg', type=3, data=self.artwork_bytes))

        self.audio_id3.add(TPE1(encoding=3, text=self.artist_itunes_edit.text()))
        self.audio_id3.add(TIT2(encoding=3, text=self.title_itunes_edit.text()))
        self.audio_id3.add(TCON(encoding=3, text=self.genre_itunes_edit.text()))
        self.audio_id3.add(TALB(encoding=3, text=self.album_itunes_edit.text()))
        self.audio_id3.add(TYER(encoding=3, text=self.release_year_itunes_edit.text()))
        self.audio_id3.add(TRCK(encoding=3, text=self.track_no_itunes_edit.text()))

        self.audio_id3.save(v2_version=3)

        shutil.move(audio_path, audio_save_path)

        self.refresh_listbox()
        self.listbox.setCurrentRow(0)

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    okno = AudioPedantik()
    sys.exit(app.exec_())
