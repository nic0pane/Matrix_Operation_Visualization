import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matrix.operations import MatrixError, matrix_shape, matrix_to_str, validate_scalar
from .matrix_input import MatrixInput
from .controller import OPERATIONS, BINARY, execute
from visualization.transformations import (plot_message,plot_transformation,plot_determinant,plot_eigenvectors,)

class MatrixApplication(ttk.Frame):

    def __init__(self, root):
        super().__init__(root, padding=8)
        self.pack(fill='both', expand=True)
        root.title('Matrix Visualizer')
        root.geometry('1250x850')
        root.minsize(850, 650)
        self.calculation_steps = []
        self.current_step_index = 0
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(3, weight=3)
        self._create_matrix_inputs()
        self._create_operation_controls()
        self._create_output_and_visualization()

    @staticmethod
    def make_text(parent):
        text_widget = ScrolledText(parent, wrap='none', font='TkFixedFont', width=38, height=12)
        text_widget.pack(fill='both', expand=True)
        text_widget.configure(state='disabled')
        return text_widget

    @staticmethod
    def set_text(widget, text):
        widget.configure(state='normal')
        widget.delete('1.0', 'end')
        widget.insert('1.0', text)
        widget.configure(state='disabled')

    def update_controls(self, event=None):
        requires_two_matrices = self.operation_variable.get() in BINARY
        self.matrix_target_dropdown.configure(
            state='disabled' if requires_two_matrices else 'readonly',
        )
        self.scalar_input.configure(
            state='normal' if self.operation_variable.get() == 'Scalar multiplication' else 'disabled',
        )

    def clear_inputs(self):
        for matrix_input in self.matrix_inputs.values():
            matrix_input.clear()
        self.status_message.set(
            'Entries cleared. Blank entries must be filled before calculating.',
        )

    def read_scalar(self):
        try:
            scalar_value = float(self.scalar_variable.get().strip())
        except ValueError as error:
            raise MatrixError('Scalar must be a finite real number') from error
        return validate_scalar(scalar_value)

    def calculate(self):
        self.calculation_steps = []
        self.current_step_index = 0
        try:
            calculation_outcome = execute(
                self.operation_variable.get(),
                self.selected_matrix_variable.get(),
                lambda matrix_name: self.matrix_inputs[matrix_name].get_matrix(),self.read_scalar,)

        except (MatrixError, ValueError, ArithmeticError, np.linalg.LinAlgError) as error:
            self.status_message.set(f'Error: {error}')
            self.set_text(self.result_text_widget, f'Calculation failed:\n{error}')
            self.show_step()
            plot_message(self.plot_figure, 'No plot: correct the input and calculate again.')
            self.plot_canvas.draw_idle()
            return
        self.status_message.set('')
        self.calculation_steps = calculation_outcome.steps
        self.show_step()
        self.set_text(self.result_text_widget,f'{self.operation_variable.get()}\n\n{calculation_outcome.text}\n\n{calculation_outcome.explanation}',)

        # Plotting errors must not hide a valid numerical result.
        try:
            self.draw_outcome(calculation_outcome)
        except (ValueError, ArithmeticError, np.linalg.LinAlgError) as error:
            plot_message(self.plot_figure,f'Numerical result available.\nPlot unavailable: {error}',)
            self.status_message.set(f'Plot unavailable: {error}')
        self.plot_canvas.draw_idle()

    def draw_outcome(self, result):
        if result.plot_kind == 'message':
            plot_message(self.plot_figure,'Row operations are algebraic, not a geometric animation.\nSee Calculation steps and use Previous / Next.',)
        
        elif matrix_shape(result.matrix) != (2, 2):
            plot_message(self.plot_figure,'Numerical result is available.\nGeometric visualization is supported only for 2x2 matrices.',)

        elif result.plot_kind == 'eigen':
            plot_eigenvectors(self.plot_figure, result.matrix, *result.eigen)

        elif result.plot_kind == 'determinant':
            plot_determinant(self.plot_figure, result.matrix, result.determinant)

        else:
            plot_title = '(AB)v = A(Bv): gray original; purple after B; blue after A' if result.intermediate is not None else self.operation_variable.get()
            plot_transformation(self.plot_figure,result.matrix,plot_title,result.intermediate,)

    def move_step(self, amount):
        if self.calculation_steps:
            self.current_step_index = max(0, min(len(self.calculation_steps) - 1, self.current_step_index + amount))
        self.show_step()

    def show_step(self):
        if self.calculation_steps:
            current_step = self.calculation_steps[self.current_step_index]
            self.step_counter_text.set(f'{self.current_step_index + 1} / {len(self.calculation_steps)}')
            self.set_text(self.step_text_widget,current_step.description + '\n\n' + matrix_to_str(current_step.matrix),)

        else:
            self.step_counter_text.set('No steps')
            self.set_text(self.step_text_widget,'No recorded calculation steps for the current result.',)
        self.previous_step_button.configure(state='normal' if self.calculation_steps and self.current_step_index > 0 else 'disabled',)
        self.next_step_button.configure(state='normal' if self.calculation_steps and self.current_step_index < len(self.calculation_steps) - 1 else 'disabled',)

    def _create_matrix_inputs(self):
        matrix_input_panel = ttk.Panedwindow(self, orient='horizontal')
        matrix_input_panel.grid(row=0, column=0, sticky='nsew')
        self.matrix_inputs = {matrix_name: MatrixInput(matrix_input_panel, matrix_name) for matrix_name in ('A', 'B')}
        for matrix_input in self.matrix_inputs.values():
            matrix_input_panel.add(matrix_input, weight=1)

    def _create_operation_controls(self):
        operation_controls = ttk.LabelFrame(self, text='Operation', padding=6)
        operation_controls.grid(row=1, column=0, sticky='ew', pady=6)
        operation_controls.columnconfigure(1, weight=1)
        self.operation_variable = tk.StringVar(value=OPERATIONS[0])
        ttk.Label(operation_controls, text='Calculate').grid(row=0, column=0, padx=4)
        operation_dropdown = ttk.Combobox(operation_controls,textvariable=self.operation_variable,values=OPERATIONS,state='readonly',width=30,)
        operation_dropdown.grid(row=0, column=1, sticky='ew')
        operation_dropdown.bind('<<ComboboxSelected>>', self.update_controls)
        ttk.Label(operation_controls, text='Single-matrix target:').grid(row=0,column=2,padx=4,)
        self.selected_matrix_variable = tk.StringVar(value='A')
        self.matrix_target_dropdown = ttk.Combobox(operation_controls,textvariable=self.selected_matrix_variable,values=('A', 'B'),state='readonly',width=3,)
        self.matrix_target_dropdown.grid(row=0, column=3)
        ttk.Label(operation_controls, text='Scalar:').grid(row=0, column=4, padx=4)
        self.scalar_variable = tk.StringVar(value='2')
        self.scalar_input = ttk.Entry(operation_controls, textvariable=self.scalar_variable, width=10)
        self.scalar_input.grid(row=0, column=5)
        ttk.Button(operation_controls, text='Calculate', command=self.calculate).grid(row=0,column=6,padx=6,)
        ttk.Button(operation_controls, text='Clear both', command=self.clear_inputs).grid(row=0,column=8,columnspan=2,sticky='ew', pady=3, padx=6,)
        self.status_message = tk.StringVar(value='Choose an operation, then Calculate.')
        ttk.Label(self,textvariable=self.status_message,foreground='firebrick',wraplength=1100,).grid(row=2,column=0,sticky='ew',pady=3,)

    def _create_output_and_visualization(self):
        output_panel = ttk.Panedwindow(self, orient='horizontal')
        output_panel.grid(row=3, column=0, sticky='nsew')
        result_notebook = ttk.Notebook(output_panel)
        output_panel.add(result_notebook, weight=1)
        result_tab = ttk.Frame(result_notebook)
        steps_tab = ttk.Frame(result_notebook)
        result_notebook.add(result_tab, text='Results / Explanation')
        result_notebook.add(steps_tab, text='Calculation steps')
        self.result_text_widget = self.make_text(result_tab)
        step_navigation = ttk.Frame(steps_tab)
        step_navigation.pack(fill='x')
        self.previous_step_button = ttk.Button(step_navigation, text='Previous', command=lambda: self.move_step(-1))
        self.previous_step_button.pack(side='left')
        self.next_step_button = ttk.Button(step_navigation, text='Next', command=lambda: self.move_step(1))
        self.next_step_button.pack(side='left')
        self.step_counter_text = tk.StringVar()
        ttk.Label(step_navigation, textvariable=self.step_counter_text).pack(side='left',padx=8)
        self.step_text_widget = self.make_text(steps_tab)
        plot_frame = ttk.LabelFrame(output_panel, text='Visualization')
        output_panel.add(plot_frame, weight=2)
        self.plot_figure = Figure(figsize=(6, 4), dpi=100)
        self.plot_canvas = FigureCanvasTkAgg(self.plot_figure, master=plot_frame)
        self.plot_canvas.get_tk_widget().pack(fill='both', expand=True)
        plot_toolbar = NavigationToolbar2Tk(self.plot_canvas, plot_frame, pack_toolbar=False)
        plot_toolbar.pack(fill='x')
        self.update_controls()
        self.show_step()
        plot_message(self.plot_figure,'Calculate a 2x2 transformation, determinant or eigen decomposition.',)
        self.plot_canvas.draw_idle()

def run():
    root_window = tk.Tk()
    MatrixApplication(root_window)
    root_window.mainloop()
