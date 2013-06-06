row = 9
col = 9
mines = 10


started = False
stopped = False
start_time = None
remain_mines = mines
remain_sites = row * col - mines
cursor = [int(row/2), int(col/2)]
mmap = []

steps_buffer = ""
n_key_buffer = 0
q_key_buffer = 0
status_bar = "Remains: "+str(remain_mines)
