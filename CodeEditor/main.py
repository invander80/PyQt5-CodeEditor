"""
(1) Zeile 49: Pfad nach Bedarf auswaehlen / aendern
"""
import PyInstaller.config
import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QDir, pyqtSlot, QModelIndex, \
    QTimer, QSize, QRegExp
from high import PythonHighlighter

from ui.ui_main import *
from data.codeedit import CodeEditor


class MainWindow(QWidget, Ui_Form):
    keyPressed = pyqtSignal(str)
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setupUi(self)                              # // UI Initialisieren

        self.remove_title_bar()                         # // TitleBar entfernen

        self.menuBar.mouseMoveEvent = self.move_win     # // Fenster bewegen
        self.menuBar.mouseDoubleClickEvent = self.dblClicked

        self.codeedit = CodeEditor(self)                # // CodeEditor Referenz
        self.textLayout.addWidget(self.codeedit)
        self.codeedit.setTabStopDistance(40.0)          # // Tabulator 40 Steps

        self.highlighter = PythonHighlighter(self.codeedit.document())

        # -------------------------------------------------------------------------------------------------------------#
        #                                               Fenster SizeGrips                                                 #
        # -------------------------------------------------------------------------------------------------------------#
        self.gripSize = 16
        self.grips = []
        for i in range(4):
            grip = QSizeGrip(self)
            grip.resize(self.gripSize, self.gripSize)
            self.grips.append(grip)

        # -------------------------------------------------------------------------------------------------------------#
        #                                               FILE EXPLORER                                                  #
        # -------------------------------------------------------------------------------------------------------------#
        self.exp = QFileSystemModel()
        self.exp.setRootPath((QDir.rootPath()))
        self.path = "C:/Users/xmich/Programmier Sprachen"                   # // PFAD FUER DEN EXPLORER
        self.treeView.setModel(self.exp)
        self.treeView.setIconSize(QSize(20, 20))
        self.treeView.setRootIndex(self.exp.index(self.path))
        self.treeView.setSortingEnabled(True)
        self.treeView.clicked.connect(self.on_item_clicked)
        for i in range(1, self.treeView.model().columnCount()):
            self.treeView.header().hideSection(i)
        self.exp.setReadOnly(False)
        self.treeView.setSelectionMode(self.treeView.SingleSelection)
        self.treeView.setDragDropMode(QAbstractItemView.InternalMove)
        self.treeView.setDragEnabled(True)
        self.treeView.setAcceptDrops(True)
        self.treeView.setDropIndicatorShown(True)


        # -------------------------------------------------------------------------------------------------------------#
        #                                       Butttons -> Frame Animationen                                          #
        # -------------------------------------------------------------------------------------------------------------#
        self.settingBtn.clicked.connect(lambda :self.property_changed(self.settingBtn,
                                        self.groupBox, 45, b"maximumHeight"))   # // Öffnet die GroupBox
        self.expandBtn.clicked.connect(lambda :self.property_changed(self.expandBtn,
                                        self.optionBar, 300, b"minimumWidth"))  # // Öffnet die navBar
        self.restoreBtn.clicked.connect(self.restoreWindow)
        self.clearTextBtn.clicked.connect(self.clearText)
        self.saveBtn.clicked.connect(self.saveText)
        self.openBtn.clicked.connect(self.openCmd)

        # -------------------------------------------------------------------------------------------------------------#
        #                                                Schatten Setzen                                               #
        # -------------------------------------------------------------------------------------------------------------#
        #self.set_shadow(self.menuBar, 10, "#00d0ff", 3, 0)             # // MenuBar
        #self.set_shadow(self.navBar, 10, "#00d0ff", 0, 3)              # // NavBar
        #self.set_shadow(self.optionBar, 20, "#00d0ff", 0, 0)           # // OptionBar
        #self.set_shadow(self.textContainer, 15, "#191c22", 0,0)        # // CodeEditor // Performance Verlust
        #self.set_shadow(self.groupBox, 20, "#191c22", 0,8)
        self.set_shadow(self, 20, "#00e6ff", 0, 0)                      # // MainWindow// Hoher Performance Verlust

        self.state = True

    # -----------------------------------------------------------------------------------------------------------------#
    def clearText(self):
        self.codeedit.clear()

    # --------------------------------------------- Ordner Name -------------------------------------------------------#
    def getFolderName(self):
        txt, ok = QInputDialog.getText(self, "Neuer Ornder", "Name", QLineEdit.Normal)
        if txt and ok != "":
            return txt

    # -------------------------------------------- Gesamter Pfad ------------------------------------------------------#
    def getPath(self):
        indexItem = self.exp.index(self.treeView.currentIndex().row(), 0, self.treeView.currentIndex().parent())
        filepath = self.exp.filePath(indexItem)
        return filepath

    # ------------------------------------------- Ordner Pfad ---------------------------------------------------------#
    def getDirectory(self):
        indexItem = self.treeView.currentIndex().parent()
        return self.exp.filePath(indexItem)

    # ------------------------------------------- Name des ausgewahlten Items -----------------------------------------#
    def getFileItem(self):
        indexItem = self.exp.index(self.treeView.currentIndex().row(), 0, self.treeView.currentIndex().parent())
        return self.exp.fileName(indexItem)

    # ------------------------------------------ Namen im TreeView aendern --------------------------------------------#
    def change_name(self, name):
        index = self.treeView.currentIndex()
        if index.isValid():
            wasReadOnly = self.exp.isReadOnly()
            self.exp.setReadOnly(False)
            self.exp.setData(index, name)
            self.exp.setReadOnly(wasReadOnly)

    # -----------------------------------------------------------------------------------------------------------------#
    def contextMenuEvent(self, event) -> None:
        menu = QMenu()
        menu.setStyleSheet("QMenu{background: #191c22; color:white; border:1px solid #5a616f}"
                           "QMenu::selected{background:#5a616f}"
                           "QMenu::pressed{background:#2d3138}")
        newFile = menu.addAction("Neue Datei")
        newFolder = menu.addAction("Neuer Order")
        menu.addSeparator()
        rename = menu.addAction("Umbenennen")
        showall = menu.addAction("Alle Ordner öffnen")
        hideall = menu.addAction("Alle Ordner schließen")
        menu.addSeparator()
        delete = menu.addAction("Löschen")
        if self.expandBtn.isChecked():
            action = menu.exec(self.mapToGlobal(event.pos()))

            ### Neuer Ornder
            if action == newFolder:
                current_index = self.treeView.currentIndex()
                index = self.exp.mkdir(current_index, self.getFolderName())
                QTimer.singleShot(0, lambda index=index: self.treeView.setCurrentIndex(index))
                QTimer.singleShot(0, lambda index=index: self.treeView.edit(index))

            ### Neue Datei
            if action == newFile:
                txt, ok = QInputDialog.getText(self, "Neue Datei", "Name", QLineEdit.Normal)
                if txt and ok != "":
                    fp = open(f"{self.getPath()}/{txt}", "x")
                    fp.close()
            ### Dateien / Ordner Umbenenen
            if action == rename:
                txt, ok = QInputDialog.getText(self, "Umbenenen", "Neuer Name", QLineEdit.Normal)
                if txt and ok != "":
                    self.change_name(txt)

            ### Alle Ordner aufklappen
            if action == showall: self.treeView.expandAll()

            ### Alle Ordner zuklappe
            if action == hideall: self.treeView.collapseAll()

            ### Datei / Ordner entfernen
            if action == delete:
                item = QModelIndex(self.exp.index(self.getPath()))
                self.exp.remove(item)

    # -------------------------------------------------------------------------------------------------------------#
    ### Text speichern (saveBtn)
    def saveText(self):
        if self.getFileItem().endswith(".py") or self.getFileItem().endswith(".cs") or self.getFileItem().endswith(".cpp")\
                or self.getFileItem().endswith(".txt"):
            with open(self.getPath(), "w") as f:
                input = self.codeedit.toPlainText()
                f.write(input)
        else:
            QMessageBox.warning(self, "Info", "Bitte die zu Speichernde Datei auswählen")

    # ------------------------------------- Dateien in den Editor einlesen --------------------------------------------#
    @pyqtSlot(QModelIndex)
    def on_item_clicked(self):
        self.settingsLbl.setText(f"Akuteller Pfad: {self.getPath()}")
        #self.codeedit.clear()
        if self.getFileItem().endswith(".py") or self.getFileItem().endswith(".cs") or self.getFileItem().endswith(".cpp")\
                or self.getFileItem().endswith(".txt"):
            with open(self.getPath(), "r") as f:
                txt = f.read()
                self.codeedit.setPlainText(txt)
            with open(self.getPath(), "w") as f:
                input = self.codeedit.toPlainText()
                f.write(input)
        else:
            self.treeView.update()

    # -------------------------------------------- Commando Prompt ----------------------------------------------------#
    def openCmd(self):
        path = os.path.abspath(self.getDirectory().replace("/", "\\"))
        name = self.getFileItem().replace(".cpp", "")
        os.chdir(path)
        if self.getFileItem().endswith(".py"):
            os.system(f"start cmd /K python {self.getFileItem()}")
        elif self.getFileItem().endswith(".cpp"):
            os.system(f"g++ -o {name} {name}.cpp&{name}.exe")
            os.popen(f"start cmd /K {name}.exe")
        elif self.getFileItem().endswith(".cs"):
            os.system(f"csc {self.getFileItem()}")
            os.system(f"start cmd /K {self.getFileItem().replace('.cs', '')}")
        else:
            QMessageBox.warning(self, "Info", "Ungültige Aktion. Bitte eine Datei auswählen.")

    # -----------------------------------------------------------------------------------------------------------------#
    # ----------------------------------------- Fenster und Widget Eigenschaften --------------------------------------#
    # -----------------------------------------------------------------------------------------------------------------#
    ### Fenster Status Normal und Maximized
    def restoreWindow(self):
        if self.restoreBtn.isChecked():
            self.showMaximized()
        else:
            self.showNormal()

    ### Fenster bewegen
    def move_win(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

    ### TitleBar entfernen
    def remove_title_bar(self):
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

    ### Animation der Frames
    def property_changed(self, btn, widget, end, prop):
        self._animate = QPropertyAnimation(widget, prop)
        self._animate.setDuration(1000)
        self._animate.setEasingCurve(QEasingCurve.OutBounce)
        if btn.isChecked():
            self._animate.setEndValue(end)
            self._animate.start()
        else:
            self._animate.setEndValue(0)
            self._animate.start()

    ### Schaten initialisieren
    def set_shadow(self, widget, radius, color, x, y) :
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(radius)
        shadow.setXOffset(x)
        shadow.setYOffset(y)
        shadow.setColor(QColor(color))
        widget.setGraphicsEffect(shadow)

    ### Fenstergroesse anpassen
    def resizeEvent(self, event):
        #QMainWindow.resizeEvent(self, event)
        rect = self.rect()
        self.grips[1].move(rect.right() - self.gripSize, 0)
        self.grips[2].move(
            rect.right() - self.gripSize, rect.bottom() - self.gripSize)
        self.grips[3].move(0, rect.bottom() - self.gripSize)

    ### Drag and Drop event
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            # to get a list of files:
            drop_list = []
            for url in event.mimeData().urls():
                drop_list.append(str(url.toLocalFile()))
            # handle the list here
        else:
            event.ignore()

    def dblClicked(self, event):
        self.showMaximized()
        self.restoreBtn.setChecked(True)

    def closeEvent(self, event):
        msg = QMessageBox()
        x = msg.question(self, "Beenden", "Bist du sicher? Das Programm wird beendet!", QMessageBox.Yes | QMessageBox.No)
        if x == QMessageBox.Yes:
            self.close()
            event.accept()
        else:
            event.ignore()
    # -----------------------------------------------------------------------------------------------------------------#


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    mw = MainWindow()

    mw.show()
    app.exec()