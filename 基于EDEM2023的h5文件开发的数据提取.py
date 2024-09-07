# Created_date: 2024/07/20
# Author: Mr zhou
#工作时间外制作的
#version：基于edem2023开发
# Script for post-processing DEM simulaitons of result


import os
import h5py
import numpy as np
import pandas as pd
import time as tm
import tkinter as tk
from tkinter import ttk, messagebox, filedialog,scrolledtext
import csv
import sys
import threading

def GeometryName_get(folder_path):
    GeometryName_dicts = {}
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file == '0.h5':
                file_path = os.path.join(root, file)
                with h5py.File(file_path, 'r') as f:
                    Geometrys_group = f['CreatorData/0/GeometryGroups']
                    for Geometry_name in Geometrys_group:
                        Geometry_group=Geometrys_group[Geometry_name]
                        name_value_bytes = Geometry_group.attrs['name']
                        name_value = name_value_bytes.decode('utf-8')
                        GeometryName_dicts[Geometry_name] = name_value

    return GeometryName_dicts


def update_progress(percent):
    # 打印提示信息
    sys.stdout.write(f'\r{percent}%')
    sys.stdout.flush()
    tm.sleep(0.2)  # 模拟一些工作
    print()  # 打印一个换行符以结束行
def pre_h5_data(folder_path):
    GeometryNameID_dicts = {}
    simulationTimeDicts = {}
    h5_file_count = 0
    file_path1= None
    save_path= None
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.h5'):
                file_path = os.path.join(root, file)
                nameh5 = file.replace(".h5", "")
                with h5py.File(file_path, 'r') as f:
                    timestepdate_group = f['TimestepData']
                    simulationTime_group = list(timestepdate_group.keys())[0]
                    simulationTimeDicts[nameh5] = simulationTime_group
                    Geometry_Groups = timestepdate_group[simulationTime_group]['GeometryGroups']
                    GeometryNames = [name for name in Geometry_Groups.keys()]
                    GeometryNameID_dicts[str(nameh5)] = GeometryNames
                save_path = os.path.join(os.path.dirname(root), '数据提取')
                if not os.path.exists(save_path):
                    os.makedirs(save_path)
                file_path1=root
                h5_file_count += 1
        if save_path is None or file_path1 is None: # Handle case when no .h5 files are found
            raise ValueError("No .h5 files found in the given folder path.")

    return GeometryNameID_dicts, simulationTimeDicts, h5_file_count, save_path, file_path1
