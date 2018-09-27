from memory import memory
import gevent
import time

def resp_string(val):
    return "+" + val + "\r\n"

def resp_bulk_string(val):
    return "$" + str(len(val)) + "\r\n" + val + "\r\n"

def resp_error(val):
    return "-" + val + "\r\n"

def resp_integer(val):
    return ":" + str(val) + "\r\n"

def resp_array(arr):
    val = "*" + str(len(arr)) + "\r\n"
    for item in arr:
        if isinstance(val, list):
            val += resp_array(item)
        else:
            val += item
    return val


def not_implemented_command():
    return resp_error("NOT IMPLEMENTED")

def no_such_key(key):
    return resp_error('NO SUCK KEY {0} EXISTS'.format(key))


def set_command(key, args):
    '''实现对一个key的value简单集合
    
    Arguments:
        key {[type]} -- [description]
        args {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    '''

    memory.volatile[key] = args[0]
    return resp_bulk_string("OK")

def get_command(key):
    '''获取一个key的值
    
    Arguments:
        key {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    '''

    return resp_bulk_string(memory.volatile[key])


def ttl_command(key):
    if key in memory.expiring:
        return resp_integer(int(memory.expiring[key]-time.time())) # 返回剩余时间
    else:
        return resp_error("NO KEY MATCHING {0} HAS AN EXPIRATION SET".format(key))

def expire_command(key, args):
    def delete_when_expired(k):
        del memory.volatile[k]
        del memory.expiring[k]
    
    if key in memory.volatile:
        memory.expiring[key] = time.time() + int(args[0]) # 设置到期时间
        gevent.spawn_later(int(args[0]), delete_when_expired, key) # 时间到时删除key
        return resp_bulk_string("OK")
    else:
        return no_such_key(args)



def list_get(L, i, v=None):
    try:
        return L[i]
    except IndexError:
        return v;

def handle_command(command_with_args):
    command = str(command_with_args[0]).upper()
    if command not in command_map:
        return not_implemented_command()
    matched_command = command_map[command]
    args = command_with_args[2:] or []
    key = list_get(command_with_args, 1, None)
    total_arg_length = len(args) + (1 if key is not None else 0)

    if total_arg_length < matched_command['min']:
        return resp_error("Too many arguments for command {0}, maximum {1}".format(command, matched_command("min")))
    
    if matched_command["max"] >= 0:
        if total_arg_length > matched_command["max"]:
            return resp_error("Too many arguments for command {0}, maximum {1}".format(command, matched_command("min")))
    else:
        if matched_command["max"] == -3 and not total_arg_length % 2:
            return resp_error("Not enough arguments or an invalid number of arguments was specified")

    if len(args) > 0:
        return command_map[command]["function"](key, args)
    elif key is not None:
        return command_map[command]["function"](key)
    else:
        return command_map[command]["function"]()


command_map = {
    # "COMMAND": {"min": 0, "max": 0, "function": output_commands},
    "SET": {"min": 2, "max": 2, "function": set_command},
    "GET": {"min": 1, "max": 1, "function": get_command},
    "EXPIRE": {"min": 2, "max": 2, "function": expire_command},
    "TTL": {"min": 1, "max": 1, "function": ttl_command},
}