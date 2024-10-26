from PyQt5.QtWidgets import *

app = QApplication([])
window = QWidget()

layout = QVBoxLayout()

label = QLabel("youssef")
layout.addWidget(label)

window.setLayout(layout)

window.show()
app.exec()