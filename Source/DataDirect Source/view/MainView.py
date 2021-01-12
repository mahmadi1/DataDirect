from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QWidget, QFileDialog

from ui.Ui_View import Ui_View
from worker.Worker import Worker

import pandas as pd
import numpy as np


class MainView(QWidget, Ui_View):
    def __init__(self, parent=None):
        super(MainView, self).__init__(parent=parent)
        self.setupUi(self)
        # path to the selected spreadsheet
        self.file_path = None

        # custom array, analyze array, and bio_num will be used as inputs for the run function
        self.custom = [0, 0, 0, 0]
        self.analy = [0, 0, 0, 0, 0, 0, 0, 0]
        self.bio_num = 0

        # final_df is the dataframe output of the run function
        self.final_df = None
        self.spreadsheet = None

        # Page 0 Buttons (Intro page)
        self.page1_nextBtn.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))

        # Page 1 Buttons (Add File page)
        self.page2_backBtn.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.page2_nextBtn.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))

        # addfilebutton will call file_handle which will open a dialog box (section 1 of support codes)
        self.addfilebutton.clicked.connect(self.addfile_handler)

        # Page 2 Buttons (Analytics page)
        self.page3_nextBtn.clicked.connect(self.array_maker)
        self.page3_backBtn.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))

        # Page 3 Buttons (Run page)
        self.page4_backBtn.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.page4_runBtn.clicked.connect(self.run)

        # Page 4 Buttons (Save file page)
        self.page5_saveBtn.clicked.connect(self.savefile)
        self.page5_restartBtn.clicked.connect(self.restart)

        # creating a thread
        self.threadpool = QThreadPool()

    # Function will open a file dialog so a file can be selected
    # It will utilize the open_dialog_box function and send the

    # Section 1
    # Add File Functions======================
    # ===============================================================================
    def addfile_handler(self):
        print("Button pressed")
        self.open_dialog_box()

    def open_dialog_box(self):
        filename = QFileDialog.getOpenFileName()
        self.file_path = filename[0]

        # change file status text
        self.file_status.setText(self.file_path)
        print(self.file_path)

        # Save File Functions========================================================

    def savefile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        pathsave_custom = \
            QFileDialog.getSaveFileName(None, "Select destination folder and file name", "Final_Dataset.csv", "(*.csv)",
                                        options=options)[0]
        print(pathsave_custom)
        self.final_df.to_csv(pathsave_custom, index=False)

        # Restart =====================================================================

    def restart(self):
        self.stackedWidget.setCurrentIndex(1)
        self.page4_runBtn.setText('Run')
        self.file_status.setText('Not Selected')

        # Section 2
        # Analytics functions=================
        # ================================================================================
        # ============custom_arry puts customization checkbox values into the custom array

    def custom_array(self):
        self.custom[0] = self.cust_pval_check.checkState()
        self.custom[1] = self.cust_actType_check.checkState()
        self.custom[2] = self.cust_illuscore_check.checkState()
        self.custom[3] = self.cust_active_score.checkState()

        # ========== analy_array puts analytics checkbox values into the analy array

    def analy_array(self):
        self.analy[0] = self.ana_dis_check.checkState()
        self.analy[1] = self.ana_sum_check.checkState()
        self.analy[2] = self.ana_mean_check.checkState()
        self.analy[3] = self.ana_median_check.checkState()
        self.analy[4] = self.ana_std_check.checkState()
        self.analy[5] = self.ana_centchange_check.checkState()
        self.analy[6] = self.ana_specperc_check.checkState()
        self.analy[7] = self.ana_specint_check.checkState()

        # ===========calls the array functions above and goes to next page (run page)

    def array_maker(self):
        self.custom_array()
        self.analy_array()

        # bioset spinbox value
        self.bio_num = self.bioset_val_input.value()
        self.stackedWidget.setCurrentIndex(3)

        print(self.bio_num)
        print(self.custom)
        print(self.analy)

    # Section 3
    def thread_complete(self):
        print("Backend Thread Complete!")
        if isinstance(self.final_df, pd.DataFrame):
            print("DATAFRAME IS READY!")
        self.stackedWidget.setCurrentIndex(4)

    def run(self):
        # Pass the function to execute
        self.page4_runBtn.setText('Running...Please wait.')
        worker = Worker(self.Run_master, self.file_path, self.custom, self.analy,   self.bio_num)  # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.set_result)
        worker.signals.finished.connect(self.thread_complete)
        # Execute
        self.threadpool.start(worker)

    def set_result(self, df):
        self.final_df = df

        # def old_run(self):
        # change run button text
        # self.page4_runBtn.setText('Running...Please wait.')
        # Run the backend codes
        #    self.final_df = self.Run_master()

        # Go to next page
        #   self.stackedWidget.setCurrentIndex(4)

    def Run_master(self, file_path, custom_array, analy_array, bio_num):
            # temporarily save a copy of the original dataframe
            df = pd.read_csv(file_path, header=0, escapechar='\\')

            original_df = df
            print("past df")
            print(self.custom)
            print(self.file_path)
            print(self.analy)
            print(self.bio_num)

            # working_df will be the dataframe that will undergo changes

            # ---------------------------------------------- Analytics functions ------------------------

            # Function 1 = negative score (illumina direction)
            def negative_score(dataframe, Bioset_count):
                df = dataframe
                temp = Bioset_count + 1
                bio_count = 1
                act = 8
                score = 5
                # act = 6
                # score = 3
                count_row = df.shape[0]
                while bio_count < temp:
                    count = 0
                    while count < count_row:
                        if df[df.columns[act]][count] < 0:
                            value = df[df.columns[score]][count]
                            df.iloc[count, df.columns.get_loc(df.columns[score])] = value * -1
                        count += 1
                    bio_count += 1
                    act += 4
                    score += 4

                return df

            # Function 2 = Mean, median, std deviation, and sum

            def sco_array(df, bio_count):
                temp = bio_count + 1
                length = df.shape[0]
                array = []
                count = 0
                while count < length:
                    temp_array = []
                    b_count = 1
                    score = 5
                    while b_count < temp:
                        value = df[df.columns[score]][count]
                        temp_array.append(value)
                        score += 4
                        b_count += 1
                    count += 1
                    array.append(temp_array)
                return array

            # Function 3 = Postive and negative change above and below

            # ------------ This function will get the percentage change above and below as a tuple
            def percent_posandneg(dataframe, Bioset_count):
                df = dataframe
                temp = Bioset_count + 1
                count_row = df.shape[0]
                counter = 0
                percent_array = []
                while counter < count_row:
                    temp_percent = []
                    bio_count = 1
                    score = 5
                    positive_counter = 0
                    negative_counter = 0
                    while bio_count < temp:
                        value = df.iloc[counter, score]
                        if value > 0:
                            positive_counter += 1
                        elif value < 0:
                            negative_counter += 1
                        bio_count += 1
                        score += 4
                    counter += 1
                    pos = positive_counter / Bioset_count
                    temp_percent.append(pos)
                    neg = negative_counter / Bioset_count
                    temp_percent.append(neg)
                    percent_array.append(temp_percent)

                return percent_array

            # -------------------- This function will separate the tuple from the above function
            def seperate_ar(array):
                length = len(array)
                pos_percent = []
                neg_percent = []
                i = 0
                while i < length:
                    pos = array[i][0]
                    pos_percent.append(pos)
                    neg = array[i][1]
                    neg_percent.append(neg)
                    i += 1
                return pos_percent, neg_percent

            # Function 4 = Specificity as Percentage
            def percent_array(df, bio_count):
                temp = bio_count + 1
                length = df.shape[0]
                array = []
                count = 0
                while count < length:
                    temp_array = []
                    studies_counter = 0
                    b_count = 1
                    score = 5
                    while b_count < temp:
                        value = df[df.columns[score]][count]
                        # temp_array.append(value)
                        score += 4
                        b_count += 1
                        if value != 0:
                            studies_counter += 1
                    count += 1
                    temp_array.append(studies_counter)
                    array.append(temp_array)
                return array

            # Checking to see if directional illumina is checked and if true, then adjusting score
            # based on activity

            working_df = df
            if self.analy[0] == 2:
                print("passed first check")
                # Temp_neg_df = negative_score(working_df, bio_num)
                temp_df = original_df.fillna(0)
                working_df = negative_score(temp_df, self.bio_num)

                # working_df = Temp_neg_df

            # calculating the mean, median, std, and/or sum
            if self.analy[1] == 2 or self.analy[2] == 2 or self.analy[3] == 2 or self.analy[4] == 2:
                Temp_stats_df = sco_array(working_df, bio_num)
                length = len(Temp_stats_df)
                count = 0
                mean_array = []
                median_array = []
                std_array = []
                sum_array = []
                total_col = len(working_df.columns)
                while count < length:
                    temp_mean = np.mean(Temp_stats_df[count])
                    mean_array.append(temp_mean)

                    temp_med = np.median(Temp_stats_df[count])
                    median_array.append(temp_med)

                    temp_std = np.std(Temp_stats_df[count])
                    std_array.append(temp_std)

                    temp_sum = np.sum(Temp_stats_df[count])
                    sum_array.append(temp_sum)
                    count += 1

                if self.analy[1] == 2:
                    working_df.insert(total_col, "Mean Score", mean_array, True)
                if self.analy[2] == 2:
                    working_df.insert(total_col, "Median Score", median_array, True)
                if self.analy[3] == 2:
                    working_df.insert(total_col, "Standard Deviation", std_array, True)
                if self.analy[1] == 2:
                    working_df.insert(total_col, "Score Sum", sum_array, True)

            # Calculating the percent change above/below control
            if self.analy[5] == 2:
                total_col = len(working_df.columns)
                Temp_percent = percent_posandneg(working_df, self.bio_num)
                pos_percent, neg_percent = seperate_ar(Temp_percent)
                working_df.insert(total_col, "Proportion positive in studies", pos_percent, True)
                working_df.insert(total_col, "Proportion negative in studies", neg_percent, True)

            # Calculating the specificity as a percentage
            if self.analy[6] == 2:
                total_col = len(working_df.columns)
                Temp_specificity_cent = percent_array(working_df, self.bio_num)
                Temp_percent = []
                for value in Temp_specificity_cent:
                    value = value[0] / self.bio_num
                    Temp_percent.append(value)
                working_df.insert(total_col, "Specificity as Percentage", Temp_percent, True)

            # if the user decides to remove the original specificty column, then this will drop the column
            if self.analy[7] == 0:
                working_df = working_df.drop('Specificity', axis=1)

            # ---------------------------------------------- Table customization ----------------------
            working_df = working_df

            # Activity score: if not checked, the activity score will be removed
            if self.custom[3] == 0:
                bio_counter = 1
                bio_count_max = self.bio_num + 1
                active_score_index = 8
                while bio_counter < bio_count_max:
                    working_df.drop(working_df.columns[active_score_index], axis=1, inplace=True)
                    active_score_index = active_score_index - 1
                    active_score_index += 4
                    bio_counter += 1

            # Activity type: if not checked, the activity columns will be removed
            if self.custom[1] == 0:
                bio_counter = 1
                bio_count_max = self.bio_num + 1
                addition_factor = 4
                if self.custom[3] == 0:
                    addition_factor = 3
                active_type_index = 7
                while bio_counter < bio_count_max:
                    working_df.drop(working_df.columns[active_type_index], axis=1, inplace=True)
                    active_type_index = active_type_index - 1
                    active_type_index += addition_factor
                    bio_counter += 1

            # P-Value: if not checked, the p-value columns will be removed
            if self.custom[0] == 0:
                bio_counter = 1
                bio_count_max = self.bio_num + 1
                p_val_index = 6
                addition_factor = 4
                if self.custom[3] == 0 and self.custom[1] == 0:
                    addition_factor = 2
                else:
                    addition_factor = 3
                while bio_counter < bio_count_max:
                    working_df.drop(working_df.columns[p_val_index], axis=1, inplace=True)
                    p_val_index = p_val_index - 1
                    p_val_index += addition_factor
                    bio_counter += 1

            # Illumina Score: if not checked, the score columns will be removed
            if self.custom[2] == 0:
                bio_counter = 1
                bio_count_max = self.bio_num + 1
                score_index = 5
                addition_factor = 4
                if self.custom[3] == 0 and self.custom[1] == 0 and self.custom[0] == 0:
                    addition_factor = 1
                elif self.custom[3] == 0 and self.custom[1] == 0:
                    addition_factor = 2
                elif self.custom[3] == 0 and self.custom[0] == 0:
                    addition_factor = 2
                elif self.custom[1] == 0 and self.custom[0] == 0:
                    addition_factor = 2
                else:
                    addition_factor = 3
                while bio_counter < bio_count_max:
                    working_df.drop(working_df.columns[score_index], axis=1, inplace=True)
                    score_index = score_index - 1
                    score_index += addition_factor
                    bio_counter += 1

            # Save all the changes to final_df, this will be the version that can be saved

            return working_df
