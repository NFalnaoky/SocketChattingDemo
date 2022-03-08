import socket
from threading import Thread
import time
import json# 解析消息字段


ADDRESS = ('127.0.0.1', 8712)  # 地址

# 构造socket对象 
g_socket_server = None  # 负责监听的socket
g_conn_pool = {}  # 连接池来缓存 字典


def accept_client():
    global g_socket_server
    # 构造socket对象  通信协议族 套接字类型
    g_socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    # 绑定/监听接口
    g_socket_server.bind(ADDRESS)
    g_socket_server.listen(5)  # 最大等待数
    print("server start，wait for client connecting...")
    '''
    接收新连接
    '''
    while True:
        client, info = g_socket_server.accept()  # 阻塞，等待客户端连接
        # 给每个客户端创建一个独立的线程进行管理 带离线程 不阻塞线程
        thread = Thread(target=message_handle, args=(client, info))
        # 设置成守护线程
        thread.setDaemon(True)
        thread.start()
 
 
def message_handle(client, info):
    """
    消息处理
    """
    handle_id = info[1]
    # 缓存客户端socket对象
    g_conn_pool[handle_id] = client
    while True:
        try:
            #接受客户端socket消息
            data = client.recv(1024)
            jsonstr = data.decode(encoding='utf8')

            #使用json对消息字段进行解析
            jd = json.loads(jsonstr)
            protocol = jd['protocol']
            uname = jd['uname']

            if 'login' == protocol:
                print('on client login, ' + uname)
                 # 转发给所有客户端
                for u in g_conn_pool:
                    g_conn_pool[u].sendall((uname + " 进入了房间").encode(encoding='utf8'))
            elif 'chat' == protocol:
                # 收到客户端聊天消息
                print(uname + ":" + jd['msg'])
                # 转发给所有客户端
                for key in g_conn_pool:
                    g_conn_pool[key].sendall((uname + " : " + jd['msg']).encode(encoding='utf8'))
        except Exception as e:
            # 抛出异常 断开socket连接 移除缓存的socket对象 
            remove_client(handle_id)
            break

def remove_client(handle_id):
    client = g_conn_pool[handle_id]
    if None != client:
        client.close()
        g_conn_pool.pop(handle_id)
        print("client offline: " + str(handle_id))


if __name__ == '__main__':
    # 新开一个线程，用于接收新连接
    thread = Thread(target=accept_client)
    thread.setDaemon(True)
    thread.start()
    # 主线程逻辑 循环确保主线程不退出
    while True:
        time.sleep(0.1)
        

