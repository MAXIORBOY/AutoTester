import tkinter as tk
from tkinter import font, messagebox, filedialog
from Base import Base
from tkscrolledframe import ScrolledFrame
from functools import partial
import random
import os
import string as st


# Main screen
class MainWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window_title = 'Auto Tester'
        self.window.title(self.window_title)
        self.bases = Base('Saved bases.hdf5')

    def create_new_window(self):
        self.window.destroy()
        self.window = tk.Tk()
        self.window.title(self.window_title)

    def run(self):
        def button_base_name(base_name):
            return base_name

        tk.Label(self.window, text='Auto Tester', font=font.Font(family='Helvetica', size=14, weight='bold')).pack()
        tk.Label(self.window, text='', font=12).pack()

        sf = ScrolledFrame(self.window, width=530, height=400)
        sf.bind_scroll_wheel(self.window)
        sf.pack()
        inner_frame = sf.display_widget(tk.Frame)

        bases = self.bases.get_bases_names()
        for i in range(len(bases)):
            frame = tk.Frame(inner_frame)
            l_box = tk.Listbox(frame, width=40, height=1, justify=tk.CENTER, font=font.Font(family='Helvetica', size=12, weight='normal'))
            l_box.insert(0, bases[i])
            l_box.pack(side=tk.LEFT)
            tk.Button(frame, text='SELECT', bd=4, font=12, command=lambda c=i: [self.proceed_button_command(partial(button_base_name, self.bases.get_bases_names()[c]).args[0])]).pack(side=tk.LEFT)
            tk.Button(frame, text='DELETE', bd=4, font=12, command=lambda c=i: [self.confirm_base_removal(partial(button_base_name, self.bases.get_bases_names()[c]).args[0])]).pack(side=tk.LEFT)
            frame.pack()

        inner_frame.pack()

        tk.Button(self.window, text='ADD NEW BASE', bd=4, font=12, command=lambda: [self.bases.file.close(), self.window.destroy(), BaseCreator().run()]).pack()
        tk.Label(self.window, text='', font=12).pack()
        tk.Button(self.window, text='EXIT', bd=4, font=12, command=lambda: [self.bases.file.close(), self.window.destroy()]).pack()

        window_config(self.window)
        tk.mainloop()

    def proceed_button_command(self, base_name):
        self.bases.file.close()
        self.window.destroy()
        BaseExplorer(base_name).run()

    def confirm_base_removal(self, base_name):
        m_box = messagebox.showwarning('Confirmation', 'The selected base will be irretrievably deleted.\nAre you sure you want to continue?', type='yesno')
        if m_box == 'yes':
            self.bases.remove_base(base_name)
            messagebox.showinfo('Info', f'Base {base_name} has been deleted.')
            self.create_new_window()
            self.run()


