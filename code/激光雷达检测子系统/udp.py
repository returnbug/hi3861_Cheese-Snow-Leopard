import serial
import time
import socket
import os
import subprocess

def get_pid_by_port(port):
    try:
        # 使用 lsof 命令获取 PID
        command = f"sudo lsof -t -i :{port}"
        result = subprocess.check_output(command, shell=True, text=True)
        pid = result.strip()
        return pid
    except subprocess.CalledProcessError as e:
        pass

def kill_process(pid):
    try:
        os.kill(int(pid), 9)  # 9 表示 SIGKILL 信号
        print(f"Process with PID {pid} has been killed.")
    except Exception as e:
        pass

def udp_init():
    global sock
    # UDP接收端的IP和端口
    UDP_IP = "0.0.0.0"  # 监听所有网络接口
    UDP_PORT = 2368  # UDP端口号
    pid = get_pid_by_port(UDP_PORT)
    
    # 创建UDP套接字
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # kill_process(pid)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"UDP接收器已启动,监听端口 {UDP_PORT}...")

def uart_init():
    global ser
    ser = serial.Serial("/dev/ttyUSB0", 9600)
    if ser.isOpen():
        print("open success")
    else:
        print("open failed")

if __name__ == '__main__':
    udp_init()
    uart_init()
    while True:
        data_matrix = []
        data, addr = sock.recvfrom(4900)  # 缓冲区大小为4900字节
        data_array = []
        for i in range(0, len(data), 1):
            chunk = data[i:i+1]
            val = int.from_bytes(chunk, byteorder='big')
            data_array.append(val)
        
        # 获取中间部分的64个点的距离
        if len(data_array) >= 1024:
            start_index = (len(data_array) // 2) - 32
            end_index = start_index + 64
            middle_points = data_array[start_index:end_index]
            
            # 将64个点的距离存储到data_matrix中
            for i in range(0, 64, 2):
                dat = float((middle_points[i+1] << 8 | middle_points[i]) / 10.0)
                data_matrix.append(dat)
        
        print(data_matrix)
        # 将64个点的距离通过串口发送出去
        serial.write(bytes((str(data_matrix) + ',').encode('utf-8')))
    
    sock.close()
