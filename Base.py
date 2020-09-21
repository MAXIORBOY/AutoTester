import h5py
import numpy as np
from tkinter import messagebox
import sys


class Base:
    def __init__(self, file_name):
        self.file_name = file_name
        self.external_base_status = True
        try:
            self.file = h5py.File(file_name, 'r+')
        except OSError:
            try:
                self.file = h5py.File(file_name, 'x')
            except OSError:
                messagebox.showerror('Error', 'The file is inaccessible!')
                sys.exit()
            self.file.close()
            self.file = h5py.File(file_name, 'r+')
        except UnicodeEncodeError:
            messagebox.showerror('Error', 'The path to the selected file contains invalid characters!')
            self.external_base_status = False

    def remove_base(self, base_name):
        del self.file[base_name]

    def get_bases_names(self):
        return [d_set for d_set in self.file]

    def get_base_columns_name(self, base_name):
        return list(self.file[base_name].dtype.names)

    def set_base_metadata(self, base_name, metadata):
        self.file[base_name].attrs['threshold'] = metadata[0]
        self.file[base_name].attrs['default_test_questions_number'] = metadata[1]
        self.file[base_name].attrs['randomize_type'] = metadata[2]

    def get_metadata(self, base_name):
        return self.file[base_name].attrs['threshold'], self.file[base_name].attrs['default_test_questions_number'], self.file[base_name].attrs['randomize_type']

    def add_new_data_set(self, base_title, columns_names, threshold, default_test_questions_number, randomize_type):
        self.file.create_dataset(base_title, (0, ), maxshape=(None, ), compression='gzip', dtype=self.create_data_type(columns_names))
        self.set_base_metadata(base_title, (threshold, default_test_questions_number, randomize_type))

    def add_new_row(self, base_name, values):
        self.file[base_name].resize((self.file[base_name].shape[0] + 1,))
        self.file[base_name][-1] = tuple(values)

    def modify_row(self, base_name, values, index):
        self.file[base_name][index] = tuple(values)

    def remove_row(self, base_name, index):
        def copy_base():
            base_copy = []
            for i in range(len(self.file[base_name])):
                base_copy.append(self.file[base_name][i])

            return base_copy

        copy_of_base = copy_base()
        counter = 0
        for j in range(len(self.file[base_name])):
            if j != index:
                self.file[base_name][counter] = tuple(copy_of_base[j])
                counter += 1

        self.file[base_name].resize((self.file[base_name].shape[0] - 1,))

    def reset_progress(self, base_name):
        for i in range(len(self.file[base_name])):
            row = self.file[base_name][i]
            row[-1] = 0
            self.file[base_name][i] = tuple(row)

    def add_progress_point(self, base_name, row_index):
        row = self.file[base_name][row_index]
        row[-1] += 1
        self.file[base_name][row_index] = tuple(row)

    def test_check_row_correctness(self, base_name, row_index, test_row):
        column_errors_list = []
        for i in range(len(self.file[base_name][row_index]) - 1):
            if self.file[base_name][row_index][i] != test_row[i]:
                column_errors_list.append(i)

        if not len(column_errors_list):
            self.add_progress_point(base_name, row_index)

        return column_errors_list

    def test_check_all_rows_correctness(self, base_name, row_indexes, test_rows):
        all_columns_errors_matrix = []
        for i in range(len(row_indexes)):
            all_columns_errors_matrix.append(self.test_check_row_correctness(base_name, row_indexes[i], test_rows[i]))

        return test_rows, all_columns_errors_matrix

    def is_that_tuple_in_base(self, base_name, entry, ignore_row_index=None):
        result = False
        for i in range(len(self.file[base_name])):
            if i == ignore_row_index:
                continue

            if tuple(self.file[base_name][i])[:-1] == entry:
                result = True
                break

        return result

    def fill_base_with_values(self, base_name, data):
        for row in data:
            self.add_new_row(base_name, row)

    def change_base_columns_names(self, base_name, new_columns_names):
        data = self.file[base_name]
        metadata = self.get_metadata(base_name)
        self.remove_base(base_name)
        self.add_new_data_set(base_name, new_columns_names, metadata[0], metadata[1], metadata[2])
        self.fill_base_with_values(base_name, data)

    def change_base_name(self, old_base_name, new_base_name):
        columns_names = self.get_base_columns_name(old_base_name)[: -1]
        metadata = self.get_metadata(old_base_name)
        data = self.file[old_base_name]
        self.remove_base(old_base_name)
        self.add_new_data_set(new_base_name, columns_names, metadata[0], metadata[1], metadata[2])
        self.fill_base_with_values(new_base_name, data)

    def is_hdf5_file_valid(self):
        result = True
        try:
            for d_set in self.file:
                threshold, def_question_number, randomize_type = self.file[d_set].attrs['threshold'], self.file[d_set].attrs['default_test_questions_number'], self.file[d_set].attrs['randomize_type']
        except:
            result = False

        return result

    @ staticmethod
    def create_data_type(columns_names):
        d_type = []
        for i in range(len(columns_names)):
            d_type.append((columns_names[i], h5py.string_dtype(encoding='utf-8')))
        d_type.append(('Learning progress', 'i'))

        return np.dtype(d_type)
