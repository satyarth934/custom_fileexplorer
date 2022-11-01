import os
import logging
import pyperclip    # 
import numpy as np
from tkinter import ttk
import tkinter as tk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)
from matplotlib import pyplot as plt
from tkinter.messagebox import showinfo


class App(tk.Tk):
    """App class within which all the events and widgets take place.
    """

    def __init__(self):
        super().__init__()

        self.title('NPY Image Viewer')
        self.geometry('620x200')

        dir_btn = tk.Button(self, text='Open Directory', bd='5',
                          command=self.get_dirname)
        dir_btn.grid(row=0, sticky=tk.E+tk.W)
        
    
    def get_dirname(self):
        """Get the directory name using a GUI pop-up.
        """
        self.dirname = tk.filedialog.askdirectory(
            title="NPY Image Directory",
            initialdir="/",
        )
        print(f"{self.dirname = }")

        # Kill the app if no directory is specified.
        if not self.dirname:
            logging.warning("No directory specified. Closing the app...")
            self.destroy()
            return

        self.open_dir()


    def open_dir(self):
        """Tasks to be performed when a directory path has been defined.
        """

        self.tree = self.create_tree_widget()
        self.update()

        # the figure that will contain the plot
        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.plot1 = self.fig.add_subplot(111)

        fig_shape = self.fig.get_size_inches() * self.fig.dpi
        self.new_height = int(fig_shape[0] + 42)    # 42 is for the NavigationToolbar
        self.new_width = int(self.tree.winfo_width() + fig_shape[1])

        self.geometry(f"{self.new_width}x{self.new_height}")


    def copy_from_treeview(self, tree, event):
        """Copy function that is executed whenever a tree item is selected. The text of the selected item is copied in the clipboard.

        Args:
            tree (ttk.Treeview): parent Treeview
            event: event when the function is to be triggered
        """

        selected_items = tree.selection()
                
        copy_values = []
        for selected_item in selected_items:
            try:
                value = tree.item(selected_item)["values"][0]
                copy_values.append(str(value))
            except:
                pass
            
        copy_string = "\n".join(copy_values)
        pyperclip.copy(copy_string)


    def create_tree_widget(self):
        """Creates the tree widget to view the list of files with a preview pane.

        Returns:
            ttk.Treeview: Treeview that is generated.
        """

        columns = ('file_name')
        tree = ttk.Treeview(self, columns=columns, show='headings')

        # define headings
        tree.heading('file_name', text='File Name')
        tree.column("file_name", minwidth=0, width=350, stretch=0)

        tree.bind('<<TreeviewSelect>>', self.item_selected)
        tree.grid(row=1, column=0, sticky=tk.NSEW)
        # tree.pack(side=tk.LEFT, expand=True, fill=tk.Y)
        tree.bind("<<TreeviewSelect>>", lambda x: self.copy_from_treeview(tree, x), add=True)

        # add a scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky='ns')
        # scrollbar.pack(side=tk.LEFT, expand=True, fill=tk.Y)

        files = os.listdir(self.dirname)

        # add data to the treeview
        for file_i in files:
            tree.insert('', tk.END, values=file_i)

        return tree

    def item_selected(self, event):
        """Function to execute when a particular item in the Treeview is selected. It reads the path, open the `npy` file, and plots it as an image in matplotlib plot. This sample function only works for a numpy 2d array with 1 or 3 channels (anything that is accepted by matplotlib.pyplot.imshow()).

        Args:
            event: event when the function is to be triggered.
        """

        selected_item = self.tree.selection()[-1]
        # for selected_item in self.tree.selection():
        item = self.tree.item(selected_item)
        record = item['values'][0]

        img = np.load(os.path.join(self.dirname, record)).squeeze()

        # plotting the graph
        self.plot1.imshow(img)
        self.plot1.set_title(record)
    
        # creating the Tkinter canvas
        # containing the Matplotlib figure
        canvas = FigureCanvasTkAgg(self.fig, master=self)
        for item in canvas.get_tk_widget().find_all():
            canvas.get_tk_widget().delete(item)
        canvas.draw()
    
        # placing the canvas on the Tkinter window
        # canvas.get_tk_widget().pack()
        canvas.get_tk_widget().grid(row=1, column=2, sticky='ns')
    
        # creating the Matplotlib toolbar
        toolbarFrame = tk.Frame(master=self)
        toolbarFrame.grid(row=2, column=2, sticky='s')
        toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)
        toolbar.update()
        self.update()


def main():
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()