# Main screen -> Adding new base
class BaseCreator:
    def __init__(self):
        self.window = tk.Tk()
        self.window_title = 'Creator'
        self.window.title(self.window_title)
        self.base_title = ''
        self.number_of_columns = 2
        self.randomize_type = 0
        self.default_test_questions_number = 10
        self.threshold = 5
        self.columns_names = []
        self.spinbox_labels = ['Number of columns', 'Threshold', 'Default number of questions']
        self.spinbox_params = [(2, 8), (1, 50), (1, 50)]
        self.radio_buttons_labels = ['Random', 'First column', 'Last column']
        self.base = Base('Saved bases.hdf5')

    def create_new_window(self):
        self.window.destroy()
        self.window = tk.Tk()
        self.window.title(self.window_title)

    def set_base_metadata(self, metadata):
        self.base_title, self.number_of_columns, self.threshold, self.default_test_questions_number, self.randomize_type = metadata

    def make_variables(self):
        variables = [tk.StringVar()]
        for i in range(4):
            variables.append(tk.IntVar())

        variables[0].set(self.base_title)
        variables[1].set(self.number_of_columns)
        variables[2].set(self.threshold)
        variables[3].set(self.default_test_questions_number)
        variables[4].set(self.randomize_type)

        return variables

    def run(self):
        tk.Label(self.window, text='Base creator: ', bd=4, font=font.Font(family='Helvetica', size=14, weight='bold')).pack()
        tk.Label(self.window, text='\n', font=12).pack()

        tk.Button(self.window, text='NEW LOCAL BASE', font=12, bd=4, command=lambda: [self.create_new_window(), self.run_local_start()]).pack()
        tk.Button(self.window, text='NEW BASE FROM FILE', font=12, bd=4, command=lambda: [self.set_path()]).pack()
        tk.Label(self.window, text='', font=12).pack()
        tk.Button(self.window, text='BACK', font=12, bd=4, command=lambda: [self.base.file.close(), self.window.destroy(), MainWindow().run()]).pack()

        window_config(self.window)
        tk.mainloop()

    def set_path(self):
        path = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select file", filetypes=(("HDF5 Files", "*.hdf5"), ("All files", "*.*")))
        filename, file_extension = os.path.splitext(path)
        if file_extension != '.hdf5':
            messagebox.showerror('Error', 'Invalid path!')
        else:
            imported_base = Base(path)
            if imported_base.external_base_status:
                if not imported_base.is_hdf5_file_valid():
                    messagebox.showerror('Error', 'Selected file is invalid!')
                    imported_base.file.close()
                else:
                    self.create_new_window()
                    self.run_import_start(imported_base)
            else:
                imported_base.file.close()

    # New local base
    def run_local_start(self):
        variables = self.make_variables()
        tk.Label(self.window, text='New local base: ', bd=4, font=font.Font(family='Helvetica', size=14, weight='bold')).pack()
        tk.Label(self.window, text='\n', font=12).pack()

        frame = tk.Frame(self.window)
        tk.Label(frame, text='Database name: ', bd=4, font=font.Font(family='Helvetica', size=14, weight='bold')).pack(side=tk.LEFT)
        entry = tk.Entry(frame, width=40, bd=4, textvariable=variables[0], font=font.Font(family='Helvetica', size=12, weight='normal'))
        entry.pack(side=tk.LEFT)
        entry.focus()
        tk.Label(frame, text='\n', font=12).pack()
        frame.pack(anchor='w')

        for i in range(len(self.spinbox_labels)):
            frame = tk.Frame(self.window)
            tk.Label(frame, text=f'{self.spinbox_labels[i]}: ', bd=4, font=font.Font(family='Helvetica', size=14, weight='bold')).pack(side=tk.LEFT)
            tk.Spinbox(frame, from_=self.spinbox_params[i][0], to=self.spinbox_params[i][1], width=5, bd=4, font=12, textvariable=variables[i + 1], state="readonly", readonlybackground='white').pack(side=tk.LEFT)
            tk.Label(frame, text='\n', font=12).pack()
            frame.pack(anchor='w')

        frame = tk.Frame(self.window)
        tk.Label(frame, text='Given column during tests: ', bd=4, font=font.Font(family='Helvetica', size=14, weight='bold')).pack(side=tk.LEFT)
        for i in range(len(self.radio_buttons_labels)):
            tk.Radiobutton(frame, text=self.radio_buttons_labels[i], font=font.Font(family='Helvetica', size=12, weight='normal'), value=i, variable=variables[-1]).pack(side=tk.LEFT)
        frame.pack(anchor='w')

        tk.Label(self.window, text='', font=12).pack()
        tk.Button(self.window, text='NEXT', font=12, bd=4, command=lambda: [self.check_base_name_correctness(variables)]).pack()
        tk.Label(self.window, text='', font=12).pack()
        tk.Button(self.window, text='BACK', font=12, bd=4, command=lambda: [self.base.file.close(), self.window.destroy(), MainWindow().run()]).pack()

        window_config(self.window)
        tk.mainloop()

    def check_base_name_correctness(self, variables):
        converted_values = prepare_variables(variables)
        if converted_values[0] == '':
            messagebox.showerror('Error', 'The name field is blank!')
        elif is_string_composed_of_whitespace(converted_values[0]):
            messagebox.showerror('Error', 'The name field consists solely of spaces!')
        elif converted_values[0] in self.base.get_bases_names():
            messagebox.showerror('Error', 'The name you entered already exists!')
        else:
            self.set_base_metadata(converted_values)
            self.create_new_window()
            self.run_local_next()

    def run_local_next(self):
        variables = []
        for i in range(self.number_of_columns):
            variables.append(tk.StringVar())

        tk.Label(self.window, text='Column names: ', bd=4, font=font.Font(family='Helvetica', size=14, weight='bold')).pack()
        tk.Label(self.window, text='', font=12).pack()

        frame = tk.Frame(self.window)
        for i in range(self.number_of_columns):
            if i == 0:
                entry = tk.Entry(frame, bd=4, textvariable=variables[i], font=font.Font(family='Helvetica', size=12, weight='normal'))
                entry.pack(side=tk.LEFT)
                entry.focus()
            else:
                tk.Entry(frame, bd=4, textvariable=variables[i], font=font.Font(family='Helvetica', size=12, weight='normal')).pack(side=tk.LEFT)
        frame.pack()

        tk.Label(self.window, text='', font=12).pack()
        tk.Button(self.window, text='CREATE', font=12, bd=4, command=lambda: [self.check_column_names_correctness(variables)]).pack()
        tk.Label(self.window, text='', font=12).pack()
        tk.Button(self.window, text='BACK', font=12, bd=4, command=lambda: [self.create_new_window(), self.run_local_start()]).pack()

        window_config(self.window)
        tk.mainloop()

    def check_column_names_correctness(self, variables):
        column_names = prepare_variables(variables)
        input_correct = True
        for i in range(len(column_names)):
            if column_names[i] == '':
                input_correct = False
                messagebox.showerror('Error', 'One of the fields is blank!')
                break
            elif is_string_composed_of_whitespace(column_names[i]):
                input_correct = False
                messagebox.showerror('Error', 'One of the fields consists solely of spaces!')
                break
            elif column_names.count(column_names[i]) > 1:
                input_correct = False
                messagebox.showerror('Error', 'The column names must be unique!')
                break
        if input_correct:
            self.columns_names = column_names
            self.base.add_new_data_set(self.base_title, self.columns_names, self.threshold, self.default_test_questions_number, self.randomize_type)
            messagebox.showinfo('Info', f'Base {self.base_title} has been created.')
            self.base.file.close()
            self.window.destroy()
            MainWindow().run()

    # New imported base
    def run_import_start(self, imported_base):
        def button_base_name(base_name):
            return base_name

        tk.Label(self.window, text='Base importer: ', font=font.Font(family='Helvetica', size=14, weight='bold')).pack()
        tk.Label(self.window, text='', font=12).pack()

        sf = ScrolledFrame(self.window, width=520, height=400)
        sf.bind_scroll_wheel(self.window)
        sf.pack()
        inner_frame = sf.display_widget(tk.Frame)

        bases = imported_base.get_bases_names()
        for i in range(len(bases)):
            frame = tk.Frame(inner_frame)
            l_box = tk.Listbox(frame, width=40, height=1, justify=tk.CENTER, font=font.Font(family='Helvetica', size=12, weight='normal'))
            l_box.insert(0, bases[i])
            l_box.pack(side=tk.LEFT)
            tk.Button(frame, text='IMPORT', bd=4, font=12, command=lambda c=i: [self.import_button_command(partial(button_base_name, bases[c]).args[0], imported_base)]).pack(side=tk.LEFT)
            frame.pack()

        inner_frame.pack()

        tk.Button(self.window, text='BACK', bd=4, font=12, command=lambda: [imported_base.file.close(), self.create_new_window(), self.run()]).pack()

        window_config(self.window)
        tk.mainloop()

    def import_button_command(self, imported_base_name, imported_base):
        if imported_base_name in self.base.get_bases_names():
            messagebox.showerror('Error', 'The name of this base already exists in your file!')
        else:
            columns_names = imported_base.get_base_columns_name(imported_base_name)[: -1]
            threshold, default_test_questions_number, randomize_type = imported_base.get_metadata(imported_base_name)
            data = imported_base.file[imported_base_name]
            self.base.add_new_data_set(imported_base_name, columns_names, threshold, default_test_questions_number, randomize_type)
            self.base.fill_base_with_values(imported_base_name, data)
            self.base.reset_progress(imported_base_name)
            messagebox.showinfo('Info', f'Base {imported_base_name} has been imported.')


