
def parse_array(array, size):
    arr = []
    for i in range(0, len(array), 2):
        if command_map.get(array[i][0]) is not None:
            arr.append(command_map.get(array[i][0])(array[i:i+2]))
        else:
            print(array[i])
    return arr
    pass

def parse_simple_string(array):
    return array[1]
    pass

def parse_bulk_string(array):
    string_byte_len = int(array[0][1:])
    if string_byte_len > 0:
        return array[1]
    else:
        return None
    pass

def parse_error(array):
    return array[1]
    pass

def parse_int(array):
    '''解析整数
    '''
    return int(array[1])
    pass


def parse_command(command, index):
    '''每次用户输入命令时调用函数，将命令转为RESP数组，然后传递给命令处理程序
    
    Arguments:
        command {str} -- 命令字符串
        index
    
    Returns:
        list -- 命令数组
    '''

    items = command.split("\r\n") # 去除换行符
    items= list(filter(lambda x: x, items)) # 生成列表，返回的是items中为True的值
    array_size = int(items[0][1:])
    command_arr = parse_array(items[1:], array_size)
    return command_arr


command_map = {
    '*': parse_array,
    '+': parse_simple_string,
    '$': parse_bulk_string,
    '-': parse_error,
    ':': parse_int
}