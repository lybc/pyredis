import sys
import os
import time
import atexit
import signal
from logger import logger

class Daemon:
    def __init__(self, pidfile):
        self.pidfile = pidfile # 进程控制文件

    def daemonize(self):
        '''守护进程方法
        实现方法基于《Advanced Programming in the unit environment section》中关于守护进程的实现规范
        '''
        try:
            pid = os.fork() # fork子进程
            if pid > 0:
                sys.exit(0) # 父进程退出
        except OSError as err:
            sys.stderr.write('fork #1 failed: {0}\n'.format(err))
            sys.exit(1)

        # 使进程脱离父环境的会话
        os.chdir('/')
        os.setsid()
        os.umask(0)

        try:
            pid = os.fork() # fork子进程
            if pid > 0:
                sys.exit(0) # 父进程退出
        except OSError as err:
            sys.stderr.write('fork #2 failed: {0}\n'.format(err))
            sys.exit(1)

        # 进程已经是守护进程了，重定向标准文件描述符
        sys.stdout.flush()
        sys.stderr.flush()
        
        stdin = open(os.devnull, 'r')
        stdout = open(os.devnull, 'a+')
        stderr = open(os.devnull, 'a+')

        # dup2函数原子化关闭和复制文件描述符
        os.dup2(stdin.fileno(), sys.stdin.fileno())
        os.dup2(stdout.fileno(), sys.stdout.fileno())
        os.dup2(stderr.fileno(), sys.stderr.fileno())

        # 注册守护进程退出的回调函数
        atexit.register(self.delpid)

        # 把进程号写入pidfile
        pid = str(os.getpid())
        with open(self.pidfile, 'w+') as f:
            f.write(pid + '\n')
        pass

    def delpid(self):
        '''删除PID文件
        '''
        os.remove(self.pidfile)

    
    def start(self):
        '''开启守护进程
        '''
        # 判断守护进程是否存在，如果存在则报错
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None
            pass
        
        if pid:
            message = 'pidfile {0} already exist.' + \
                        'Daemon already running?\n'
            sys.stderr.write(message.format(self.pidfile))
            sys.exit(1)
        self.daemonize()
        self.run()


    def stop(self):
        '''关闭守护进程
        '''
        # 判断守护进程是否存在，如果不存在报错
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None
        
        if not pid:
            message = 'pidfile {0} does not exist. ' + \
                        'Daemon not running? \n'
            sys.stderr.write(message.format(self.pidfile))
            return

        # 如果存在则关闭进程，根据进程号发送kill信号
        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            e = str(err.args)
            if e.find('No such process') > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print(str(err.args))
                sys.exit(1)
            pass

    def restart(self):
        '''重启守护进程
        '''

        self.stop()
        self.start()

    def run(self):
        '''运行方法
        当使用子类集成Daemon，可以通过重构该方法让子类成为守护进程
        '''

        pass