# Main screen -> Selected base
class BaseExplorer:
    def __init__(self, title):
        self.title = title
        self.window = tk.Tk()
        self.window.title(self.title)
        self.base = Base('Saved bases.hdf5')

    def create_new_window(self):
        self.window.destroy()
        self.window = tk.Tk()
        self.window.title(self.title)

    def make_base_header(self, frame):
        columns_names = self.base.get_base_columns_name(self.title)
        for i in range(len(columns_names)):
            if i < len(columns_names) - 1:
                l_box = tk.Listbox(frame, bg=self.window['bg'], width=30, height=1, justify=tk.CENTER, font=font.Font(family='Helvetica', size=12, weight='bold'))
            else:
                l_box = tk.Listbox(frame, bg=self.window['bg'], width=18, height=1, justify=tk.CENTER, font=font.Font(family='Helvetica', size=12, weight='bold'))
            l_box.insert(0, columns_names[i])
            l_box.pack(side=tk.LEFT)
        frame.pack(fill=tk.X)

    def calculate_window_width(self):
        width = int(305 + 274 * (len(self.base.get_base_columns_name(self.title)) - 1))
        if width > self.window.winfo_screenwidth():
            width = self.window.winfo_screenwidth()
        return width

    def run(self):
        def get_button_index(index):
            return index

        tk.Label(self.window, text=self.title, bd=4, font=font.Font(family='Helvetica', size=14, weight='bold')).pack()
        tk.Label(self.window, text='', font=12).pack()

        sf = ScrolledFrame(self.window, width=self.calculate_window_width(), height=335)
        sf.bind_scroll_wheel(self.window)
        sf.pack()
        inner_frame = sf.display_widget(tk.Frame)

        self.make_base_header(tk.Frame(inner_frame))
        for i in range(len(self.base.file[self.title])):
            frame = tk.Frame(inner_frame)
            for j in range(len(self.base.file[self.title][i])):
                if j < len(self.base.file[self.title][i]) - 1:
                    l_box = tk.Listbox(frame, width=30, height=1, justify=tk.CENTER, font=font.Font(family='Helvetica', size=12, weight='normal'))
                    l_box.insert(0, self.base.file[self.title][i][j])
                else:
                    l_box = tk.Listbox(frame, width=18, height=1, justify=tk.CENTER, font=font.Font(family='Helvetica', size=12, weight='normal'))
                    l_box.insert(0, f"{self.base.file[self.title][i][j]}/{self.base.file[self.title].attrs['threshold']}")
                l_box.pack(side=tk.LEFT)
            tk.Button(frame, text='EDIT', font=10, bd=4, command=lambda c=i: [self.base.file.close(), self.window.destroy(), BaseModifier(self.title, partial(get_button_index, c).args[0]).run()]).pack(side=tk.LEFT)
            tk.Button(frame, text='DELETE', font=10, bd=4, command=lambda c=i: [self.confirm_row_remove(partial(get_button_index, c).args[0])]).pack(side=tk.LEFT)
            frame.pack()

        tk.Label(self.window, text=f"Rows: {len(self.base.file[self.title])}", bd=4, font=font.Font(family='Helvetica', size=12, weight='normal')).pack(anchor='w')

        tk.Button(self.window, text='START TESTING', font=12, bd=4, command=lambda: [self.base.file.close(), self.window.destroy(), Testing(self.title).run_start()]).pack()
        tk.Button(self.window, text='ADD NEW ROW', font=12, bd=4, command=lambda: [self.base.file.close(), self.window.destroy(), BaseModifier(self.title).run()]).pack()
        tk.Button(self.window, text='SETTINGS', font=12, bd=4, command=lambda: [self.base.file.close(), self.window.destroy(), Settings(self.title).run()]).pack()
        tk.Label(self.window, text='', font=12).pack()
        tk.Button(self.window, text='BACK', font=12, bd=4, command=lambda: [self.base.file.close(), self.window.destroy(), MainWindow().run()]).pack()

        window_config(self.window)
        tk.mainloop()

    def confirm_row_remove(self, index):
        m_box = messagebox.showwarning('Confirmation', 'The selected row will be removed from this base.\nAre you sure you want to continue?', type='yesno')
        if m_box == 'yes':
            self.base.remove_row(self.title, index)
            self.create_new_window()
            self.run()


