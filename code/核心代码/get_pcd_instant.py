import sys
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
import pcl
import struct
import oss2
import os
import time
import shutil

class PointCloudSaver(Node):
    def __init__(self):
        super().__init__('pointcloud_saver')
        
        # 设置QoS配置，确保与发布者一致
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        
        self.subscription = self.create_subscription(
            PointCloud2,
            '/dtof/depth1/point',  # 替换为你的点云话题名称
            self.listener_callback,
            qos_profile)
        self.subscription  # 防止未使用的变量警告

        self.points_accumulated = []  # 存储累积的点云数据
        self.save_count = 0  # 点云文件计数器

        # 阿里云OSS配置
        self.auth = oss2.Auth('LTAI5tSdmM7JBcPdEUEiSJH8', 'twudtXOjsndbj57EJsqSjBvaafrbKD')
        self.bucket = oss2.Bucket(self.auth, 'https://oss-cn-beijing.aliyuncs.com', 'my-pcd11')

        # 上传文件名标签
        self.upload_labels = ['top', 'bottom', 'left', 'right']
        self.remove_dir('/home/pie/桌面/bag_pcds')

    def remove_dir(self,path):
        try:
            shutil.rmtree(path)
            os.mkdir(path)
        except:
            pass
    
    def listener_callback(self, msg):
        self.accumulate_points(msg)
        self.save_pointcloud()

    def accumulate_points(self, cloud_msg):
        # 提取点云数据并添加到累积的点云列表中
        for point in self.read_points(cloud_msg):
            self.points_accumulated.append([point[0], point[1], point[2]])

    def save_pointcloud(self):
        if self.points_accumulated:
            # 转换为PCL点云对象
            pcl_cloud = pcl.PointCloud()
            pcl_cloud.from_list(self.points_accumulated)

            # 生成唯一的文件名
            file_name = '{}.pcd'.format(self.save_count)
            file_path = os.path.join('/home/pie/桌面/bag_pcds', file_name)

            # 保存为PCD文件
            pcl.save(pcl_cloud, file_path)
            # self.get_logger().info('Saved point cloud to {}'.format(file_path))

            # 上传到阿里云OSS
            try:
                self.remove_from_oss(file_path)
            except:
                pass
            self.upload_to_oss(file_path)

            # 清空累积的点云列表
            self.points_accumulated.clear()

            # 递增文件计数器
            self.save_count += 1
            if(self.save_count == 4):
                sys.exit()

    def upload_to_oss(self, file_path):
        label_index = (self.save_count) % 4
        file_group = (self.save_count) // 4 + 1
        oss_file_name = '{}_{}.pcd'.format(file_group, self.upload_labels[label_index])
        
        with open(file_path, 'rb') as fileobj:
            self.bucket.put_object(oss_file_name, fileobj)
            self.get_logger().info('Uploaded {} to OSS as {}'.format(file_path, oss_file_name))

    def remove_from_oss(self, file_path):
        label_index = (self.save_count) % 4
        file_group = (self.save_count) // 4 + 1
        oss_file_name = '{}_{}.pcd'.format(file_group, self.upload_labels[label_index]) 
        
        self.bucket.delete_object(oss_file_name)
        self.get_logger().info('removes from OSS as {}'.format(oss_file_name))

    def read_points(self, cloud_msg):
        # 这里是手动解析PointCloud2数据
        fmt = 'fff'  # 对于xyz点云
        width, height = cloud_msg.width, cloud_msg.height
        point_step, row_step = cloud_msg.point_step, cloud_msg.row_step
        data = cloud_msg.data

        for h in range(height):
            for w in range(width):
                offset = h * row_step + w * point_step
                x, y, z = struct.unpack_from(fmt, data, offset)
                yield (x, y, z)

def main(args=None):
    rclpy.init(args=args)
    pointcloud_saver = PointCloudSaver()
    rclpy.spin(pointcloud_saver)
    pointcloud_saver.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
