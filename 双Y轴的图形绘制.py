import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import chardet
import re
# 设置中文字体
def set_matplotlib_font():
    font_path = "C:/Windows/Fonts/simhei.ttf"  # 确保路径指向有效的中文字体文件
    matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 中文字体
    matplotlib.rcParams['axes.unicode_minus'] = False  # 负号显示正常

class DualYAxisPlotter:
    def __init__(self, root):
        self.root = root
        self.root.title("Dual Y-axis Plotter")
        #用列表来存储数据
        self.data_frames = []
        #同样用列表来存储图形
        self.curves = []
        self.file_namedicts={}
        self.colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', '#FF5733', '#33FF57', '#3357FF']
        self.linestyles = ['-', '--', '-.', ':', '-', '--', '-.', ':', '-', '--']
        self.markers = ['o', 's', 'D', '^', 'v', '<', '>', 'p', '*', 'h']  # 圆形, 方形, 菱形, 上三角, 下三角, 左三角, 右三角, 五边形, 星形, 六边形

        set_matplotlib_font()  # 设置中文字体

        self.create_widgets()

    def create_widgets(self):
        # Load CSV button
        self.load_button = ttk.Button(self.root, text="Load CSV File", command=self.load_csv)
        self.load_button.grid(row=0, column=0, padx=10, pady=10)

        # Dropdowns for selecting CSV file, columns, color, linestyle, marker, and size
        self.csv_file_label = ttk.Label(self.root, text="Select CSV file:")
        self.csv_file_label.grid(row=1, column=0, padx=10, pady=10)
        self.csv_file_combo = ttk.Combobox(self.root, state="readonly")
        self.csv_file_combo.grid(row=1, column=1, padx=10, pady=10)
        self.csv_file_combo.bind("<<ComboboxSelected>>", self.update_columns)

        self.x_col_label = ttk.Label(self.root, text="Select X-axis column:")
        self.x_col_label.grid(row=2, column=0, padx=10, pady=10)
        self.x_col_combo = ttk.Combobox(self.root, state="readonly")
        self.x_col_combo.grid(row=2, column=1, padx=10, pady=10)

        self.y_col_label = ttk.Label(self.root, text="Select Y-axis column:")
        self.y_col_label.grid(row=3, column=0, padx=10, pady=10)
        self.y_col_combo = ttk.Combobox(self.root, state="readonly")
        self.y_col_combo.grid(row=3, column=1, padx=10, pady=10)

        self.color_label = ttk.Label(self.root, text="Choose color:")
        self.color_label.grid(row=4, column=0, padx=10, pady=10)
        self.color_combo = ttk.Combobox(self.root, state="readonly", values=self.colors)
        self.color_combo.grid(row=4, column=1, padx=10, pady=10)

        self.linestyle_label = ttk.Label(self.root, text="Choose linestyle:")
        self.linestyle_label.grid(row=5, column=0, padx=10, pady=10)
        self.linestyle_combo = ttk.Combobox(self.root, state="readonly", values=self.linestyles)
        self.linestyle_combo.grid(row=5, column=1, padx=10, pady=10)

        self.marker_label = ttk.Label(self.root, text="Choose marker:")
        self.marker_label.grid(row=6, column=0, padx=10, pady=10)
        self.marker_combo = ttk.Combobox(self.root, state="readonly", values=self.markers)
        self.marker_combo.grid(row=6, column=1, padx=10, pady=10)

        self.size_label = ttk.Label(self.root, text="Marker size:")
        self.size_label.grid(row=7, column=0, padx=10, pady=10)
        self.size_spinbox = ttk.Spinbox(self.root, from_=1, to=20, increment=1)
        self.size_spinbox.grid(row=7, column=1, padx=10, pady=10)

        self.y_axis_label = ttk.Label(self.root, text="Select Y-axis:")
        self.y_axis_label.grid(row=8, column=0, padx=10, pady=10)
        self.y_axis_combo = ttk.Combobox(self.root, state="readonly", values=["Left Y-axis", "Right Y-axis"])
        self.y_axis_combo.grid(row=8, column=1, padx=10, pady=10)

        # Add curve button
        self.add_curve_button = ttk.Button(self.root, text="Add Curve", command=self.add_curve)
        self.add_curve_button.grid(row=9, column=0, columnspan=2, pady=10)

        # Plot button
        self.plot_button = ttk.Button(self.root, text="Plot", command=self.plot)
        self.plot_button.grid(row=10, column=0, columnspan=2, pady=10)

        # Clear curves button
        self.clear_curves_button = ttk.Button(self.root, text="Clear Curves", command=self.clear_curves)
        self.clear_curves_button.grid(row=11, column=0, columnspan=2, pady=10)

        # Clear data button
        self.clear_data_button = ttk.Button(self.root, text="Clear Data", command=self.clear_data)
        self.clear_data_button.grid(row=12, column=0, columnspan=2, pady=10)

        # Update data button
        self.update_data_button = ttk.Button(self.root, text="Update Data", command=self.update_data)
        self.update_data_button.grid(row=13, column=0, columnspan=2, pady=10)

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])

        if file_path:
            # 自动检测文件编码
            with open(file_path, 'rb') as f:
                result = chardet.detect(f.read())
            encoding = result['encoding']

            # 使用检测到的编码读取文件
            try:
                data = pd.read_csv(file_path, encoding=encoding)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV file:\n{e}")
                return
            #将读取到的数据存储到列表中
            self.data_frames.append(data)
            for i in range(len(self.data_frames)):

                file_name=os.path.basename(file_path)
                file_name=os.path.splitext(file_name)[0]
                self.file_namedicts[i]=file_name
            self.csv_file_combo['values'] = [f"CSV {i}:{self.file_namedicts[i]}" for i in range(len(self.data_frames))]
            self.csv_file_combo.current(len(self.data_frames) - 1)
            print(self.csv_file_combo.current())

            self.update_columns()

    def update_columns(self, event=None):
        if self.csv_file_combo.current() >= 0:
            data = self.data_frames[self.csv_file_combo.current()]
            columns = data.columns.tolist()
            self.x_col_combo['values'] = columns
            self.y_col_combo['values'] = columns

    def add_curve(self):
        if self.x_col_combo.get() == "" or self.y_col_combo.get() == "":
            messagebox.showwarning("Input Error", "Please select columns for X-axis and Y-axis.")
            return

        if self.color_combo.get() == "" or self.linestyle_combo.get() == "" or self.marker_combo.get() == "" or self.size_spinbox.get() == "":
            messagebox.showwarning("Input Error", "Please select color, linestyle, marker, and size.")
            return

        self.curves.append({
            "data": self.data_frames[self.csv_file_combo.current()],
            "x_col": self.x_col_combo.get(),
            "y_col": self.y_col_combo.get(),
            "color": self.color_combo.get(),
            "linestyle": self.linestyle_combo.get(),
            "marker": self.marker_combo.get(),
            "size": int(self.size_spinbox.get()),
            "y_axis": self.y_axis_combo.get(),
            "lable" :self.file_namedicts[self.csv_file_combo.current()]+self.y_col_combo.get(),
        })
        print(self.curves)

        messagebox.showinfo("Curve Added", f"Curve added with Y-axis column: {self.y_col_combo.get()}")

    def plot(self):
        if len(self.curves) == 0:
            messagebox.showwarning("No Curves", "No curves added to plot.")
            return

        fig, ax1 = plt.subplots()

        ax2 = None
        for curve in self.curves:
            data = curve["data"]
            x_col = curve["x_col"]
            y_col = curve["y_col"]
            color = curve["color"]
            linestyle = curve["linestyle"]
            marker = curve["marker"]
            size = curve["size"]
            y_axis = curve["y_axis"]
            lable=curve["lable"]
            clean_name = re.sub(r'\s*\(.*?\)', '', lable)
            if y_axis == "Left Y-axis":
                ax = ax1
            else:
                if ax2 is None:
                    ax2 = ax1.twinx()
                ax = ax2

            ax.plot(data[x_col], data[y_col], color=color, linestyle=linestyle, marker=marker, markersize=size, label=clean_name)

            ax.set_xlabel(x_col)
            if y_axis == "Left Y-axis":
                ax.set_ylabel(y_col)
            else:
                ax2.set_ylabel(y_col)

            ax.legend()
        ax1.legend(loc="upper left")
        if ax2:
            ax2.legend(loc="upper right")
        plt.title("Dual Y-axis Plot")
        plt.show()

    def clear_curves(self):
        self.curves.clear()
        messagebox.showinfo("Curves Cleared", "All curves have been cleared.")

    def clear_data(self):
        self.data_frames.clear()
        self.csv_file_combo.set('')
        self.x_col_combo.set('')
        self.y_col_combo.set('')
        self.curves.clear()
        self.csv_file_combo['values'] = []
        messagebox.showinfo("Data Cleared", "All data and curves have been cleared.")

    def update_data(self):
        if self.csv_file_combo.current() >= 0:
            file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
            if file_path:
                # 自动检测文件编码
                with open(file_path, 'rb') as f:
                    result = chardet.detect(f.read())
                encoding = result['encoding']

                # 使用检测到的编码读取文件
                try:
                    new_data = pd.read_csv(file_path, encoding=encoding)
                    self.data_frames[self.csv_file_combo.current()] = new_data
                    self.update_columns()
                    messagebox.showinfo("Data Updated", "CSV file has been updated.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load CSV file:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DualYAxisPlotter(root)
    root.mainloop()