import time

def get_now():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def get_timestamp(time_str):
    return int(time.mktime(time.strptime(time_str, "%Y-%m-%d %H:%M:%S")))