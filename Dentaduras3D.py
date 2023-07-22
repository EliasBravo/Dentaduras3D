import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QFont
from pacientes_perfil import Ui_MainWindow

def window():
    app = QApplication(sys.argv)
    font = QFont("Roboto")
    QApplication.setFont(font)
    win = QMainWindow() 
    
    ui = Ui_MainWindow()
    ui.setupUi(win)
    win.setGeometry(450,200,1000,600)
    win.setWindowTitle("Conversión a Dentaduras 3D")
    win.setWindowIcon(QIcon("src/images/icon.png"))
    win.show()
    sys.exit(app.exec_())

window()