from command_parser import parse_command
import socket
from command_handler import handle_command, resp_error
from gevent.server import StreamServer

def read_from_client(s, address):
    '''
    处理客户端传入的命令，将他们发送到命令解析器中解析后发送到命令处理器中处理
    然后输出到客户端
    
    Arguments:
        s {[type]} -- 客户端传入的命令
        address {[type]} --
    '''

    while True:
        try:
            data = s.recvfrom(65536) # 从客户端读取socket套接字
            if data is not None and data[0] is not None:
                try:
                    command_arr = parse_command(data[0].decode('utf-8'), 0) # 解析客户端传入的命令
                    response = handle_command(command_arr)
                    s.send(bytes(response, 'utf-8'))
                except socket.error:
                    raise
                except Exception as e:
                    s.send(bytes(resp_error("An unspecified error occurred. {0}".format(str(e))), 'utf-8'))
        except socket.error:
            print(socket.error)
            break
    s.close()


def bind_server(ip, port, spawn_limit):
    '''创建一个服务器
    
    Arguments:
        ip {[type]} -- [description]
        port {[type]} -- [description]
        spawn_limit {[type]} -- [description]
    '''
    try:
        server = StreamServer((ip, port), read_from_client, spawn=spawn_limit) # 创建一个服务器
        server.serve_forever() # 启动服务器一直等待，知道终端或服务端终止
    except Exception as e:
        print(str(e))
        server.close() if server is not None and server.started else None
