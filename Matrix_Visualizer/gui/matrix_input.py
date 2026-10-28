import tkinter as tk
from tkinter import ttk
from matrix.operations import MatrixError, validate_matrix, validate_scalar

class MatrixInput(ttk.LabelFrame):
    MAX_SIZE = 20

    def __init__(self, parent, name):
        super().__init__(parent, text=f'Matrix {name}', padding=6)
        self.matrix_name = name
        self.row_count_variable = tk.StringVar(value='2')
        self.column_count_variable = tk.StringVar(value='2')
        self.cell_entries = []
        dimension_controls = ttk.Frame(self)
        dimension_controls.pack(fill='x')
        for dimension_label, dimension_variable in (('Rows', self.row_count_variable), ('Columns', self.column_count_variable)):
            ttk.Label(dimension_controls, text=dimension_label).pack(side='left')
            dimension_spinbox = ttk.Spinbox(dimension_controls,from_=1,to=self.MAX_SIZE,width=4,textvariable=dimension_variable,command=self.resize,)
            dimension_spinbox.pack(side='left', padx=3)
            dimension_spinbox.bind('<Return>', self.resize)
            dimension_spinbox.bind('<FocusOut>', self.resize)
        ttk.Button(dimension_controls, text='Resize', command=self.resize).pack(side='left',padx=4,)
        ttk.Button(dimension_controls, text='Clear', command=self.clear).pack(side='left')
        self.validation_message = tk.StringVar()
        ttk.Label(self, textvariable=self.validation_message, foreground='firebrick').pack(fill='x',)
        scrollable_area = ttk.Frame(self)
        scrollable_area.pack(fill='both', expand=True)
        scrollable_area.rowconfigure(0, weight=1)
        scrollable_area.columnconfigure(0, weight=1)
        self.scroll_canvas = tk.Canvas(scrollable_area, height=120, highlightthickness=0)
        self.scroll_canvas.grid(row=0, column=0, sticky='nsew')
        vertical_scrollbar = ttk.Scrollbar(scrollable_area, orient='vertical', command=self.scroll_canvas.yview)
        horizontal_scrollbar = ttk.Scrollbar(scrollable_area, orient='horizontal', command=self.scroll_canvas.xview)
        vertical_scrollbar.grid(row=0, column=1, sticky='ns')
        horizontal_scrollbar.grid(row=1, column=0, sticky='ew')
        self.scroll_canvas.configure(yscrollcommand=vertical_scrollbar.set,xscrollcommand=horizontal_scrollbar.set,)
        self.cell_grid = ttk.Frame(self.scroll_canvas)
        self.scroll_canvas.create_window((0, 0), window=self.cell_grid, anchor='nw')
        self.cell_grid.bind('<Configure>',lambda event: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox('all')),)
        self.resize()

    def resize(self, event=None):
        try:
            row_count, column_count = (int(self.row_count_variable.get()), int(self.column_count_variable.get()))
            if not (1 <= row_count <= self.MAX_SIZE and 1 <= column_count <= self.MAX_SIZE):
                raise ValueError()
        except ValueError:
            self.validation_message.set(f'Dimensions must be integers from 1 to {self.MAX_SIZE}.')
            return False
        if self.cell_entries and len(self.cell_entries) == row_count and (len(self.cell_entries[0]) == column_count):
            self.validation_message.set('')
            return True
        previous_cell_values = [[cell_entry.get() for cell_entry in entry_row] for entry_row in self.cell_entries]
        for cell_widget in self.cell_grid.winfo_children():
            cell_widget.destroy()
        self.cell_entries = []
        for row_index in range(row_count):
            entry_row = []
            for column_index in range(column_count):
                cell_entry = ttk.Entry(self.cell_grid, width=9, justify='right')
                cell_entry.grid(row=row_index, column=column_index, padx=2, pady=2)
                cell_entry.insert(0,previous_cell_values[row_index][column_index] if row_index < len(previous_cell_values) and column_index < len(previous_cell_values[row_index]) else '0')
                entry_row.append(cell_entry)
            self.cell_entries.append(entry_row)
        self.validation_message.set('')
        return True

    def get_matrix(self):
        if not self.resize():
            raise MatrixError(f'Matrix {self.matrix_name}: invalid dimensions')
        matrix = []
        for row_index, entry_row in enumerate(self.cell_entries):
            row_values = []
            for column_index, cell_entry in enumerate(entry_row):
                entered_text = cell_entry.get().strip()
                try:
                    numeric_value = float(entered_text)
                except ValueError as error:
                    raise MatrixError(f'{self.matrix_name}[{row_index + 1},{column_index + 1}]: enter a number') from error
                validate_scalar(numeric_value,f'{self.matrix_name}[{row_index + 1},{column_index + 1}]')
                row_values.append(numeric_value)
            matrix.append(row_values)
        validate_matrix(matrix, self.matrix_name)
        return matrix

    def clear(self):
        for entry_row in self.cell_entries:
            for cell_entry in entry_row:
                cell_entry.delete(0, 'end')

    def set_matrix(self, matrix):
        row_count, column_count = validate_matrix(matrix)
        if max(row_count, column_count) > self.MAX_SIZE:
            raise MatrixError('Example exceeds the input size limit')
        self.row_count_variable.set(str(row_count))
        self.column_count_variable.set(str(column_count))
        self.resize()
        for entry_row, matrix_row in zip(self.cell_entries, matrix):
            for cell_entry, cell_value in zip(entry_row, matrix_row):
                cell_entry.delete(0, 'end')
                cell_entry.insert(0, str(cell_value))
