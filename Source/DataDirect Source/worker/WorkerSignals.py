from PyQt5.QtCore import QObject, pyqtSignal


class WorkerSignals(QObject):
    # Defining the signals available from a running worker thread
    # finished => No data
    # error => tuple
    # result => object (data returned from processing)
    # progress => int (% progress)
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)
