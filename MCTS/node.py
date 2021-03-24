from copy import deepcopy
import datetime as dt
import math
import re


def get_time_diff(start):
    return dt.datetime.now() - start


class Node:
    def __init__(self, board, turn, parent=None, approach=None):
        self.board = board
        self.turn = turn
        self.parent = parent
        self.approach = approach
        self.children = list()
        self.positive = list()
        self.simulation_t = 0
        self.beat_t = 0
        self.empty, self.occupied = self.the_board()
        self.about_situation = self.about_situation()
        self.score = self.evaluation()
        self.optimal_pos = self.optimal_pos()

    def the_board(self):
        empty, occupied = list(), list()
        for x in range(20):
            for y in range(20):
                if not self.board[x][y]:
                    empty.append((x, y))
                else:
                    occupied.append((x, y))
        return empty, occupied

    def about_situation(self):

        def if_diff_s(turn):
            former = deepcopy(self.parent.about_situation[turn - 1])
            ((pos1, pos2), t) = self.approach
            ways = [1, 2, 3, 4]
            for way in ways:
                ln = self.parent.about_line(pos1, pos2, way)
                ln = [3] + ln + [3]
                case = self.gather_statistic(turn, ln)
                if case not in former.keys():
                    former[case] = -1
                else:
                    former[case] -= 1

            for way in ways:
                ln = self.about_line(pos1, pos2, way)
                ln = [3] + ln + [3]
                case = self.gather_statistic(turn, ln)
                if case not in former.keys():
                    former[case] = 1
                else:
                    former[case] += 1

            for key in list(former.keys()):
                if not former[key]:
                    del former[key]
            return former

        def situation_detection(turn):
            different_cases = dict()

            for i in range(len(self.board)):
                ln = self.about_line(i, 0, 1)
                ln = [3] + ln + [3]
                case = self.gather_statistic(turn, ln)
                if case not in different_cases.keys():
                    different_cases[case] = 1
                else:
                    different_cases[case] += 1

            for i in range(len(self.board)):
                ln = self.about_line(0, i, 2)
                ln = [3] + ln + [3]
                case = self.gather_statistic(turn, ln)
                if case not in different_cases.keys():
                    different_cases[case] = 1
                else:
                    different_cases[case] += 1

            for i in range(len(self.board)):
                ln = self.about_line(0, i, 3)
                ln = [3] + ln + [3]
                case = self.gather_statistic(turn, ln)
                if case not in different_cases.keys():
                    different_cases[case] = 1
                else:
                    different_cases[case] += 1

            for i in range(1, len(self.board)):
                ln = self.about_line(i, len(self.board) - 1, 3)
                ln = [3] + ln + [3]
                case = self.gather_statistic(turn, ln)
                if case not in different_cases.keys():
                    different_cases[case] = 1
                else:
                    different_cases[case] += 1

            for i in range(len(self.board) - 1, -1, -1):
                ln = self.about_line(i, 0, 4)
                ln = [3] + ln + [3]
                case = self.gather_statistic(turn, ln)
                if case not in different_cases.keys():
                    different_cases[case] = 1
                else:
                    different_cases[case] += 1

            for i in range(1, len(self.board)):
                ln = self.about_line(0, i, 4)
                ln = [3] + ln + [3]
                case = self.gather_statistic(turn, ln)
                if case not in different_cases.keys():
                    different_cases[case] = 1
                else:
                    different_cases[case] += 1
            return different_cases

        if not self.parent:
            return [situation_detection(1), situation_detection(2)]
        return [if_diff_s(1), if_diff_s(2)]

    def about_line(self, r, c, way):
        if way == 1:
            return self.board[r]

        elif way == 2:
            result = list()
            for ln in self.board:
                result.append(ln[c])
            return result

        elif way == 3:
            line = list()
            for i in range(len(self.board)):
                for j in range(len(self.board)):
                    if i + j == r + c:
                        line.append(self.board[i][j])
            return line

        elif way == 4:
            line = list()
            for i in range(len(self.board)):
                for j in range(len(self.board)):
                    if j-i == c-r:
                        line.append(self.board[i][j])
            return line

    def gather_statistic(self, turn, ln):
        answer = list()
        if turn != 1:
            for i in range(len(ln)):
                if ln[i] == 1:
                    ln[i] = 2
                elif ln[i] == 2:
                    ln[i] = 1

        line = list(map(str, ln))
        line = ''.join(line)
        case_id = {'活五': 0, '活四': 1, '活三': 2, '死四': 3, '活二': 4, '死三': 5, '死二': 6, '活一': 7, '死一': 8, 'None': 9}

        if re.findall('11111', line):
            return '活五'
        elif re.findall('011110', line):
            return '活四'
        elif re.findall('[32]11110', line):
            answer.append('死四')
        elif re.findall('01111[32]', line):
            answer.append('死四')
        elif re.findall('11101', line):
            answer.append('死四')
        elif re.findall('10111', line):
            answer.append('死四')
        elif re.findall('01110', line):
            answer.append('活三')
        elif re.findall('[32]11100', line):
            answer.append('死三')
        elif re.findall('00111[32]', line):
            answer.append('死三')
        elif re.findall('[32]01110[32]', line):
            answer.append('死三')
        elif re.findall('11011', line):
            answer.append('死四')
        elif re.findall('010110', line):
            answer.append('活三')
        elif re.findall('011010', line):
            answer.append('活三')
        elif re.findall('01011[23]', line):
            answer.append('死三')
        elif re.findall('[23]11010', line):
            answer.append('死三')
        elif re.findall('01101[23]', line):
            answer.append('死三')
        elif re.findall('[23]10110', line):
            answer.append('死三')
        elif re.findall('0100110', line):
            answer.append('死三')
        elif re.findall('0110010', line):
            answer.append('死三')
        elif re.findall('0110', line):
            answer.append('活二')
        elif re.findall('[23]1100', line):
            answer.append('死二')
        elif re.findall('0011[23]', line):
            answer.append('死二')
        elif re.findall('01010', line):
            answer.append('活二')
        elif re.findall('010010', line):
            answer.append('活二')
        elif re.findall('00101[23]', line):
            answer.append('死二')
        elif re.findall('[23]10100', line):
            answer.append('死二')
        elif re.findall('01001[23]', line):
            answer.append('死二')
        elif re.findall('[23]10010', line):
            answer.append('死二')
        elif re.findall('010', line):
            answer.append('活一')
        elif re.findall('[23]10', line):
            answer.append('死一')
        elif re.findall('01[23]', line):
            answer.append('死一')
        if not answer:
            return 'None'
        for i, j in enumerate(answer):
            answer[i] = (j, case_id[j])
        return sorted(answer, key=lambda x: x[1])[0][0]

    def evaluation(self):
        eva_score = 0
        scores = {'活五': 100000, '活四': 50000, '活三': 500, '死四': 300, '活二': 100, '死三': 50, '死二': 5, '活一': 2, '死一': 1,
                  'None': 0}

        if self.turn == 1:
            us = 1
            oppo = 0
        else:
            us = 0
            oppo = 1
        if self.about_situation[us].get('活五', 0) > 0:
            return 100000
        elif self.about_situation[us].get('活四', 0) > 0:
            return 40000
        elif (self.about_situation[us].get('死四', 0) > 1) or (
                self.about_situation[us].get('死四', 0) > 0 and self.about_situation[us].get('活三', 0) > 0):
            return 20000
        elif self.about_situation[us].get('活三', 0) > 1:
            return 10000
        elif self.about_situation[oppo].get('活四', 0) > 0:
            return -100000
        elif self.about_situation[oppo].get('死四', 0) > 0:
            return -40000
        elif self.about_situation[oppo].get('活三', 0) > 1:
            return -20000
        elif self.about_situation[oppo].get('活三', 0) > 0:
            return -10000
        else:
            for i in self.about_situation[us]:
                eva_score += scores[i] * self.about_situation[us][i]
            for j in self.about_situation[oppo]:
                eva_score -= scores[j] * self.about_situation[oppo][j]
            return eva_score

    def optimal_pos(self):
        if (not self.parent) or (not self.parent.optimal_pos):
            result = list()
            for pos in self.occupied:
                nearby = list()
                size = 2
                for i in range(size):
                    for j in range(size):
                        if (pos[0] + i, pos[1] + j) not in nearby:
                            nearby.append((pos[0] + i, pos[1] + j))
                        if (pos[0] + i, pos[1] - j) not in nearby:
                            nearby.append((pos[0] + i, pos[1] - j))
                        if (pos[0] - i, pos[1] + j) not in nearby:
                            nearby.append((pos[0] - i, pos[1] + j))
                        if (pos[0] + i, pos[1] + j) not in nearby:
                            nearby.append((pos[0] - i, pos[1] - j))
                nearby = set(nearby)
                if len(list(nearby & set(self.empty))) != 0:
                    result.extend(list(nearby & set(self.empty)))
            return result
        else:
            others = deepcopy(self.parent.optimal_pos)
            others.remove(self.approach[0])
            pos = self.approach[0]
            nearby = list()
            size = 2
            for i in range(size):
                for j in range(size):
                    if (pos[0] + i, pos[1] + j) not in nearby:
                        nearby.append((pos[0] + i, pos[1] + j))
                    if (pos[0] + i, pos[1] - j) not in nearby:
                        nearby.append((pos[0] + i, pos[1] - j))
                    if (pos[0] - i, pos[1] + j) not in nearby:
                        nearby.append((pos[0] - i, pos[1] + j))
                    if (pos[0] + i, pos[1] + j) not in nearby:
                        nearby.append((pos[0] - i, pos[1] - j))
            nearby = set(nearby)
            result = list((nearby & set(self.empty) | set(others)))
            return result
