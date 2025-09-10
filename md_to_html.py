import markdown
from PySide6.QtWidgets import QFileDialog, QApplication, QDialog, QMainWindow, QListWidgetItem, QAbstractButton, QDialogButtonBox
from PySide6.QtCore import QSize, Slot
from converter_ui.python.confirmation_ui import Ui_Form
from converter_ui.python.main_ui import Ui_MainWindow
import os


class WindowResizeSmall:
    x = 400
    y = 100

class WindowResizeLarge:
    x = 400
    y = 300



def write_to_html(md_name: str, html_name: str):
    with open(md_name, "r", encoding="utf8") as file:
        with open(html_name, "w", encoding="utf8") as html:
            html.write(markdown.markdown(file.read()))

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self._confirm = Ui_Form()
        self._popup = QDialog()
        self._confirm.setupUi(self._popup)

        if not self.fileList.isEnabled():
            self.fileList.setVisible(False)

        self.resize(QSize(WindowResizeSmall.x, WindowResizeSmall.y))

        self.openFileDialog.pressed.connect(self.selectFilesForConversion)
        self.convertFiles.pressed.connect(self.convertSelectedFiles)

        self.file_paths = dict()

        self._confirm.buttonBox.clicked.connect(self.confirmClicked)
        self.buttonclicked: QAbstractButton = None

    def enableFileList(self, enable: bool):
        self.fileList.setEnabled(enable)
        self.fileList.setVisible(enable)

        if enable:
            self.resize(QSize(WindowResizeLarge.x, WindowResizeLarge.y))

    def enableConversionItems(self, enable: bool):
        self.convertFiles.setEnabled(enable)
        self.progressBar.setEnabled(enable)
        self.progressBar.setValue(0)

    def appendToFileList(self, files: list[str]):
        for file in files:
            name = os.path.basename(file)
            self.file_paths[name] = file

            item = QListWidgetItem()
            item.setText(name)

            self.fileList.addItem(item)

    def showConfirmationPopup(self, show: bool):
        if show:
            self._popup.show()
            self._popup.exec()
        else:
            self._popup.hide()
            self._popup.close()

    @Slot()
    def selectFilesForConversion(self):
        dialog = QFileDialog(self)
        dialog.setNameFilter("Markdown (*.md)")

        names = []

        if dialog.exec():
            names = dialog.selectedFiles()
            if len(names) > 0:
                self.enableFileList(True)
                self.appendToFileList(names)
                self.enableConversionItems(True)

    @Slot()
    def convertSelectedFiles(self):
        dont_ask = False
        files = self.fileList.selectedItems()

        for index, item in enumerate(files):
            written = False
            name = item.text()
            print(name)
            file = self.file_paths[name]

            html_file = file.rsplit(".", 1)[0] + ".html"

            if (os.path.exists(html_file) and not dont_ask):
                self.showConfirmationPopup(True)

                if self.buttonclicked == self._confirm.buttonBox.button(
                        QDialogButtonBox.StandardButton.YesToAll):
                    dont_ask = True
                    write_to_html(file, html_file)
                    written = True

                elif self.buttonclicked == self._confirm.buttonBox.button(
                        QDialogButtonBox.StandardButton.Yes):
                    write_to_html(file, html_file)
                    written = True

                elif self.buttonclicked == self._confirm.buttonBox.button(
                        QDialogButtonBox.StandardButton.Cancel):
                    # Do nothing
                    pass

            else:
                write_to_html(file, html_file)
                written = True

            if written:
                val = (index + 1) / len(files) * 100
                self.progressBar.setValue(int(val))

    @Slot()
    def confirmClicked(self, button: QAbstractButton):
        self.buttonclicked = button
        self.showConfirmationPopup(False)

            
if __name__ == "__main__":
    app = QApplication()
    window = MainWindow()
    window.show()
    app.exec()
