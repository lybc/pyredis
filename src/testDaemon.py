import os, sys, time

from daemon import Daemon

PID_FILE = '/tmp/testDaemon.pid'

class TestDaemon(Daemon):
    def run(self):
        while True:
            sys.stdout.write('%s: hello world\n' % (time.ctime(), ))
            sys.stdout.flush()
            time.sleep(1)


if __name__ == '__main__':
    daemon = TestDaemon(PID_FILE)
    
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            print('Starting daemon...')
            daemon.start()
        elif 'stop' == sys.argv[1]:
            print('Stopping daemon...')
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            print('Restarting daemon...')
            daemon.restart()
        else:
            print('Unknow command')
            sys.exit(2)
        sys.exit(0)
    else:
        print('usage: {0} start|stop|restart'.format(sys.argv[0]))
        sys.exit(2)

    