# Main screen -> Selected base -> New row / Edit row
class BaseModifier:
    def __init__(self, title, index=None):
        self.window = tk.Tk()
        self.title = title
        self.window_title = f'{self.title} - Editor'
        self.window.title(self.window_title)
        self.base = Base('Saved bases.hdf5')
        self.index = index

    def create_new_window(self):
        self.window.destroy()
        self.window = tk.Tk()
        self.window.title(self.window_title)

    def make_base_header(self, frame):
        columns_names = self.base.get_base_columns_name(self.title)
        for i in range(len(columns_names) - 1):
            l_box = tk.Listbox(frame, bg=self.window['bg'], width=30, height=1, justify=tk.CENTER, font=font.Font(family='Helvetica', size=12, weight='bold'))
            l_box.insert(0, columns_names[i])
            l_box.pack(side=tk.LEFT)
        frame.pack(fill=tk.X)

    def run(self):
        if self.index is None:
            label_text = 'Row creator'
        else:
            label_text = 'Row editor'

        tk.Label(self.window, text=label_text, bd=4, font=font.Font(family='Helvetica', size=14, weight='bold')).pack()
        tk.Label(self.window, text='', font=12).pack()

        columns_names = self.base.get_base_columns_name(self.title)
        values = []
        for _ in range(len(columns_names) - 1):
            values.append(tk.StringVar())
        values.append(tk.IntVar())

        if self.index is not None:
            for i in range(len(columns_names) - 1):
                values[i].set(self.base.file[self.title][self.index][i])
            values[-1].set(self.base.file[self.title][self.index][-1])

        self.make_base_header(tk.Frame(self.window))

        frame = tk.Frame(self.window)
        for i in range(len(columns_names) - 1):
            if i == 0:
                entry = tk.Entry(frame, width=30, bd=1, textvariable=values[i], font=font.Font(family='Helvetica', size=12, weight='normal'))
                entry.pack(side=tk.LEFT)
                entry.focus()
            else:
                tk.Entry(frame, width=30, bd=1, textvariable=values[i], font=font.Font(family='Helvetica', size=12, weight='normal')).pack(side=tk.LEFT)
        frame.pack()

        tk.Label(self.window, text='', font=12).pack()
        if self.index is None:
            button = tk.Button(self.window, text='ADD', bd=4, font=12, command=lambda: [self.check_input_correctness(values)])
            button.pack()
        else:
            button = tk.Button(self.window, text='EDIT', bd=4, font=12, command=lambda: [self.check_input_correctness(values, index=self.index)])
            button.pack()
        tk.Label(self.window, text='', font=12).pack()
        tk.Button(self.window, text='BACK', bd=4, font=12, command=lambda: [self.base.file.close(), self.window.destroy(), BaseExplorer(self.title).run()]).pack()

        self.window.bind('<Return>', lambda event=None: button.invoke())
        window_config(self.window)
        tk.mainloop()

    def check_input_correctness(self, user_input, index=None):
        fields = prepare_variables(user_input)
        input_correct = True
        for i in range(len(fields) - 1):
            if fields[i] == '':
                input_correct = False
                messagebox.showerror('Error', 'One of the fields is blank!')
                break
            elif is_string_composed_of_whitespace(fields[i]):
                input_correct = False
                messagebox.showerror('Error', 'One of the fields consists solely of spaces!')
                break
            elif self.base.is_that_tuple_in_base(self.title, tuple(fields[:-1]), ignore_row_index=index):
                input_correct = False
                messagebox.showerror('Error', 'The exact same row already exists in the base!')
                break

        if input_correct:
            if index is None:
                self.base.add_new_row(self.title, fields)
                messagebox.showinfo('Info', 'New row has been added.')
                self.create_new_window()
                self.run()
            else:
                self.base.modify_row(self.title, fields, self.index)
                messagebox.showinfo('Info', 'The row has been edited.')
                self.base.file.close()
                self.window.destroy()
                BaseExplorer(self.title).run()