def extract_h5_data(root, timestep, geom_name, force=None):
    file_name = f'{timestep}.h5'
    file_path = os.path.join(root, file_name)
    result={}
    with h5py.File(file_path, 'r') as f:
        timestepdate_group = f['TimestepData']
        simulationTime_group = list(timestepdate_group.keys())[0]
        GeometryGroups = timestepdate_group[simulationTime_group]['GeometryGroups']
        geom_names = [name for name in GeometryGroups.keys()]
        #这里的geom——name实际上是h5文件中的几何cad所在的组的组名一般是1、2、3、4数字，因此geom——name实际是数字可以理解为几何ID
        if geom_name in geom_names:
            geom_group = GeometryGroups[geom_name]
            #提取力，h5文件中force torque是数据集共有6列，前三列是x、y、z方向的力
            force1 = np.array(geom_group['force torque'])
            #切片，提取前面三列的数据
            force=force1[:,0:3]

            #print("Shape of force array:", force.shape)  # Print shape for debugging
            #下面这个计算的力不是合力，但是作为求取合力最大，最小值，和的基本数据
            forcemagnitube = np.sqrt(np.sum(force ** 2, axis=1))
            #print("Shape of force magnitube array:", forcemagnitube.shape)
            forcemagnitube_max = np.max(forcemagnitube)
            forcemagnitube_mean = np.mean(forcemagnitube)
            #print('Shape of forcemagnitube_maxarray:', forcemagnitube_max.shape)
            #print('Shape of forcemagnitube_mean array:', forcemagnitube_mean.shape)
            # Ensure correct dimensions for force array
            #对force进行检查，避免不符合3列的数据出现
            if force.shape[1] == 3:
                ###############################################################################
                Xforce_max, Yforce_max, Zforce_max = np.max(force, axis=0)
                Xforce_mean, Yforce_mean, Zforce_mean = np.mean(force, axis=0)
                Xforce_sum, Yforce_sum, Zforce_sum = np.sum(force, axis=0)
                # print('Shape of Xforce_maxarray:', Xforce_max.shape)
                # print('Shape of Xforce_meanarray:', Xforce_mean)
                # 这个才是合力(不知道为何)
                forcemagnitube_sum = np.sqrt(Xforce_sum ** 2 + Yforce_sum ** 2 + Zforce_sum ** 2)
                # print("Shape of  forcemagnitube array:", forcemagnitube_sum.shape)
                ########################################################################################
                # 对力进行分类整合
                force_max = np.hstack((forcemagnitube_max, Xforce_max, Yforce_max, Zforce_max))
                force_mean = np.hstack((forcemagnitube_mean, Xforce_mean, Yforce_mean, Zforce_mean))
                force_sum = np.hstack((forcemagnitube_sum, Xforce_sum, Yforce_sum, Zforce_sum))
                # print("Shape of  force_sum array:", force_sum.shape)
                ###############################################################################################
                # 创建一个空的列表，用来存储磨损值
                wear_data1 = []
                # 2020版本只有0-5，顺序分别是oka、NCCE、TCCE、NCF、TCF、Archard
                for i in range(8):
                    wear_data1.append(np.array(geom_group['CustomProperties'][str(i)]['data']))
                    # print(wear_data1)
                    wear_data = np.array(wear_data1)
            #ar_date存储的数据是['磨粒磨损(m)', 'Archard_Intermediate_Data', '冲击磨损(m)', 'Oka_Deformation','法向力做功值(J)', '切向力做功值(J)'，'法向力', '切向力'],,按照顺序,单位好像默认是m在h5文件中貌似不可以更改，若不对可在后续改进'''
                wear_data = np.squeeze(wear_data)
                # print("Shape of wear data array:", wear_data.shape)
                wear_max = np.max(wear_data, axis=1)
                # print("Shape of wear max array:", wear_max.shape)
                wear_mean = np.mean(wear_data, axis=1)
                # print("Shape of wear mean array:", wear_mean.shape)
                # print("Shape of wear mean :", wear_mean)
                wear_sum = np.sum(wear_data, axis=1)
                wear_all = np.hstack((wear_max, wear_mean, wear_sum))
                # print("Shape of wear all array:", wear_all.shape)
                ##################################################################################################
                # 给出一个高平率使用的组合,分析磨损的平均值，阻力是合力的总合（np数组的列是从0开始数的）
                temp1 = wear_mean[[2, 4, 5, 0]]
                print('shape of temp1', temp1.shape)
                High_frequence_OF_use = np.hstack((temp1, forcemagnitube_sum))
                print("Shape of High_frequence_OF_use array:",High_frequence_OF_use.shape)


            else:
                raise ValueError("Unexpected shape of force array: {}".format(force.shape))
        return force_max, force_mean, force_sum, wear_all, High_frequence_OF_use

def create_h5_file(save_path, timestepDate, column_names):
            h5_file_path = os.path.join(save_path, 'results.h5')
            with h5py.File(h5_file_path, 'w') as h5_file:
                for geometry_name, arrays in timestepDate.items():
                    geom_group = h5_file.create_group(geometry_name)
                    for idx, group_name in enumerate(['max', 'mean', 'sum']):
                        sub_group = geom_group.create_group(group_name)
                        for col_idx, column_name in enumerate(column_names[idx]):
                            sub_group.create_dataset(column_name, data=arrays[idx][:, col_idx])





