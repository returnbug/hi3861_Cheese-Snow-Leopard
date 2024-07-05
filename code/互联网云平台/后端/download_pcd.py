# -*- coding: utf-8 -*-
import oss2
import datetime
import time
import os
from oss2.credentials import EnvironmentVariableCredentialsProvider
from oss2.models import MetaQuery
import open3d as o3d
import numpy as np
from scipy.optimize import curve_fit

voxel_size = 0.01  # 越小密度越大
radius = 0.07

# 从环境变量中获取访问凭证。运行本代码示例之前，请确保已设置环境变量OSS_ACCESS_KEY_ID和OSS_ACCESS_KEY_SECRET。
auth = oss2.Auth('LTAI5tSdmM7JBcPdEUEiSJH8', 'twudtXOjsndbj57EJsqSjBvaafrbKD')

# Endpoint以杭州为例，其它Region请按实际情况填写。
# 填写Bucket名称，例如examplebucket。
bucket = oss2.Bucket(auth, 'https://oss-cn-beijing.aliyuncs.com', 'my-pcd11')

# 本地保存文件的目录
local_save_dir = 'D:\\Projects\\PycharmProjects\\IotBack\\pcds1'

# 确保本地保存文件的目录存在
os.makedirs(local_save_dir, exist_ok=True)

# 记录最后一次查询的时间
last_checked_time = datetime.datetime(2023, 12, 1)


def to_rfc3339(dt):
    return dt.isoformat("T") + "Z"

#处理Nan
def remove_nan_lines(input_file):
    # 读取输入文件
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # 过滤掉带有 "nan" 数据的行
    filtered_lines = [line for line in lines if "nan" not in line]

    # 将过滤后的内容写回输入文件
    with open(input_file, 'w') as f:
        f.writelines(filtered_lines)

# 定义非线性函数，这里假设是一个二次曲面
def func(x, a, b, c, d, e, f):
    return a * x[0]**2 + b * x[1]**2 + c * x[0] * x[1] + d * x[0] + e * x[1] + f
#
# def f(x, y):
#     return popt[0]*x**2 + popt[1]*y**2 + popt[2]*x*y + popt[3]*x + popt[4]*y + popt[5]

# 定义曲面的梯度函数，即一阶偏导数
def gradient(f, x, y):
    h = 1e-6  # 差分步长，可以根据精度要求调整
    df_dx = (f(x + h, y) - f(x - h, y)) / (2 * h)  # 对x求偏导
    df_dy = (f(x, y + h) - f(x, y - h)) / (2 * h)  # 对y求偏导
    return df_dx, df_dy

# 定义曲面的曲率函数，即二阶偏导数
def curvature(f, x, y):
    h = 1e-6  # 差分步长，可以根据精度要求调整
    d2f_dx2 = (f(x + h, y) - 2 * f(x, y) + f(x - h, y)) / (h ** 2)  # 对x求二阶偏导
    d2f_dy2 = (f(x, y + h) - 2 * f(x, y) + f(x, y - h)) / (h ** 2)  # 对y求二阶偏导
    d2f_dxdy = (f(x + h, y + h) - f(x + h, y - h) - f(x - h, y + h) + f(x - h, y - h)) / (4 * h ** 2)  # 对xy求混合偏导
    df_dx, df_dy = gradient(f, x, y)  # 调用梯度函数求一阶偏导
    E = 1 + df_dx ** 2
    F = df_dx * df_dy
    G = 1 + df_dy ** 2
    L = d2f_dx2 / np.sqrt(1 + df_dx ** 2 + df_dy ** 2)  # np.sqrt()表示开方
    M = d2f_dxdy / np.sqrt(1 + df_dx ** 2 + df_dy ** 2)
    N = d2f_dy2 / np.sqrt(1 + df_dx ** 2 + df_dy ** 2)
    K = (L * N - M ** 2) / (E * G - F ** 2)  # 高斯曲率
    H = (E * N + G * L - 2 * F * M) / (2 * (E * G - F ** 2))  # 平均曲率
    return K, H

