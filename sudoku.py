############################################################
# Imports
############################################################

import random
import time
import os
import copy

############################################################
//Sudoku Solver
############################################################

def sudoku_cells():
    return [(row, col) for row in range(9) for col in range(9)]

def sudoku_arcs():
    box_map = {0:0, 1:0, 2:0, 3:3, 4:3, 5:3, 6:6, 7:6, 8:6}
    arcs = []
    for row1, col1 in sudoku_cells():
        for col2 in range(9):
            if col2 != col1:
                arcs.append(((row1, col1), (row1, col2)))
        for row2 in range(9):
            if row2 != row1:
                arcs.append(((row1, col1), (row2, col1)))
        r_start, c_start = box_map[row1], box_map[col1]
        for row3 in range(r_start, r_start+3):
            for col3 in range(c_start, c_start+3):
                if row3 != row1 and col3 != col1:
                    arcs.append(((row1, col1), (row3, col3)))
    return arcs
    
def read_board(path):
    board = {}
    with open(path, 'r+') as f:
        row = 0
        for ele in f:
            col = 0
            for num in ele.rstrip('\r\n'):
                if num != '*':
                    board[(row, col)] = set([int(num)])
                else:
                    board[(row, col)] = set([1, 2, 3, 4, 5, 6, 7, 8, 9])
                col += 1
            row += 1
    return board

class Sudoku(object):

    CELLS = sudoku_cells()
    ARCS = sudoku_arcs()

    def __init__(self, board):
        self.board = board
        self.mod = False

    def get_values(self, cell):
        return self.board[cell]
        
    def remove_inconsistent_values(self, cell1, cell2):
        modified = False
        c2_list = self.board[cell2]
        if cell1 == cell2:
            return modified
        c1_list = self.board[cell1]
        for ele in tuple(c1_list):
            if len([_ for _ in c2_list if _ != ele]) > 0:
                continue
            else:
                modified = True
                self.modified = True
                c1_list.remove(ele)
        return modified
    
    def infer_ac3(self):
        queue = set()
        for arc in self.ARCS:
            if not self.certain(arc[0]) and self.certain(arc[1]):
                queue.add(arc)
        while queue:
            first = queue.pop()
            if self.remove_inconsistent_values(first[0], first[1]):
                if self.certain(first[0]):
                    for arc in self.ARCS:
                        if arc[1] == first[0] and not self.certain(arc[0]):
                            queue.add(arc)

    def infer_improved(self):
        self.infer_ac3()
        while self.helper1():
            self.infer_ac3()
 
    def infer_with_guessing(self):
        if not self.infer_improved():
            return False
        if max(map(len, self.board.values()))==1:
            return True
        cur = {ele:val for ele, val in self.board.items() if len(val)>=2}
        sol = self.helper2({}, cur)
        if sol:
            for ele, val in sol.items():
                self.board[ele] = {val}
            return True
        return False

    def helper1(self):
        self.mod = False
        if not self.check():
            return self.mod
        for cell in self.CELLS:
            if len(self.board[cell]) >= 2:
                for ele in self.board[cell]:
                    altered = True
                    for col in range(9):
                        hold = (cell[0], col)
                        if cell == hold:
                            continue
                        if ele in self.board[hold]:
                            altered = False 
                            break
                    if altered:
                        self.board[cell] = set([ele])
                        self.mod = True
                        break
                    altered = True
                    for row in range(9):
                        hold = (row, cell[1]) 
                        if cell == hold:
                            continue
                        if ele in self.board[hold]:
                            altered = False
                            break
                    if altered:
                        self.board[cell] = set([ele])
                        self.mod = True
                        break
                    altered = True
                    col = cell[1] / 3 * 3
                    row = cell[0] / 3 * 3
                    for delta_row in range(3):
                        for delta_col in range(3):
                            hold = (row + delta_row, col + delta_col)
                            if hold == cell:
                                continue
                            if ele in self.board[hold]:
                                altered = False
                                break
                    if altered:
                        self.board[cell] = set([ele])
                        self.mod = True
                        break
        return self.mod

    def helper2(self, sol, current):
        if len(current) == 0:
            return sol
        temp = {ele:[] for ele in range(2,10)}
        for tup, val in current.items():
            temp[len(val)].append(tup)
        temp = {ind:val for ind, val in temp.items() if len(val)>=1}
        r = random.choice(temp[min(temp.keys())])
        for value in current[r]:
            for tup, val in sol.items():
                if value == val and (r, tup) in self.ARCS:
                    continue
            sol[r] = val
            hold_q = current.pop(r)
            b_copy = copy.deepcopy(self)
            b_copy.board[r] = {value}
            temp_d = {tup for tup,val in b_copy.board.items() if len(val)==1}
            update = set()
            if b_copy.infer_improved():
                temp_d2 = {tup for tup,val in b_copy.board.items() if len(val)==1}
                update = temp_d2 - temp_d
                for ele in update:
                    sol[ele] = b_copy.get_values(ele)
                final = b_copy.helper2(sol, current) #recursion
                if final:
                    return final
            sol.pop(r)
            for ele in update:
                sol.pop(ele)
            current[r] = hold_q
        return False
    
    def certain(self, cell):
        if len(self.board[cell]) == 1:
            return True
        return False
        
    def check(self):
        for cell in self.CELLS:
            if len(self.board[cell]) == 0:
                return False
        return True
