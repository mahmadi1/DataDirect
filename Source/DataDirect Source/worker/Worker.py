import sys
import traceback

from PyQt5.QtCore import pyqtSlot, QRunnable

from worker.WorkerSignals import WorkerSignals


class Worker(QRunnable):

    # Initializing worker thread, the arguments will take in a function and
    # its respective arguments in order to run that function in a separate array
    # than the gui thread
    def __init__(self, fn, file_path, custom_array, analy_array, bio_num):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.file_path = file_path
        self.custom_array = custom_array
        self.analy_array = analy_array
        self.bio_num = bio_num
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(self.file_path, self.custom_array, self.analy_array, self.bio_num)

        # sending error if unable to run function
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))

        # outputting thread result
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done
