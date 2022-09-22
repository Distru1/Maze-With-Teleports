import curses
from curses import wrapper
import queue
import os

# P is starting point, K is the key necessary to open the exit, E is the exit

maze=[
['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'], 
['#', '.', '.', '#', '.', '.', '.', '.', '.', '#', '#', '#', '.', '#', '.', '.', '#', '.', '.', '#'], 
['#', '#', '#', '.', '#', '#', '#', '.', '.', '#', '#', '#', '#', '#', '#', '.', '.', '.', '#', '#'], 
['#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '.', '.', '.', '#', '.', '#', '#'], 
['#', '.', '.', '#', '.', '.', '#', '.', '.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#'], 
['#', '.', '.', '#', '#', '.', '.', '.', '.', '#', '#', '.', '#', '.', '#', '.', '#', '.', '#', '#'], 
['#', '#', '.', '#', '#', '.', '#', '.', '#', '.', 'K', '.', '#', '#', '.', '.', '.', '.', '#', '#'], 
['#', '.', '#', '.', '#', '.', '#', '.', '#', '.', '.', '.', '.', '#', '#', '#', '.', '.', '.', '#'], 
['#', '.', '#', '.', '.', '.', '.', '.', '.', '.', '#', '.', '.', '#', '.', '.', '.', '.', '.', '#'], 
['#', '.', '#', '.', '.', '.', '.', '.', '.', '.', '#', '.', '.', '#', '.', '#', '.', '#', '#', '#'], 
['#', '.', '#', '.', '.', '#', '.', '#', '.', '#', '.', '.', '#', '.', '.', '.', '.', '.', '.', '#'], 
['#', '.', '.', '.', '.', '.', '.', '#', '#', '.', '.', '.', '.', '#', '.', '.', '.', '.', '.', '#'], 
['#', '.', '.', '.', '#', '#', '.', '.', '.', '.', '.', '#', '#', '.', '.', '#', '#', '.', '.', '#'], 
['#', '#', '#', '.', '.', '.', '.', '#', '#', '#', '#', '.', '.', '.', '#', '.', '#', '.', '#', '#'], 
['#', '.', '#', '.', '.', '#', '.', '#', '.', '.', '.', '.', '.', '#', '.', '.', '.', '.', '.', '#'], 
['#', '.', '.', '#', '.', '.', '.', '#', '.', '.', '#', '#', '.', '#', '.', '#', '.', '.', '#', '#'], 
['#', 'P', '#', '.', '.', '.', '.', '#', '.', '.', '#', '#', '.', '#', '.', '.', '.', '.', '.', '#'], 
['#', '.', '.', '.', '#', '.', '#', '.', '#', '.', '#', '.', '.', '.', '#', '.', '.', '#', '.', '#'], 
['#', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '#', '.', '#', '#', '#'], 
['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', 'E', '#', '#', '#', '#', '#', '#']
]

def print_maze(maze, stdscr, path=[]):          #Print maze before having key - RED path
    BLUE = curses.color_pair(1)
    RED = curses.color_pair(2)

    for i, row in enumerate(maze):
        for j, value in enumerate(row):
            if (i, j) in path:
                try:
                    stdscr.addstr(i, j*2, "X", RED)
                except curses.error:
                    pass
            else:
                try:
                    stdscr.addstr(i, j*2, value, BLUE)
                except curses.error:
                    pass

def print_maze_ak(maze, stdscr, path=[]):           #Print maze after having key - GREEN path
    BLUE = curses.color_pair(1)
    GREEN = curses.color_pair(3)

    for i, row in enumerate(maze):
        for j, value in enumerate(row):
            if (i, j) in path:
                try:
                    stdscr.addstr(i, j*2, "X", GREEN)
                except curses.error:
                    pass
            else:
                try:
                    stdscr.addstr(i, j*2, value, BLUE)
                except curses.error:
                    pass


def find_start(maze, start):
    for i, row in enumerate(maze):              #i is number of row, row is the complete row
        for j, value in enumerate(row):             #j is the number of column, value is the character in the column
            if value == start:
                return i, j

    return None


def find_path(maze, stdscr):
    start = "P"
    key = "K"
    end = "E"
    
    start_pos = find_start(maze, start)

    q = queue.Queue()
    q.put((start_pos, [start_pos], start_pos))

    visited = set()

    while not q.empty():                                    #Process to find KEY
        current_pos, path, last_tp = q.get()
        row, col = current_pos
        #time.sleep(0.1)
        stdscr.clear()
        print_maze(maze, stdscr, path)
        stdscr.refresh()   
 
        if maze[row][col] == key:                           #If KEY is found
            final_path=path
            break

        neighbors = find_neighbors(maze, row, col)          #Find next step (1)
        for neighbor in neighbors:
            if neighbor in visited:
                continue

            new_path = path + [neighbor]
            q.put((neighbor, new_path, last_tp))
            visited.add(neighbor)
        
        neighbors = find_tps(maze, row, col, last_tp)       #Find next step(teleport)
        for neighbor in neighbors:
            if neighbor[0] in visited:
                continue

            new_path = path + [neighbor[0]]
            q.put((neighbor[0], new_path, neighbor[1]))
            visited.add(neighbor[0])
    
    visited.clear()                                             #Clear visited spots
    with q.mutex: q.queue.clear()                               #Clear queue after finding the key
    
    start_pos=row,col
    q.put((start_pos, [start_pos],last_tp))
    
    while not q.empty():                                    #Process to find EXIT
        current_pos, path, last_tp = q.get()
        row, col = current_pos
        #time.sleep(0.1)
        stdscr.clear()
        print_maze_ak(maze, stdscr, path)
        stdscr.refresh()

        if maze[row][col] == end:                           #If END is found, return path
            return final_path+path

        neighbors = find_neighbors(maze, row, col)          #Find next step (1)
        for neighbor in neighbors:
            if neighbor in visited:
                continue

            new_path = path + [neighbor]
            q.put((neighbor, new_path, last_tp))
            visited.add(neighbor)
        
        neighbors = find_tps(maze, row, col, last_tp)           #Find next step(teleport)
        for neighbor in neighbors:
            if neighbor[0] in visited:
                continue

            new_path = path + [neighbor[0]]
            q.put((neighbor[0], new_path, neighbor[1]))
            visited.add(neighbor[0])
    ERROR = "NOT SOLVED"
    return ERROR

def find_neighbors(maze, row, col):
    neighbors = []

    try:                        #Check UP for wall
        if maze[row-1][col]!="#":       
            neighbors.append((row-1,col))
    except IndexError:
        pass
    try:                        #Check Down for wall 
        if maze[row+1][col]!="#":       
            neighbors.append((row+1,col))
    except IndexError:
        pass
    try:                        #Check Left for wall
        if maze[row][col-1]!="#":       
            neighbors.append((row,col-1))   
    except IndexError:
        pass
    try:                         #Check Right for wall
        if maze[row][col+1]!="#":       
            neighbors.append((row,col+1))  
    except IndexError:
        pass

    return neighbors
    
def find_tps(maze, row, col, last_tp):
    neigh_tps=[]
    copy_last_tp=last_tp
    steps=0
    left = False
    right = False
    up = False
    down = False
    tp = False

    try:                        #Check UP for wall
        if maze[row-1][col]=="#":       
            tp = True
        else:
            up = True
    except IndexError:
        pass
    try:                        #Check Down for wall 
        if maze[row+1][col]=="#":       
            tp = True
        else:
            down = True
    except IndexError:
        pass
    try:                        #Check Left for wall
        if maze[row][col-1]=="#":       
            tp = True   
        else:
            left = True
    except IndexError:
        pass
    try:                         #Check Right for wall
        if maze[row][col+1]=="#":       
            tp = True
        else:
            right = True
    except IndexError:
        pass
    
    if up and tp:
        while True:  #check for amount of spaces up
            try: 
                if row == 0:
                    row = row + steps 
                    steps = 0
                    break
                if maze[row-1][col]=="#":
                    break
            except: 
                row = row + steps
                steps = 0
                break
            row = row - 1
            steps+=1
        if steps >= 2:          #if two or more spaces, save that position(new) and previous
            last_tp = row+steps, col
            neigh_tps.append([(row,col),last_tp])
            last_tp=copy_last_tp
        if steps==0 and last_tp[0]<row:
            new_tp = row, col
            neigh_tps.append([(last_tp[0],col),new_tp])
        row = row + steps
        steps = 0
    if down and tp:
        while True:  #check for amount of spaces down
            try: 
                if maze[row+1][col]=="#":
                    break
            except: 
                row = row - steps
                steps = 0
                break
            row = row + 1
            steps+=1
        if steps >= 2:
            last_tp = row-steps, col
            neigh_tps.append([(row,col),last_tp])
            last_tp=copy_last_tp
        if steps==0 and last_tp[0]>row:
            new_tp = row, col
            neigh_tps.append([(last_tp[0],col),new_tp])
        row = row - steps
        steps = 0
    if left and tp:
        while True:  #check for amount of spaces left
            try: 
                if col == 0:
                    col = col + steps 
                    steps = 0
                    break
                if maze[row][col-1]=="#":
                    break
            except: 
                col = col + steps 
                steps = 0
                break
            col = col - 1
            steps+=1
        if steps >= 2:
            last_tp = row, col+steps
            neigh_tps.append([(row,col),last_tp])
            last_tp=copy_last_tp
        if steps==0 and last_tp[1]<col:
            new_tp = row, col
            neigh_tps.append([(row,last_tp[1]),new_tp])
        col = col + steps
        steps = 0
    if right and tp:
        while True:  #check for amount of spaces right
            try: 
                if maze[row][col+1]=="#":
                    break
            except: 
                steps = 0
                col = col - steps
                break
            col = col + 1
            steps+=1
        if steps >= 2:
            last_tp=row,col-steps
            neigh_tps.append([(row,col),last_tp])
            last_tp=copy_last_tp
        if steps==0 and last_tp[1]>col:
            new_tp=row,col
            neigh_tps.append([(row,last_tp[1]),new_tp])
    
    return neigh_tps


def main(stdscr):
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)

    a = find_path(maze, stdscr)
    print("number of steps:",len(a)-2)          #Len -2 because there we don't count the first spot as a step, and there is a repetition of entry after finding the key
    print("steps log:",a[1:len(a)])             #One step is repeated, it's the position of the key
    stdscr.getch()

wrapper(main)
