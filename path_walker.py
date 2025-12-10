import os
import time
from PySide6 import QtWidgets, QtCore


class PathWalker(QtCore.QThread):
    """
    Класс-поток для обхода файловых путей
    """

    progress_received = QtCore.Signal(list)
    data_received = QtCore.Signal(dict)

    def __init__(self, path_to_count: str, parent=None):
        super().__init__(parent)

        self.path_to_count = path_to_count

    def run(self) -> None:
        """
        Метод для запуска потока по обходу директорий

        :return: None
        """
        data = {}
        file_count = 0
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.path_to_count):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                total_size += os.path.getsize(file_path)
                file_count += 1

                step = filenames.index(filename) + 1
                process_length = len(filenames)

                self.progress_received.emit([step, process_length])
                time.sleep(0.05)
        data['file_count'] = file_count
        data['total_size'] = total_size
        self.data_received.emit(data)

    def set_path(self, path: str) -> None:
        """
        Метод для установки с валидацией пути для обхода

        :return: None
        """

        if os.path.exists(path) and not os.path.islink(path):
            self.path_to_count = path


class PathWalkerWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('PathWalker')
        self.setFixedSize(750, 430)

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
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)

        self.groupBoxProgress = QtWidgets.QGroupBox('Прогресс сканирования')
        self.groupBoxProgress.setLayout(QtWidgets.QHBoxLayout())
        self.groupBoxProgress.layout().addWidget(self.progressBar)

        layoutPath = QtWidgets.QVBoxLayout()
        layoutPath.addWidget(self.groupBoxPath)
        layoutPath.addWidget(self.groupBoxProgress)

        self.plainTextEditLog = QtWidgets.QPlainTextEdit()
        self.plainTextEditLog.setReadOnly(True)
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
        # self.path_walker.

    def initSignals(self) -> None:
        """
        Инициализация сигналов

        :return: None
        """

        self.pushButtonSetPath.clicked.connect(self.onPushButtonSetPathClicked)
        self.pushButtonStartScan.clicked.connect(self.onPushButtonStartScanClicked)
        self.path_walker.data_received.connect(lambda data: self.update_log(data))
        self.path_walker.progress_received.connect(lambda progress: self.update_progress_bar(progress))
        self.path_walker.finished.connect(lambda: self.pushButtonStartScan.setEnabled(True))

    def onPushButtonStartScanClicked(self) -> None:
        """
        Обработчик сигнала для запуска сканирования пути

        :return: None
        """

        self.pushButtonStartScan.setEnabled(False)
        self.path_walker.set_path(self.lineEditPath.text())

        self.start_time = time.ctime()
        self.path_walker.start()


    def onPushButtonSetPathClicked(self) -> None:
        """
        Обработчик сигнала для вызова каталога выбора пути для обхода

        :return: None
        """

        directory_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите каталог для сканирования", "")
        self.lineEditPath.setText(directory_path)

    def update_progress_bar(self, progress: list) -> None:
        step_value = 100 / progress[1]
        self.progressBar.setValue(progress[0] * step_value)

    def update_log(self, data: dict) -> None:
        """
        Обработчик сигнала полученных данных с потока path_walker, обновляет лог и лейблы

        :param data: список с данными, полученными в процессе работы потока path_walker
        :return: None
        """

        finish_time = time.ctime()

        if data["total_size"] >= pow(1024, 3):
            formated_total_size = f'{round(data["total_size"] / pow(1024, 3), 1)} ГБ'
        elif data["total_size"] >= pow(1024, 2):
            formated_total_size = f'{round(data["total_size"] / pow(1024, 2), 1)} МБ'
        elif data["total_size"] >= 1024:
            formated_total_size = f'{round((data["total_size"] / 1024), 1)} КБ'
        else:
            formated_total_size = f'{data["total_size"]} Б'

        self.labelSize.setText(f'Размер: {formated_total_size}\n')
        self.labelCount.setText(f'Кол-во: {data["file_count"]}\n')
        self.plainTextEditLog.appendPlainText(f'Путь к папке: {self.lineEditPath.text()}\n\n'
                                              f'Общий размер файлов: {formated_total_size}\n'
                                              f'Просканировано файлов: {data["file_count"]}\n\n'
                                              f'Время начала сканирования: {self.start_time}\n'
                                              f'Время завершения сканирования: {finish_time}\n'
                                              f'{"="  * 40}\n')


if __name__ == "__main__":
    app = QtWidgets.QApplication()

    window = PathWalkerWidget()
    window.show()

    app.exec()
