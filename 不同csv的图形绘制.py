import pandas as pd
import matplotlib.pyplot as plt
import os
import re
import matplotlib
from charset_normalizer import from_path

# 设置字体为微软雅黑，标签和标题的大小分别为16号和18号
matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
matplotlib.rcParams['font.size'] = 18

file_names = [f"pp{i}.csv" for i in range(216)]

# 分组大小
group_size = 6
target_folder = r'F:/EDEMSTUDY/dem/Research on Friction Factors/PP/数据分析/按照滚动摩擦分组'

# 开始分组并处理文件
for i in range(0, len(file_names), group_size):
    group = file_names[i:i + group_size]

    # 创建目标子文件夹，如 '0-5', '6-11'
    folder_name = f"{i}-{i + group_size - 1}"
    csv_folder_path = os.path.join(target_folder, folder_name)
    csv_folder_path = csv_folder_path.replace("\\", "/")

    # 变量名称列表（与列索引对应）
    column_names = [
        '冲击磨损平均值(m)', '法向力做功平均值(J)', '切向力做功平均值(J)', '磨粒磨损(m)', '合力总合(N)'
    ]

    # 获取所有CSV文件的路径，并按数字顺序排序
    csv_files = sorted([f for f in os.listdir(csv_folder_path) if f.endswith('.csv')],
                       key=lambda x: int(re.findall(r'\d+', x)[0]))

    # 创建字典来存储每列数据
    data_dict = {i: [] for i in range(1, 6)}

    # 读取每个CSV文件
    for file in csv_files:
        file_path = os.path.join(csv_folder_path, file)

        # 自动检测文件编码
        encoding = from_path(file_path).best().encoding
        print('编码格式', encoding)
        try:
            df = pd.read_csv(file_path, encoding=encoding)  # 读取CSV文件，并替换无效字符
        except Exception as e:
            print(f"文件 {file} 读取失败，错误信息：{e}")
            continue

        # 提取数据
        time = df.iloc[:, 0]  # 第一列是时间
        for i in range(1, 6):
            data_dict[i].append(df.iloc[:, i])

    # 图形颜色列表，每个图形内部使用相同的颜色顺序
    colors = plt.cm.tab10.colors  # Tab10色图包含10种不同的颜色

    # 绘制图形
    for i in range(1, 6):
        plt.figure(figsize=(16, 9))  # 图形大小3:4
        for idx, file in enumerate(csv_files):
            label = file.split('.')[0]  # 使用文件名作为图例标签
            plt.plot(data_dict[i][idx], label=label, color=colors[idx % len(colors)], linewidth=5)

        # 清理列名称中的括号及其内容
        clean_name = re.sub(r'\s*\(.*?\)', '', column_names[i - 1])

        # 设置图形属性，调整标签字体大小为16
        plt.xlabel('时间(s)', fontsize=16)
        plt.ylabel(clean_name, fontsize=16)
        plt.title(f'{clean_name} vs 时间(s)', fontsize=18)
        plt.legend(title='文件名', fontsize=16)  # 调整图例字体大小为16
        plt.grid(True)

        # 保存图形
        plt.savefig(f'{csv_folder_path}/plot_{i}.png', bbox_inches='tight')
        plt.close()

    print(f"{folder_name} 组图形已保存。")
