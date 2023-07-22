# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pacientes_perfil.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFileDialog
import generar3dvroboflow
import generar3dvlocal

class HoverButton(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        super(HoverButton, self).__init__(parent)
        
        # Designar el style sheet original
        self.setStyleSheet("background-color: #0A71B8; color: white; font-weight: normal;")
        
        # Instalar filtros de eventos
        self.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.HoverEnter:
            # Evento hover de entrada: cambia el estilo del botón
            self.setStyleSheet("background-color: #0A466F; color: white; font-weight: bold;")
            self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        elif event.type() == QtCore.QEvent.HoverLeave:
            # Evento hover de salida: restaura el estilo del botón
            self.setStyleSheet("background-color: #0A71B8; color: white; font-weight: normal;")
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        
        return super(HoverButton, self).eventFilter(obj, event)

class Ui_MainWindow(object):

    
    
    def setupUi(self, MainWindow):
        self.dni_paciente = None
        MainWindow.setObjectName("Perfil")
        MainWindow.resize(1000, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
       
        #Imagen del Odontograma
        self.img_Odontograma = QtWidgets.QLabel(self.centralwidget)
        self.img_Odontograma.setGeometry(QtCore.QRect(100, 150, 350, 260))
        self.img_Odontograma.setText("")
        self.img_Odontograma.setPixmap(QtGui.QPixmap("src/images/odon_placeholder.jpg"))
        self.img_Odontograma.setScaledContents(True)
        self.img_Odontograma.setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Plain)
        self.img_Odontograma.setObjectName("img_Odontograma")

        #Botones
        self.ButtonGenerar3D = HoverButton(self.centralwidget)
        self.ButtonGenerar3D.setGeometry(QtCore.QRect(620, 300, 200, 30))
        self.ButtonGenerar3D.setObjectName("ButtonGenerar3D")
        self.ButtonSubirImagen = QtWidgets.QPushButton(self.centralwidget)
        self.ButtonSubirImagen.setGeometry(QtCore.QRect(620, 200, 200, 38))
        self.ButtonSubirImagen.setObjectName("ButtonSubirImagen")
        # Asignar el cursor de la manito al botón
        self.ButtonSubirImagen.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.ButtonSubirImagen.clicked.connect(self.selectImage)
        self.ButtonGenerar3D.clicked.connect(self.generate3DModel)
    


    def selectImage(self):
        file_dialog = QFileDialog()
        image_path, _ = file_dialog.getOpenFileName(None, "Seleccionar imagen", "", "Imagen (*.png *.jpg *.jpeg)")
        print(image_path)
        if image_path:
            # Cargar la imagen como bytes
            with open(image_path, "rb") as file:
                self.image_bytes = file.read()


            # Actualizar la imagen en la interfaz de usuario si es necesario
            pixmap = QPixmap()
            pixmap.loadFromData(self.image_bytes)
            self.img_Odontograma.setPixmap(pixmap)

    
        
    def generate3DModel(self):
        if hasattr(self, "image_bytes") and self.image_bytes:  # Verifica que los bytes de las imágenes esten disponibles
            temp_image_path = "src/temp_image.jpg"
            with open(temp_image_path, "wb") as file:
                file.write(self.image_bytes)

            generar3dvlocal.convertir(img_path=temp_image_path) #Cambiar a generar3dvroboflow.convertir(img_path=temp_image_path) para ver el resultado en Roboflow

        else:
            print("No se ha cargado ninguna imagen del odontograma. Por favor, seleccione una imagen antes de generar el modelo 3D.")

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("Perfil de Paciente", "Perfil de Paciente"))
        MainWindow.setWindowIcon(QIcon("src/images/icon.png"))     
        self.ButtonGenerar3D.setText(_translate("MainWindow", "Generar Modelo 3D"))
        self.ButtonSubirImagen.setText(_translate("MainWindow", "Subir imagen"))
        

    