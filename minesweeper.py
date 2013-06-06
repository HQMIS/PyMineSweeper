import urwid
import time
import random
import gl

def init():
    gl.started = False
    gl.stopped = False
    gl.start_time = None
    gl.remain_mines = gl.mines
    gl.remain_sites = gl.row * gl.col - gl.mines  
    gl.cursor = [int(gl.row/2), int(gl.col/2)]
    gl.steps_buffer = "" #used to trace the inputed digits
    gl.n_key_buffer = 0  #used to count the inputed "n"
    gl.q_key_buffer = 0  #used to count the inputed "q"
    gl.mmap = []
    gl.status_bar = "Remains: "+str(gl.remain_mines)

    for x in range(gl.row):
        single_row = []
        for y in range(gl.col):
            single_row.append([0, " * "])     
            #For each site,  there are two values
            #The first value is the real status
            #    == number : the number of mines that surround the site
            #    == "mine" : the site is a mine
            #The second value is the displayed status
            #    == number : the number of mines that surround the site
            #    == " * "  : the site has not be revealed
            #    == " M "  : the site was marked as a mine
            #    == " X "  : the site is a mine and it exploded
        gl.mmap.append(single_row)

def start(x, y):
    gl.started = True
    gl.start_time = time.time()
    linear_mmap = list(range(gl.row*gl.col))
    linear_mmap = list(set(linear_mmap) - set([x*gl.col+y])) #start spot must not be a mine.
    mine_sites = random.sample(linear_mmap, gl.mines)      #lay mines randomly
    for i in mine_sites:     #fill mmap with the mines
        x = int(i/gl.col)
        y = int(i%gl.col)
        gl.mmap[x][y][0] = "mine"
        for d in range(9):   #update the number of surrounded sites
            dx = x + int(d/3) - 1
            dy = y + d%3 - 1
            if 0<=dx<gl.row and 0<=dy<gl.col:
                if gl.mmap[dx][dy][0] != "mine":
                    gl.mmap[dx][dy][0] += 1

palette = [
    ('default_color', 'default', 'default'),
    ('cursor_color', 'dark red', 'default'),
    ('unreveald_color', 'dark green', 'default'),
    ('marked_color', 'light green', 'default'),
    ('exploded_color', 'light red', 'default', 'bold'),]

def draw():
    dmap = []
    for x in range(gl.row):
        for y in range(gl.col):
            mvalue = gl.mmap[x][y][1]
            gl.color = 'default_color'
            if mvalue == u" * ":
                gl.color = 'unreveald_color'
            elif mvalue == u" M ":
                gl.color = 'marked_color'
            if x==gl.cursor[0] and y == gl.cursor[1]:
                gl.color = 'cursor_color'
            if mvalue == u" X ":
                gl.color = 'exploded_color'
            dmap.append((gl.color, mvalue))
        dmap.append(u"\n")
    dmap.append(u"\n")
    dmap.append(gl.status_bar)

    display.set_text(dmap)


def explode(x, y):
    gl.mmap[x][y][1] = u" X "
    gl.stopped = True

def reveal(x, y, deep):
    if gl.started == False:
        start(x, y)
    value = gl.mmap[x][y][0]
    if value == "mine":
        explode(x, y)
        return
    if gl.mmap[x][y][1] == u" * ":
        gl.mmap[x][y][1] = u" "+str(value)+u" "
        gl.remain_sites -= 1
    
    real_mines = 0
    marked_mines = 0
    for d in range(9):
        if d==4:
            continue
        dx = x + int(d/3) - 1
        dy = y + d%3 - 1
        if 0 <= dx < gl.row and 0 <= dy < gl.col:
            if gl.mmap[dx][dy][1] == u" M ":
                marked_mines += 1
            if gl.mmap[dx][dy][0] == "mine":
                real_mines += 1
    #If the correct number of mines have been flagged around the site, 
    #then the remaining surrounding sites will be auto-revealed recursively.
    #But in this case if a site is flagged in error, 
    #a real mine around the site will explode immediately.
    if real_mines == marked_mines:
        for d in range(9):
            if d==4:
                continue
            dx = x + int(d/3) - 1
            dy = y + d%3 - 1
            if 0 <= dx < gl.row and 0 <= dy < gl.col:
                if gl.mmap[dx][dy][1] == u" * ":
                    reveal(dx, dy, deep+1)

def succeed():
    gl.stopped = True
    time_itv = time.time() - gl.start_time
    time_str = "%.2f" % float(time_itv)
    gl.status_bar = "You survived with "+time_str+" seconds!"
    draw()

move_key = "hjkl"
move_dir = [[1, -1], [0, 1], [0, -1], [1, 1]]
def key_press(key):
    if key == 'n':                 
        if gl.n_key_buffer == 2:
            init()
            draw()
        else:
            gl.n_key_buffer += 1
    else:
        gl.n_key_buffer = 0

    if key == 'q':                  
        if gl.q_key_buffer == 2:
            raise urwid.ExitMainLoop()
        else:
            gl.q_key_buffer += 1
    else:
        gl.q_key_buffer = 0

    if gl.stopped == True: #Do not response for below keys after stopped
        return

    if key in move_key:           
        direction = move_dir[move_key.find(key)]
        steps = 1
        if gl.steps_buffer != "":
            steps = int(gl.steps_buffer)
        gl.cursor[direction[0]] += (direction[1] * steps)
        gl.cursor[0] = max(0, gl.cursor[0])
        gl.cursor[0] = min(gl.row-1, gl.cursor[0])
        gl.cursor[1] = max(0, gl.cursor[1])
        gl.cursor[1] = min(gl.col-1, gl.cursor[1])
        draw()
    if key.isdigit():
        gl.steps_buffer += key
    else:
        gl.steps_buffer = ""

    if key == '0':
        gl.cursor[1] = 0
        draw()
    if key == '$':
        gl.cursor[1] = gl.col - 1
        draw()

    if key == 'i':
        x = gl.cursor[0]
        y = gl.cursor[1]
        if gl.mmap[x][y][1] == u" * ":
            gl.mmap[x][y][1] = u" M "
            gl.remain_mines -= 1
            gl.status_bar = "Remains: "+str(gl.remain_mines)
            draw()
    if key == 'u':
        x = gl.cursor[0]
        y = gl.cursor[1]
        if gl.mmap[x][y][1] == u" M ":
            gl.mmap[x][y][1] = u" * "
            gl.remain_mines += 1
            gl.status_bar = "Remains: "+str(gl.remain_mines)
            draw()
    if key == ' ':
        x = gl.cursor[0] 
        y = gl.cursor[1]
        if gl.mmap[x][y][1] == u" M ":  #to reveal a marked mine does equal to cancel the mark
            gl.mmap[x][y][1] = u" * "
            gl.remain_mines += 1
            draw()
        else:
            reveal(x, y, 0)
            draw()
    if gl.remain_sites == 0 and gl.remain_mines == 0: #if the game finished successfully
        succeed()


display = urwid.Text(u"", align="center")
init()
draw()
fill = urwid.Filler(display, 'middle')
loop = urwid.MainLoop(fill, palette, unhandled_input=key_press)
loop.run()