class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.status_text = None
        self.title("Geometry Selection Tool")
        self.geometry("1600x900")

        self.geometry_dicts = {}
        self.selected_items = []
        self.folder_path = None

        # UI Elements
        self.create_widgets()

    def create_widgets(self):
        # File selection
        self.file_label = tk.Label(self, text="No folder selected")
        self.file_label.pack(pady=10)

        self.select_file_button = tk.Button(self, text="Select Folder", command=self.select_folder)
        self.select_file_button.pack(pady=10)

        # Geometry selection
        self.geometry_label = tk.Label(self, text="Select Geometry Names:")
        self.geometry_label.pack(pady=10)

        self.geometry_listbox = tk.Listbox(self, selectmode=tk.MULTIPLE,height=8)
        self.geometry_listbox.pack(pady=10, fill=tk.BOTH, expand=True)

        # Run and status
        self.run_button = tk.Button(self, text="Run", command=self.run)
        self.run_button.pack(pady=10)

        self.status_label = tk.Label(self, text="Status: Waiting for input")
        self.status_label.pack(pady=10)

        self.status_text = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=50, height=10)
        self.status_text.pack(pady=10)

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_path = folder_path
            self.file_label.config(text=folder_path)
            self.geometry_dicts = GeometryName_get(folder_path)
            self.geometry_listbox.delete(0, tk.END)
            for key, value in self.geometry_dicts.items():
                self.geometry_listbox.insert(tk.END, f"{key}: {value}")
    def run(self):
        selected_indices = self.geometry_listbox.curselection()
        self.selected_items11 = [self.geometry_listbox.get(i) for i in selected_indices]

        self.selected_items= {(selected_items1.split(':')[0]): selected_items1.split(':')[1] for selected_items1 in self.selected_items11}
        print(self.selected_items)


        if not self.selected_items:
            messagebox.showwarning("No Selection", "Please select at least one geometry name.")
            return

        self.status_label.config(text="Status: Running...")
        self.update()

        # Simulate running process
        self.perform_computation()

        self.status_label.config(text="Status: Completed")

    def perform_computation(self):
        if self.folder_path is None:
            messagebox.showerror("Error", "No folder selected.")
            return

        GeometryNameID_dicts, simulationTimeDicts, h5_file_count, save_path, file_path1 = pre_h5_data(self.folder_path)

        if file_path1 is None:
            raise ValueError("file_path1 is None. No .h5 files found.")
        last_folder_name = os.path.basename(file_path1.rstrip(os.path.sep))
        times = np.zeros(h5_file_count, )
        print("-------------------------------------------------------")
        print("Loading: " + str(last_folder_name) + ".dem")
        print("-------------------------------------------------------")
        for i, time in simulationTimeDicts.items():
            #提取时间
            times[int(i)] = float(time)
        print('h5文件总数量：', h5_file_count - 1)
        #初始化变量存储计算数据
        timestepDate_max = np.zeros((h5_file_count, 12))
        timestepDate_mean = np.zeros((h5_file_count, 12))
        timestepDate_sum = np.zeros((h5_file_count, 12))
        timestepDate_High_Frequece = np.zeros((h5_file_count, 5))
        # 创建字典来保存每个几何的数据，字典的键是几何的ID，值是numpy数组
        timestepDate = {}
        timestepDate_HighFrequece = {}
        combine_all_dicts={}
        #创建保存表的名称
        column_names = [
            ['磨粒磨损最大值(mm)', 'Archard_Intermediate_Data', '冲击磨损最大值(mm)', 'Oka_Deformation',
             '法向力做功最大值(J)', '切向力做功最大值(J)', '法向力', '切向力', '合力最大值(N)', 'X方向最大力(N)',
             'Y方向最大力(N)', 'Z方向最大力(N)'],
            ['磨粒磨损平均值(mm)', 'Archard_Intermediate_Data', '冲击磨损平均值(mm)', 'Oka_Deformation',
             '法向力做功平均值(J)', '切向力做功平均值(J)', '法向力', '切向力', '合力平均值(N)', 'X方向平均值(N)',
             'Y方向平均值(N)', 'Z方向平均值(N)'],
            ['磨粒磨损总和(mm)', 'Archard_Intermediate_Data', '冲击磨损总和(mm)', 'Oka_Deformation',
             '法向力做功总和(J)', '切向力做功总和(J)', '法向力', '切向力', '合力总和(N)', 'X方向总和(N)',
             'Y方向总和(N)', 'Z方向总和(N)']
        ]
        # 对数据名称进行重

        sheet_names = ['最大值', '平均值', '总和']
        for geometry_ID, geometry_name in self.selected_items.items():
            #for geometry_name in geometrys_ID:
                # 其实这里的idx和file_h5_name差1，因为h5文件是从0开始算的
                # 获取真正的几何名称
            real_GeometryName = self.selected_items[geometry_ID]
            print("-------------------------------------------------------")
            print("正在计算几何: " + str(real_GeometryName) + "的数据"+'*******')
            for idx in range(1, h5_file_count):
                #提取每一个h5文件内的计算数据
                force_max, force_mean, force_sum, wear_data, High_frequence = extract_h5_data(file_path1, idx,
                                                                                              geometry_ID)

                timestepDate_max[idx] = np.hstack((wear_data[0:8], force_max))

                timestepDate_mean[idx] = np.hstack((wear_data[8:16], force_mean))
                timestepDate_sum[idx] = np.hstack((wear_data[16:24], force_sum))
                timestepDate_High_Frequece[idx] = High_frequence
                print('High_frequence大小',High_frequence)
                combine_all_dicts
            timestepDate[geometry_ID] = np.array([timestepDate_max, timestepDate_mean, timestepDate_sum])
            #提取高频使用的数据
            timestepDate_HighFrequece[geometry_ID] = timestepDate_High_Frequece
            print('timestepDate_High_Frequece的大小',timestepDate_High_Frequece.shape)
                #完成进度计算