# Main screen -> Selected base -> Settings
class Settings:
    def __init__(self, base_name):
        self.window = tk.Tk()
        self.window_title = 'Settings'
        self.window.title(self.window_title)
        self.base_name = base_name
        self.base = Base('Saved bases.hdf5')
        self.spinbox_labels = ['Threshold', 'Default number of questions']
        self.spinbox_params = [(1, 50), (1, 50)]
        self.radio_buttons_labels = ['Random', 'First column', 'Last column']
        self.randomize_type = self.base.file[self.base_name].attrs['randomize_type']
        self.default_test_questions_number = self.base.file[self.base_name].attrs['default_test_questions_number']
        self.threshold = self.base.file[self.base_name].attrs['threshold']

    def create_new_window(self):
        self.window.destroy()
        self.window = tk.Tk()
        self.window.title(self.window_title)

    def prepare_variables(self):
        variables = []
        for i in range(3):
            variables.append(tk.IntVar())

        variables[0].set(self.threshold)
        variables[1].set(self.default_test_questions_number)
        variables[2].set(self.randomize_type)

        return variables

    def run(self):
        def prepare_values(values):
            for j in range(len(values)):
                values[j] = values[j].get()

            return values

        variables = self.prepare_variables()

        tk.Label(self.window, text='Settings: ', bd=4, font=font.Font(family='Helvetica', size=14, weight='bold')).pack()
        tk.Label(self.window, text='\n', font=12).pack()

        for i in range(len(self.spinbox_labels)):
            frame = tk.Frame(self.window)
            tk.Label(frame, text=self.spinbox_labels[i] + ': ', bd=4, font=font.Font(family='Helvetica', size=14, weight='bold')).pack(side=tk.LEFT)
            tk.Spinbox(frame, from_=self.spinbox_params[i][0], to=self.spinbox_params[i][1], width=5, bd=4, font=12, textvariable=variables[i], state="readonly", readonlybackground='white').pack(side=tk.LEFT)
            tk.Label(frame, text='\n', font=12).pack()
            frame.pack(anchor='w')

        frame = tk.Frame(self.window)
        tk.Label(frame, text='Given columns in tests: ', bd=4, font=font.Font(family='Helvetica', size=14, weight='bold')).pack(side=tk.LEFT)
        for i in range(len(self.radio_buttons_labels)):
            tk.Radiobutton(frame, text=self.radio_buttons_labels[i], font=font.Font(family='Helvetica', size=12, weight='normal'), value=i, variable=variables[-1]).pack(side=tk.LEFT)
        frame.pack(anchor='w')

        tk.Label(self.window, text='', font=12).pack()
        tk.Button(self.window, text='CONFIRM', font=12, bd=4, command=lambda: [self.base.set_base_metadata(self.base_name, prepare_values(variables)), messagebox.showinfo("Info", 'The settings have been changed.')]).pack()
        tk.Label(self.window, text='', font=12).pack()
        tk.Button(self.window, text='EDIT NAMES', bd=4, font=12, command=lambda: [self.create_new_window(), self.run_edit()]).pack()
        tk.Button(self.window, text='RESET PROGRESS', font=12, bd=4, command=lambda: [self.confirm_reset_progress()]).pack()
        tk.Label(self.window, text='', font=12).pack()
        tk.Button(self.window, text='BACK', font=12, bd=4, command=lambda: [self.base.file.close(), self.window.destroy(), BaseExplorer(self.base_name).run()]).pack()

        window_config(self.window)
        tk.mainloop()

    def confirm_reset_progress(self):
        m_box = messagebox.showwarning('Confirmation', 'The learning progress of all entries in this base will be reset to zero.\nAre you sure you want to continue?', type='yesno')
        if m_box == 'yes':
            self.base.reset_progress(self.base_name)
            messagebox.showinfo('Info', 'The learning progress has been reset.')

    def run_edit(self):
        tk.Label(self.window, text='Edit names: ', bd=4, font=font.Font(family='Helvetica', size=14, weight='bold')).pack()
        tk.Label(self.window, text='\n', font=12).pack()

        tk.Button(self.window, text='EDIT COLUMN NAMES', bd=4, font=12, command=lambda: [self.create_new_window(), self.run_edit_columns_names()]).pack()
        tk.Button(self.window, text='EDIT DATABASE NAME', bd=4, font=12, command=lambda: [self.create_new_window(), self.run_edit_base_name()]).pack()
        tk.Label(self.window, text='', font=12).pack()
        tk.Button(self.window, text='BACK', font=12, bd=4, command=lambda: [self.create_new_window(), self.run()]).pack()

        window_config(self.window)
        tk.mainloop()

    def run_edit_columns_names(self):
        variables = []
        columns_names = self.base.get_base_columns_name(self.base_name)[: -1]
        for i in range(len(columns_names)):
            variables.append(tk.StringVar())
            variables[i].set(columns_names[i])

        tk.Label(self.window, text='Edit column names ', bd=4, font=font.Font(family='Helvetica', size=14, weight='bold')).pack()
        tk.Label(self.window, text='\n', font=12).pack()

        frame = tk.Frame(self.window)
        for i in range(len(columns_names)):
            if i == 0:
                entry = tk.Entry(frame, bd=4, textvariable=variables[i], font=font.Font(family='Helvetica', size=12, weight='normal'))
                entry.pack(side=tk.LEFT)
                entry.focus()
            else:
                tk.Entry(frame, bd=4, textvariable=variables[i], font=font.Font(family='Helvetica', size=12, weight='normal')).pack(side=tk.LEFT)
        frame.pack()

        tk.Button(self.window, text='EDIT', font=12, bd=4, command=lambda: [self.check_column_names_correctness(variables)]).pack()
        tk.Label(self.window, text='', font=12).pack()
        tk.Button(self.window, text='BACK', font=12, bd=4, command=lambda: [self.create_new_window(), self.run_edit()]).pack()

        window_config(self.window)
        tk.mainloop()

    def check_column_names_correctness(self, variables):
        column_names = prepare_variables(variables)
        input_correct = True
        for i in range(len(column_names)):
            if column_names[i] == '':
                input_correct = False
                messagebox.showerror('Error', 'One of the fields is blank')
                break
            elif is_string_composed_of_whitespace(column_names[i]):
                input_correct = False
                messagebox.showerror('Error', 'One of the fields consists solely of spaces!')
                break
            elif column_names.count(column_names[i]) > 1:
                input_correct = False
                messagebox.showerror('Error', 'The column names must be unique!')
                break
        if input_correct:
            self.base.change_base_columns_names(self.base_name, column_names)
            messagebox.showinfo('Info', 'The column names have been changed.')
            self.create_new_window()
            self.run_edit()

    def run_edit_base_name(self):
        variable = tk.StringVar()
        variable.set(self.base_name)
        tk.Label(self.window, text='Edit database name: ', bd=4, font=font.Font(family='Helvetica', size=14, weight='bold')).pack()
        tk.Label(self.window, text='\n', font=12).pack()

        frame = tk.Frame(self.window)
        tk.Label(frame, text='Database name: ', bd=4, font=font.Font(family='Helvetica', size=14, weight='bold')).pack(side=tk.LEFT)
        entry = tk.Entry(frame, width=40, bd=4, textvariable=variable, font=font.Font(family='Helvetica', size=12, weight='normal'))
        entry.pack(side=tk.LEFT)
        entry.focus()
        tk.Label(frame, text='\n', font=12).pack()
        frame.pack(anchor='w')

        tk.Button(self.window, text='EDIT', font=12, bd=4, command=lambda: [self.check_base_name_correctness(variable)]).pack()
        tk.Label(self.window, text='', font=12).pack()
        tk.Button(self.window, text='BACK', font=12, bd=4, command=lambda: [self.create_new_window(), self.run_edit()]).pack()

        window_config(self.window)
        tk.mainloop()

    def check_base_name_correctness(self, new_base_name):
        base_name = new_base_name.get()
        if base_name == '':
            messagebox.showerror('Error', 'The name field is blank!')
        elif is_string_composed_of_whitespace(base_name):
            messagebox.showerror('Error', 'The name field consists solely of spaces!')
        elif base_name in self.base.get_bases_names():
            messagebox.showerror('Error', 'The name you entered already exists!')
        else:
            self.base.change_base_name(self.base_name, base_name)
            self.base_name = base_name
            messagebox.showinfo('Info', 'The name of the database has been changed.')
            self.create_new_window()
            self.run_edit()


