#! /usr/bin/python
import shutil
import signal
import sys
import time
import os
import threading
import subprocess
import oss2

folder_path = "/home/pie/bag"
pcd_path = "/home/pie/bag_pcds"
extension = ".db3"

auth = oss2.Auth('LTAI5tSdmM7JBcPdEUEiSJH8', 'twudtXOjsndbj57EJsqSjBvaafrbKD')
bucket = oss2.Bucket(auth, 'https://oss-cn-beijing.aliyuncs.com', 'my-pcd11')

count = 0

def upload():
    
    os.system("gnome-terminal -- bash -c 'cd ~ && zip -r bag_pcds.zip bag_pcds'")
    time.sleep(3)
    with open('/home/pie/bag_pcds.zip', 'rb') as fileobj:
        bucket.put_object(f'bag{count}.zip', fileobj)

def RemoveDir(filepath):
    if os.path.exists(filepath):
        shutil.rmtree(filepath)

def run_dtof_task():
    # global pid
    # command = "cd ./dtof_sensor_driver/sample/ubuntu_pc/dtof_ros_demo_udp/ && source install/setup.sh && ros2 launch dtof_client_node dtof_client_node.launch.py"
    # process = subprocess.Popen(command, shell=True)
    # # 获取子进程的PID
    # pid = process.pid
    # print(pid)
    os.system("gnome-terminal -- bash -c 'cd ./dtof_sensor_driver/sample/ubuntu_pc/dtof_ros_demo_udp/ && source install/setup.sh && ros2 launch dtof_client_node dtof_client_node.launch.py;exec bash'")
    # os.system("cd ./dtof_sensor_driver/sample/ubuntu_pc/dtof_ros_demo_udp/ && source install/setup.sh && ros2 launch dtof_client_node dtof_client_node.launch.py")
    # subprocess.run("source ./install/setup.sh", shell=True, cwd="./dtof_sensor_driver/sample/ubuntu_pc/dtof_ros_demo_udp/src")

def run_bag_task():
    global pid2
    # pid2 = os.getpid()
    command = "cd ~ && ros2 bag record /dtof/depth1/point -d 1 -o bag"
    process = subprocess.Popen(command, shell=True)
    # # 获取子进程的PID
    pid2 = process.pid

    # os.system("gnome-terminal --command='bash -c \"cd ~ && ros2 bag record /dtof/depth1/point -d 1 -o bag\"'")
    # os.system("cd ~ && ros2 bag record /dtof/depth1/point -d 1 -o bag")

def run_pcd_task():
    os.system("gnome-terminal -- bash -c 'cd ./rosbag2_to_pcd && source install/setup.sh && ros2 launch rosbag2_to_pcd rosbag2_to_pcd.launch.xml'")
    # os.system("cd ./rosbag2_to_pcd && source install/setup.sh && ros2 launch rosbag2_to_pcd rosbag2_to_pcd.launch.xml")

if __name__ == "__main__":

    RemoveDir(folder_path)
    RemoveDir(pcd_path)

    dtof_thread = threading.Thread(target=run_dtof_task)
    dtof_thread.start()

    time.sleep(5)

    # # 启动另一个线程来运行ros2 bag录制
    # bag_thread = threading.Thread(target=run_bag_task)
    # bag_thread.start()

    time.sleep(3)

    

    # while True:
    #     try:
    #         files = os.listdir(folder_path)
    #         db3_files = [file for file in files if file.endswith(extension)]
    #         # 统计文件数量
    #         file_count = len(db3_files)
    #         # print(file_count)
    #         # print(pid1)
    #         if(file_count == 3):
    #     #         # kill bag task
    #             os.system(f"gnome-terminal -- bash -c 'kill -2 {pid2}'")
                
    #             # run pcd task
    #             pcd_thread = threading.Thread(target=run_pcd_task)
    #             pcd_thread.start()
    #             time.sleep(2)                # break
    #             upload()
    #             time.sleep(2)
    #             # sys.exit()
                
    #             RemoveDir(folder_path)
    #             RemoveDir(pcd_path)
    #             file_count = 0

    #             print(f"epoch_{count} finished")
    #             count += 1
                
    #             time.sleep(1)

    #             bag_thread = threading.Thread(target=run_bag_task)
    #             bag_thread.start()
    #             time.sleep(2)
    # #         # print("kill")
    # #         # sys.exit()
    #     except:
    #         pass