#########################################################################################################
            print("-------------------------------------------------------")
            # *
            # 保存所有数据到excel表格中
            data = timestepDate[geometry_ID]
            file_name = self.selected_items[geometry_ID]
            print("-------------------------------------------------------")
            print("Lsaving: " + file_name + " Geometry Date")
            print("-------------------------------------------------------")
            file_full = os.path.join(save_path, f'{file_name}的全部数据.xlsx')
            with pd.ExcelWriter(file_full, engine='openpyxl') as writer:
                for i, array in enumerate(data):
                    print('array的大小',array.shape)
                    print('保存文件时候的i', i)
                    df = pd.DataFrame(array, columns=column_names[i])
                    df.insert(0, '时间', times)  # Insert time column
                    sheet_name = f'{sheet_names[i]}'
                    print(f"Writing to sheet: {sheet_name}")  # Debugging information
                    print(df.head())  # Print first few rows for debugging
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f'{file_name}几何的数据已保存为xlsx格式。\n 存储位置：{save_path}')

            # *
            # 保存高频数据到exxcel表格中
            #
            save_path1 = os.path.join(os.path.dirname(save_path), '高频数据')
            if not os.path.exists(save_path1):
                os.makedirs(save_path1)

            if save_path1 is None or file_path1 is None:  # Handle case when no .h5 files are found
                raise ValueError("No .h5 files found in the given folder path.")
            column_names_HighFrequece = [
                '冲击磨损平均值(m)', '法向力做功平均值(J)', '切向力做功平均值(J)', '磨粒磨损(m)', '合力总合(N)'
            ]
            data_f1 = timestepDate_HighFrequece[geometry_ID]
            data_f = np.insert(data_f1, 0, times, axis=1)
            # print('data_f的大小',data_f.shape)
            file_name = self.selected_items[geometry_ID]
            print("-------------------------------------------------------")
            print("saving: " + file_name + "的高频数据")
            # file_full = os.path.join(save_path1, f'{file_name}计算结果.xlsx')
            save_path2=r'F:/EDEMSTUDY/dem/全部数据整理'
            file_full = os.path.join(save_path2, f'{file_name}.csv')

            df = pd.DataFrame(data_f, columns=['时间(s)'] + column_names_HighFrequece)
            df.to_csv(file_full, index=False,encoding='utf-8-sig' , quoting=csv.QUOTE_MINIMAL)
            print(f'高频数据文件已保存为csv格式。\n 存储位置：{save_path}')


#########################################################################################################




if __name__ == "__main__":
    app = Application()
    app.mainloop()