def download_new_files():
    global last_checked_time

    # 获取当前时间
    current_time = datetime.datetime.utcnow()

    # 指定查询最后更新时间在上次查询时间到当前时间范围内的文件，返回结果按文件名升序排列。
    do_meta_query_request = MetaQuery(
        max_results=100,
        query=f'{{"SubQueries":[{{"Field":"FileModifiedTime","Value":"{to_rfc3339(last_checked_time)}","Operation":"gt"}},{{"Field":"FileModifiedTime","Value":"{to_rfc3339(current_time)}","Operation":"lt"}}],"Operation":"and"}}',
        sort='Filename',
        order='asc'
    )
    result = bucket.do_bucket_meta_query(do_meta_query_request)

    for s in result.files:
        # 本地文件路径
        local_file_path = os.path.join(local_save_dir, s.file_name)
        # 下载文件
        bucket.get_object_to_file(s.file_name, local_file_path)
        #处理NaN
        remove_nan_lines(local_file_path)

        # #查找缺陷
        # pcd = o3d.io.read_point_cloud(local_file_path)
        # pcd = pcd.voxel_down_sample(voxel_size)  # 下采样
        # cloud = pcd
        # points = np.asarray(cloud.points)  # 点云转换为数组 点云数组形式为[[x1,y1,z1],[x2,y2,z2],...]
        # kdtree = o3d.geometry.KDTreeFlann(cloud)  # 建立KDTree
        # num_points = len(cloud.points)  # 点云中点的个数
        # pcd.paint_uniform_color([1, 0, 0])  # 初始化所有颜色为红色
        #
        # curvatures = []
        # well_points = []  # 用于存储阱部分的点的坐标
        #
        # global popt, pcov
        # for i in range(num_points):
        #     k, idx, _ = kdtree.search_radius_vector_3d(cloud.points[i], radius)  # 返回邻域点的个数和索引
        #     neighbors = points[idx]  # 数组形式为[[x1,y1,z1],[x2,y2,z2],...]
        #     if len(neighbors) < 6:  # 检查邻域点数量是否足够
        #         curvatures.append([0, 0])  # 如果不够，跳过拟合，填充0
        #         continue
        #     Y = neighbors[:, 2]  # 因变量
        #     X = neighbors[:, [0, 1]]  # 自变量 [[2, 3], [1, 1], [8, 9], [11, 12], [4, 5], [8, 9]] 6*2
        #     popt, pcov = curve_fit(func, xdata=X.T, ydata=Y)
        #     x = cloud.points[i][0]  # 某一点的x坐标
        #     y = cloud.points[i][1]  # 某一点的y坐标
        #     K, H = curvature(f, x, y)  # 计算该点的曲率
        #     curvatures.append([K, H])
        #
        # for i in range(len(curvatures)):
        #     if -0.05 < curvatures[i][0] < 0.05 and -0.05 < curvatures[i][1] < 0.05:  # 平坦
        #         np.asarray(pcd.colors)[i] = [0, 0, 0]  # 黑
        #     elif -0.05 < curvatures[i][0] < 0.05 and curvatures[i][1] > 0.05:  # 凸
        #         np.asarray(pcd.colors)[i] = [1, 0, 0]  # 红
        #     elif -0.05 < curvatures[i][0] < 0.05 and curvatures[i][1] < -0.05:  # 凹
        #         np.asarray(pcd.colors)[i] = [0, 1, 0]  # 绿
        #     elif curvatures[i][0] < -0.05 and curvatures[i][1] > 0.05:  # 鞍形脊
        #         np.asarray(pcd.colors)[i] = [0, 0, 1]  # 蓝
        #     elif curvatures[i][0] < -0.05 and curvatures[i][1] < -0.05:  # 鞍形谷
        #         np.asarray(pcd.colors)[i] = [0, 1, 1]  # 青
        #     elif curvatures[i][0] > 0.05 and curvatures[i][1] > 0.05:  # 峰
        #         np.asarray(pcd.colors)[i] = [1, 0, 1]  # 紫
        #     elif curvatures[i][0] > 0.05 and curvatures[i][1] < -0.05:  # 阱
        #         np.asarray(pcd.colors)[i] = [1, 1, 0]  # 黄
        #         well_points.append(points[i])  # 将阱部分的点的坐标添加到well_points
        #
        # o3d.io.write_point_cloud(local_file_path, pcd)

        print(f'Downloaded: {s.file_name} to {local_file_path}')

    # 更新最后一次查询的时间
    last_checked_time = current_time

while True:
    try:
        download_new_files()
    except Exception as e:
        print(f'Error: {e}')
    # 每隔一秒钟检查一次
    time.sleep(10)