# Main screen -> Selected base -> Start test
class Testing:
    def __init__(self, base_name):
        self.window = tk.Tk()
        self.window_title = 'Tester'
        self.window.title(self.window_title)
        self.base_name = base_name
        self.base = Base('Saved bases.hdf5')
        self.randomize_type = self.base.file[self.base_name].attrs['randomize_type']
        self.default_number_of_questions = self.base.file[self.base_name].attrs['default_test_questions_number']
        self.threshold = self.base.file[self.base_name].attrs['threshold']
        self.valid_row_indexes = []
        self.possible_number_of_questions, self.not_enough_questions = self.determine_number_of_questions()
        self.number_of_questions = 1
        self.generated_row_indexes = []
        self.generated_column_indexes = []

    def determine_number_of_questions(self):
        valid_rows = 0
        for i in range(len(self.base.file[self.base_name])):
            if self.base.file[self.base_name][i][-1] < self.threshold:
                self.valid_row_indexes.append(i)
                valid_rows += 1
        if valid_rows < self.default_number_of_questions:
            return valid_rows, True
        else:
            return valid_rows, False

    def error_message(self, message):
        m_box = messagebox.showerror("Error", message)
        if m_box == 'ok':
            self.window.destroy()
            BaseExplorer(self.base_name).run()

    def create_new_window(self):
        self.window.destroy()
        self.window = tk.Tk()
        self.window.title(self.window_title)

    def run_start(self):
        tk.Label(self.window, text='Test', bd=4, font=font.Font(family='Helvetica', size=14, weight='bold')).pack()
        tk.Label(self.window, text='\n', font=12).pack()

        if self.possible_number_of_questions:
            value = tk.IntVar()
            if not self.not_enough_questions:
                value.set(self.default_number_of_questions)
            else:
                value.set(self.possible_number_of_questions)

            frame = tk.Frame(self.window)
            tk.Label(frame, text='Number of questions: ', bd=4, font=font.Font(family='Helvetica', size=14, weight='bold')).pack(side=tk.LEFT)
            tk.Spinbox(frame, from_=1, to=self.possible_number_of_questions, width=5, bd=4, font=12, textvariable=value, state="readonly", readonlybackground='white').pack(side=tk.LEFT)
            tk.Label(frame, text='\n', font=12).pack()
            frame.pack(anchor='w')

            tk.Label(self.window, text='', font=12).pack()
            tk.Button(self.window, text='START', font=12, bd=4, command=lambda: [self.set_generated_variables(value.get()), self.create_new_window(), self.run_main()]).pack()
            tk.Label(self.window, text='', font=12).pack()
            tk.Button(self.window, text='BACK', font=12, bd=4, command=lambda: [self.base.file.close(), self.window.destroy(), BaseExplorer(self.base_name).run()]).pack()

            window_config(self.window)
            tk.mainloop()
        else:
            window_config(self.window)
            self.error_message('In the base there are no valid rows in order to start the test.\nAdd new rows to the base, increase the threshold or reset your progress.')

    def make_base_header(self, frame):
        columns_names = self.base.get_base_columns_name(self.base_name)
        for i in range(len(columns_names) - 1):
            l_box = tk.Listbox(frame, bg=self.window['bg'], width=30, height=1, justify=tk.CENTER, font=font.Font(family='Helvetica', size=12, weight='bold'))
            l_box.insert(0, columns_names[i])
            l_box.pack(side=tk.LEFT)
        frame.pack()

    def calculate_window_width(self):
        width = int(274 * (len(self.base.get_base_columns_name(self.base_name)) - 1))
        if width > self.window.winfo_screenwidth():
            width = self.window.winfo_screenwidth()
        return width

    def set_generated_variables(self, number_of_questions):
        self.number_of_questions = number_of_questions
        self.generated_row_indexes = random.sample(self.valid_row_indexes, self.number_of_questions)
        if self.randomize_type == 0:
            self.generated_column_indexes = []
            for i in range(self.number_of_questions):
                self.generated_column_indexes.append(random.choice(range(len(self.base.file[self.base_name].dtype) - 1)))
        elif self.randomize_type == 1:
            self.generated_column_indexes = [0] * self.number_of_questions
        else:
            self.generated_column_indexes = [len(self.base.file[self.base_name].dtype) - 2] * self.number_of_questions

    def run_main(self):
        def make_variables():
            variables = []
            for i in range(self.number_of_questions):
                row = []
                for j in range(len(self.base.file[self.base_name].dtype) - 1):
                    if j != self.generated_column_indexes[i]:
                        row.append(tk.StringVar())
                    else:
                        value = tk.StringVar()
                        value.set(self.base.file[self.base_name][self.generated_row_indexes[i]][j])
                        row.append(value)
                variables.append(row)

            return variables

        tk.Label(self.window, text=f'{self.base_name} - Test', bd=4, font=font.Font(family='Helvetica', size=14, weight='bold')).pack()
        tk.Label(self.window, text='\n', font=12).pack()

        values = make_variables()

        sf = ScrolledFrame(self.window, width=self.calculate_window_width(), height=400)
        sf.bind_scroll_wheel(self.window)
        sf.bind_arrow_keys(self.window)
        sf.pack()
        inner_frame = sf.display_widget(tk.Frame)

        self.make_base_header(tk.Frame(inner_frame))
        is_first_entry_focused = False

        for m in range(len(values)):
            frame = tk.Frame(inner_frame)
            for n in range(len(values[m])):
                if self.generated_column_indexes[m] != n:
                    if not is_first_entry_focused:
                        entry = tk.Entry(frame, width=30, bd=1, textvariable=values[m][n], font=font.Font(family='Helvetica', size=12, weight='normal'))
                        entry.pack(side=tk.LEFT)
                        entry.focus()
                        is_first_entry_focused = True
                    else:
                        tk.Entry(frame, width=30, bd=1, textvariable=values[m][n], font=font.Font(family='Helvetica', size=12, weight='normal')).pack(side=tk.LEFT)
                else:
                    l_box = tk.Listbox(frame, bg=self.window['bg'], width=30, height=1, justify=tk.CENTER, font=font.Font(family='Helvetica', size=12, weight='normal'))
                    l_box.insert(0, values[m][n].get())
                    l_box.pack(side=tk.LEFT)
            frame.pack()

        tk.Label(self.window, text='', font=12).pack()
        tk.Button(self.window, text='CHECK', font=12, bd=4, command=lambda: [self.accept_user_input(values)]).pack()
        tk.Label(self.window, text='', font=12).pack()
        tk.Button(self.window, text='ABORT', font=12, bd=4, command=lambda: [self.base.file.close(), self.window.destroy(), BaseExplorer(self.base_name).run()]).pack()

        window_config(self.window)
        tk.mainloop()

    def accept_user_input(self, user_input):
        def prepare_values(user_input):
            return [prepare_variables(row) for row in user_input]

        def check_user_input(values):
            all_fields_are_filled = True
            for i in range(len(values)):
                for j in range(len(values[i])):
                    if values[i][j] == '' or is_string_composed_of_whitespace(values[i][j]):
                        all_fields_are_filled = False
                        break

                if not all_fields_are_filled:
                    break

            return all_fields_are_filled

        values = prepare_values(user_input)
        input_flag = check_user_input(values)

        if not input_flag:
            m_box = messagebox.showwarning('Warning', 'Some fields are not filled. Are you sure you want to continue?', type='yesno')

        if input_flag or m_box == 'yes':
            self.create_new_window()
            self.run_result(self.base.test_check_all_rows_correctness(self.base_name, self.generated_row_indexes, values))

    def run_result(self, user_input_and_results):
        user_input, errors_matrix = user_input_and_results
        tk.Label(self.window, text=f'{self.base_name} - Result', bd=4, font=font.Font(family='Helvetica', size=14, weight='bold')).pack()
        tk.Label(self.window, text='\n', font=12).pack()

        sf = ScrolledFrame(self.window, width=self.calculate_window_width(), height=400)
        sf.bind_scroll_wheel(self.window)
        sf.pack()
        inner_frame = sf.display_widget(tk.Frame)

        self.make_base_header(tk.Frame(inner_frame))
        questions = self.number_of_questions * (len(self.base.file[self.base_name].dtype) - 2)
        good_rows = self.calculate_correct_rows_amount(errors_matrix)
        good_answers = 0

        for i in range(len(user_input)):
            frame = tk.Frame(inner_frame)
            for j in range(len(user_input[i])):
                if j != self.generated_column_indexes[i]:
                    l_box = tk.Listbox(frame, width=30, height=2, justify=tk.CENTER, font=font.Font(family='Helvetica', size=12, weight='normal'))
                    l_box.insert(0, user_input[i][j])
                    l_box.insert(1, self.base.file[self.base_name][self.generated_row_indexes[i]][j])
                    if j in errors_matrix[i]:
                        l_box.itemconfig(0, {'fg': 'red'})
                    else:
                        l_box.itemconfig(0, {'fg': 'green'})
                        good_answers += 1
                    l_box.pack(side=tk.LEFT)
                else:
                    l_box = tk.Listbox(frame, bg=self.window['bg'], width=30, height=2, justify=tk.CENTER, font=font.Font(family='Helvetica', size=12, weight='normal'))
                    l_box.insert(0, self.base.file[self.base_name][self.generated_row_indexes[i]][j])
                    l_box.pack(side=tk.LEFT)
            frame.pack()

        tk.Button(self.window, text='FINISH', font=12, bd=4, command=lambda: [self.base.file.close(), self.window.destroy(), BaseExplorer(self.base_name).run()]).pack()
        window_config(self.window)
        messagebox.showinfo("Result", self.prepare_string_for_result_messagebox(questions, good_answers, good_rows, self.number_of_questions))
        tk.mainloop()

    @staticmethod
    def calculate_correct_rows_amount(errors_matrix):
        correct_rows = 0
        for i in range(len(errors_matrix)):
            if not len(errors_matrix[i]):
                correct_rows += 1

        return correct_rows

    @staticmethod
    def prepare_string_for_result_messagebox(questions, good_answers, good_rows, total_rows):
        return f'Correct answers: {good_answers} / {questions} ({round(100 * good_answers / questions, 2)}%\nCorrect rows: {good_rows} / {total_rows} ({round(100 * good_rows / total_rows, 2)}%)'


def prepare_variables(variables_list):
    return [variable.get() for variable in variables_list]


def is_string_composed_of_whitespace(string):
    return all([char in st.whitespace for char in string])


def window_config(window, width_adjuster=0.85, height_adjuster=0.55):
    window.attributes('-topmost', 1)
    window.attributes('-topmost', 0)
    window.focus_force()
    window.update()
    window.geometry('%dx%d+%d+%d' % (window.winfo_width(), window.winfo_height(), width_adjuster * ((window.winfo_screenwidth() / 2) - (window.winfo_width() / 2)), height_adjuster * ((window.winfo_screenheight() / 2) - (window.winfo_height() / 2))))
