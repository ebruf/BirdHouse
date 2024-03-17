import sys
import sqlite3
import random
#import keras
from tensorflow.keras.preprocessing.image import img_to_array, load_img
import numpy as np
from keras.models import load_model
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QDesktopWidget, QFileDialog, QSpacerItem, QSizePolicy, QHBoxLayout, QScrollArea
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5 import QtCore

# card widgets are added to the scroll box in my garden each
# time the user uploads a photo with information about the bird
class CardWidget(QWidget):
    def __init__(self, icon, species, description, quantity):
        super().__init__()

        layout = QHBoxLayout()

        # Icons show a cartoon representation of a bird
        iconLabel = QLabel()
        iconLabel.setPixmap(icon.pixmap(64, 64))
        layout.addWidget(iconLabel)

        # Describes the layout for the card
        cardFormat = QVBoxLayout()

        # instantiates each element of card
        speciesLabel = QLabel(species)
        descriptionLabel = QLabel(description)
        quantityLabel = QLabel(f"Quantity: {quantity}")

        cardFormat.addWidget(speciesLabel)
        cardFormat.addWidget(descriptionLabel)
        cardFormat.addWidget(quantityLabel)

        layout.addLayout(cardFormat)
        self.setLayout(layout)

# my garden window displays cards displaying info about birds from the database
class MyGarden(QMainWindow):
    def __init__(self):
        super().__init__()
        # sets colour to a pastel green
        self.setStyleSheet("background-color: #77dd77;")

        # Scroll box in the centre of the window is set up
        self.centralWid = QWidget()
        self.setCentralWidget(self.centralWid)

        self.layout = QVBoxLayout()
        self.centralWid.setLayout(self.layout)

        # My Garden label is set up at the top of the scroll box
        self.label = QLabel("My Garden")
        self.layout.addWidget(self.label)
        myGardenLabel = QFont("Marker Felt", 35)
        self.label.setFont(myGardenLabel)

        # Add scroll area
        self.scrollBox = QScrollArea()
        self.scrollBox.setWidgetResizable(True)
        self.scrollContent = QWidget()
        self.scrollBoxLayout = QVBoxLayout()
        self.scrollContent.setLayout(self.scrollBoxLayout)
        self.scrollBox.setWidget(self.scrollContent)
        self.layout.addWidget(self.scrollBox)

        # fills cards from database

        self.fillScrollBoxFromDB()

    # creates a new card to add to the scroll area with the right info about a bird
    def addCardToScrollBox(self, Name, Picture, Description, Quantity):

        icon = QIcon(Picture)
        name = Name
        description = Description
        quantity = Quantity

        card = CardWidget(icon, name, description, quantity)
        self.scrollBoxLayout.addWidget(card)

    # Reads all the birds from the database and creates a card in the scroll box to display them to the user
    def fillScrollBoxFromDB(self):

        self.connection = sqlite3.connect('BirdData_database.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute("SELECT name FROM birds")

        # selects just the species name from the rows
        species = [row[0] for row in self.cursor.fetchall()]

        # loop through all birds fetched and create cards

        listOfBirdPics = ["bird1.png","bird2.png","bird3.png"]
        for specie in species:
            random_number = random.randint(0, 2)
            self.addCardToScrollBox(specie,listOfBirdPics[random_number],"tbc",1)


# This is the window opened when the user first opens the application
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # classfied label starts as empty as there has been no bird uploaded yet
        # it is instantiated here so it can be modified on picture upload
        self.classifiedLabel = QLabel("", self)

        screen_geometry = QApplication.desktop().screenGeometry()
        width = screen_geometry.width()
        height = screen_geometry.height()
        self.setGeometry(0, 0, width, height)

        # set the backgound images with trees and flowers as a border
        background_label = QLabel(self)
        background_pixmap = QPixmap("BackgroundImage.png")
        background_pixmap = background_pixmap.scaled(width, height, QtCore.Qt.KeepAspectRatio)
        background_label.setPixmap(background_pixmap)
        background_label.setGeometry(0, 0, width, height)


        main_layout = QHBoxLayout()
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Fixed, QSizePolicy.Minimum))
        centerlayout = QVBoxLayout()

        # label displays the name of the application at the top of the window
        BirdHouseLabel = QLabel("BirdHouse", self)
        BHFont = QFont("Marker Felt", 60)
        BirdHouseLabel.setFont(BHFont)
        BirdHouseLabel.setStyleSheet("color: white;")
        BirdHouseLabel.setAlignment(QtCore.Qt.AlignCenter)
        centerlayout.addWidget(BirdHouseLabel)

        # Button triggers image upload
        GoToGardenButton = QPushButton("My Garden", self)
        GoToGardenButton.setFixedWidth(300)
        GoToGardenButton.setFixedHeight(60)
        GoToGardenButton.setStyleSheet("color: black;")
        GoToGardenButton.clicked.connect(self.OpenGardenWindow)
        centerlayout.addWidget(GoToGardenButton, alignment=QtCore.Qt.AlignLeft)

        # classified label will display the name of the bird species when a bird is classifed
        classifiedLabel_font = QFont("Marker Felt", 35)
        self.classifiedLabel.setFont(classifiedLabel_font)
        self.classifiedLabel.setStyleSheet("color: white;")
        self.classifiedLabel.setAlignment(QtCore.Qt.AlignCenter)
        centerlayout.addWidget(self.classifiedLabel)

        # widget to contain image
        self.imageHolder = QWidget(self)
        self.imageHolder.setStyleSheet("background-color: white;")
        self.imageHolder.setFixedSize(300, 300)
        centerlayout.addWidget(self.imageHolder, alignment=QtCore.Qt.AlignCenter)

        self.imageLabel = QLabel(self.imageHolder)

        # Button triggers image upload
        uploadImageButton = QPushButton("Upload Image", self)
        uploadImageButton.setFixedWidth(300)
        uploadImageButton.setFixedHeight(60)
        uploadImageButton.setStyleSheet("color: black;")
        uploadImageButton.clicked.connect(self.uploadImage)
        centerlayout.addWidget(uploadImageButton, alignment=QtCore.Qt.AlignCenter)

        main_layout.addLayout(centerlayout)
        central_widget = QWidget(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # database initlised so that bird data can be stored
        self.initliseDataBase()

        # creates an instance of the other window
        self.MyGarden = MyGarden()



    def initliseDataBase(self):

        #initlises conntection
        self.connection = sqlite3.connect('BirdData_database.db')
        self.cursor = self.connection.cursor()

        # creates table to store bird daga if it doesnt already exist
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS birds
                               (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, upload_date DATE)''')
        self.connection.commit()

    # allows user to upload an image from files then classifies it and stores that data
    def uploadImage(self):
        # Open a file dialog to select an image file
        file_dialog = QFileDialog()
        imagePath, _ = file_dialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")

        #if the path exists then...
        if imagePath:

            #image is loaded in and appears in the white box in the window
            #image is resized to fit
            pixmap = QPixmap(imagePath).scaled(300, 300, aspectRatioMode=QtCore.Qt.KeepAspectRatio)

            self.imageLabel.setPixmap(pixmap)
            self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
            layout = QVBoxLayout(self.imageHolder)
            layout.addWidget(self.imageLabel)

            # Store image path and upload date to database
            self.StoreImage(imagePath)

    #called each time an image is uploaded and classified to store data to SQL database
    def StoreImage(self, imagePath):
        # Get the name by classifying the image
        species = self.classifyImage(imagePath)

        # Update the text of the existing label
        self.classifiedLabel.setText(species)

        # Insert species and upload date into the database
        self.cursor.execute("INSERT INTO birds (name, upload_date) VALUES (?, datetime('now'))", (species,))
        self.connection.commit()


    def closeEvent(self, event):
        # closes database connection each time application closes
        self.connection.close()
        event.accept()

    def OpenGardenWindow(self):
        self.MyGarden.show()

    def classifyImage(self,imagePath):

        model = load_model('model.h5')
        image = self.preprocess_image(imagePath, target_size=(224, 224))
        prediction = model.predict(image)
        return prediction
    #ensures the image is in the expected format for the model to classify 
    def preprocess_image(self,imagepath,targetsize):
        image = load_img(imagepath, target_size=targetsize)
        imageAsArray = img_to_array(image)
        imageAsArray = np.expand_dims(imageAsArray, axis=0)  # Model expects a batch
        return imageAsArray


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
