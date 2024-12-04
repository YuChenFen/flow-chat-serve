import random

def get_room_id() -> str:
    return ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=24))
