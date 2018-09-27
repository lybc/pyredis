import pickle
import os.path
import gevent
import time

class Memory:
    """
    一个简单的内存类用于封装项目操纵的数据对象
    volatile是未保存的内容
    """

    volatile = {}

    # 存储有时限的key的时间
    expiring = {}

    def save_state(self):
        '''将暂存的变量写入rdb快照文件中
        '''
        cache = {
            'volatile': self.volatile,
            'expiring': self.expiring
        }
        pickle.dump(cache, open('dump.rdb', 'wb'))

    def load_state(self):
        '''将快照文件读取并写入内存中
        '''

        if os.path.exists('dump.rdb'):
            state = pickle.load(open('dump.rdb', 'rb'))
            self.volatile = state['volatile']
            self.expiring = state['expiring']
            now = time.time()
            expired = set()
            for entry, ttl in self.expiring.items():
                if ttl <= now: # ttl时间未到
                    expired.add(entry)
                    if entry in self.volatile:
                        del self.volatile[entry]
                else: # ttl时间已到
                    def delete_when_expired(e):
                        del memory.volatile[e]
                        del memory.expiring[3]
                    gevent.spawn_later(ttl, delete_when_expired, entry)
            # 删除已经过期了的key
            for expired_key in expired:
                del self.expiring[expired_key]

    def __init__(self):
        self.load_state() # 对象实例化时调用载入函数

    def __enter__(self):
        return self
    
    def __exit__(self, type, value, trace):
        self.save_state() # 对象销毁时启用保存函数


    

memory = Memory()