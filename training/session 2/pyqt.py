from PyQt5.QtWidgets import *

app = QApplication([])

def prnt(value):
    print(value)

label = QLabel("overflow")

combo = QComboBox()
combo.addItems(["name 1","name 2"," name 3"])
combo.currentIndexChanged.connect(prnt)

line = QLineEdit()
line.setPlaceholderText("enter your name")
line.returnPressed.connect(prnt)

slid = QSlider()
slid.setMinimum(1)
slid.setMaximum(10)
slid.valueChanged.connect(prnt)
layout = QVBoxLayout()


layout.addWidget(label)
layout.addWidget(combo)
layout.addWidget(line)
layout.addWidget(slid)
window = QWidget()
window.setLayout(layout)
window.show()

app.exec()