import os
import sys
from datetime import datetime
from PySide6 import QtWidgets, QtCore


class PathWalker(QtCore.QThread):
    """
    Класс-поток для обхода файловых путей
    """
    size_received = QtCore.Signal(list)

    def __init__(self, path_to_count: str, parent=None):
        super().__init__(parent)

        self._path_to_count = path_to_count
        self._status = None

    def run(self) -> None:
        """
        Метод для запуска потока по обходу директорий

        :return: None
        """

        file_count = 0
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self._path_to_count):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                total_size += os.path.getsize(file_path)
                file_count += 1
        self.size_received.emit([total_size, file_count])

    def set_path(self, path: str) -> None:
        """
        Метод для установки с валидацией пути для обхода

        :return: None
        """

        if os.path.exists(path) and os.path.islink(path):
            self._path_to_count = path


class PathWalkerWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('PathWalker')
        self.resize(750, 430)

        self.initUi()
        self.initThreads()
        self.initSignals()

    def initUi(self) -> None:
        """
        Инициализация интерфейса

        :return: None
        """

        self.lineEditPath = QtWidgets.QLineEdit()
        self.lineEditPath.setPlaceholderText('Введите путь или выберете в каталоге')
        self.pushButtonSetPath = QtWidgets.QPushButton('Выбрать путь')

        self.groupBoxPathLine = QtWidgets.QGroupBox()
        self.groupBoxPathLine.setLayout(QtWidgets.QHBoxLayout())
        self.groupBoxPathLine.layout().addWidget(self.lineEditPath)
        self.groupBoxPathLine.layout().addWidget(self.pushButtonSetPath)

        self.pushButtonStartScan = QtWidgets.QPushButton('Запустить сканирование')

        self.groupBoxPath = QtWidgets.QGroupBox('Выберете путь')
        self.groupBoxPath.setLayout(QtWidgets.QVBoxLayout())
        self.groupBoxPath.layout().addWidget(self.groupBoxPathLine)
        self.groupBoxPath.layout().addWidget(self.pushButtonStartScan)

        self.progressBar = QtWidgets.QProgressBar()

        self.groupBoxProgress = QtWidgets.QGroupBox('Прогресс сканирования')
        self.groupBoxProgress.setLayout(QtWidgets.QHBoxLayout())
        self.groupBoxProgress.layout().addWidget(self.progressBar)

        layoutPath = QtWidgets.QVBoxLayout()
        layoutPath.addWidget(self.groupBoxPath)
        layoutPath.addWidget(self.groupBoxProgress)

        self.plainTextEditLog = QtWidgets.QPlainTextEdit()
        self.labelCount = QtWidgets.QLabel()
        self.labelSize = QtWidgets.QLabel()

        self.groupBoxLog = QtWidgets.QGroupBox()
        self.groupBoxLog.setLayout(QtWidgets.QVBoxLayout())
        self.groupBoxLog.layout().addWidget(self.plainTextEditLog)
        self.groupBoxLog.layout().addWidget(self.labelCount)
        self.groupBoxLog.layout().addWidget(self.labelSize)

        layoutMain = QtWidgets.QHBoxLayout()
        layoutMain.addLayout(layoutPath)
        layoutMain.addWidget(self.groupBoxLog)

        self.setLayout(layoutMain)

    def initThreads(self) -> None:
        """
        Инициализация потока

        :return: None
        """

        self.path_walker = PathWalker('')

    def initSignals(self) -> None:
        """
        Инициализация сигналов

        :return: None
        """

        self.pushButtonSetPath.clicked.connect(self.onPushButtonSetPathClicked)
        self.pushButtonStartScan.clicked.connect(self.onPushButtonStartScanClicked)
        # self.system_info_app.systemInfoReceived.connect(self.system_info_updated)

    def onPushButtonStartScanClicked(self) -> None:
        """
        Обработчик сигнала для запуска сканирования пути

        :return: None
        """

        self.pushButtonStartScan.setEnabled(False)
        self.path_walker.set_path(self.lineEditPath.text())
        self.path_walker.start()


    def onPushButtonSetPathClicked(self) -> None:
        """
        Обработчик сигнала для вызова каталога выбора пути для обхода

        :return: None
        """

        directory_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите каталог для сканирования", "")
        self.lineEditPath.setText(directory_path)



if __name__ == "__main__":
    app = QtWidgets.QApplication()

    window = PathWalkerWidget()
    window.show()

    app.exec()
