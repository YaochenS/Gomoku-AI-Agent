import node as nd
from copy import deepcopy
import datetime as dt


def get_value(board):
    state = nd.Node(board, 1)
    start = dt.datetime.now()
    the_state = deepcopy(state)
    count = 0
    while (nd.get_time_diff(start)).seconds < 3:
        next_state = selection(the_state)
        if not next_state:
            expansion(the_state)
            if len(the_state.children) == 1:
                selected = the_state.children[0]
                break
            else:
                simulation(the_state, start)
                selected = selection(the_state)
                continue
        else:
            compare = deepcopy(next_state)
            while len(next_state.children) != 0:
                next_state = selection(next_state)
            expansion(next_state)
            simulation(next_state, start)
            selected = selection(the_state)
            if compare.approach == selected.approach:
                if count != 1:
                    count += 1
                else:
                    break
    return selected.approach[0]


def selection(node):
    be_positive(node)
    sum_positive = sum(node.positive)
    if len(node.children) == 0:
        return None
    elif len(node.children) == 1:
        return node.children[0]
    else:
        selected = node.children[0]
        if sum_positive == 0:
            if selected.simulation_t == 0:
                optimal = 1/2
            else:
                optimal = selected.beat_t / selected.simulation_t
            for i in range(1, len(node.children)):
                cur = node.children[i]
                if cur.simulation_t == 0:
                    new = 1/2
                else:
                    new = cur.beat_t / cur.simulation_t
                if new > optimal:
                    optimal = new
                    selected = cur
        else:
            if selected.simulation_t == 0:
                optimal = node.positive[0] / sum_positive
            else:
                optimal = node.positive[0] / sum_positive + selected.beat_t / selected.simulation_t
            for i in range(1, len(node.children)):
                cur = node.children[i]
                if cur.simulation_t == 0:
                    new = node.positive[i] / sum_positive
                else:
                    new = node.positive[i] / sum_positive + cur.beat_t / cur.simulation_t
                if new > optimal:
                    optimal = new
                    selected = cur
        return selected


def expansion(node):

    if len(node.occupied) == 0:
        new_board = deepcopy(node.board)
        new_board[10][10] = node.turn
        node.children.append(nd.Node(new_board, (3 - node.turn), parent=node, approach=((10, 10), node.turn)))

    else:
        multi_list = [[], [], [], [], [], []]
        for pos in node.optimal_pos:
            new_board = deepcopy(node.board)
            new_board[pos[0]][pos[1]] = (3 - node.turn)
            after_oppo = nd.Node(new_board, node.turn, parent=node, approach=(pos, (3 - node.turn)))
            new_board[pos[0]][pos[1]] = node.turn
            after_us = nd.Node(new_board, (3 - node.turn), parent=node, approach=(pos, node.turn))
            if after_us.score == 100000:
                node.children = [after_us]
                break
            elif after_oppo.score == 100000:
                multi_list[0].append((after_us, after_oppo.score))
            elif after_us.score >= 20000:
                multi_list[1].append((after_us, after_us.score))
            elif after_oppo.score >= 20000:
                multi_list[2].append((after_us, after_oppo.score))
            elif after_us.score == 10000:
                multi_list[3].append((after_us, after_us.score))
            elif after_oppo.score == 10000:
                multi_list[4].append((after_us, after_oppo.score))
            else:
                multi_list[5].append(after_us)

        if after_us.score != 100000:
            null = 0
            for i in range(5):
                if not multi_list[i]:
                    null += 1
            if null == 5:
                node.children = []
            else:
                for i in range(5):
                    if multi_list[i]:
                        multi_list[i].sort(key=lambda x: x[1], reverse=True)
                        node.children = [multi_list[i][0][0]]
                        break

            if not node.children:
                number = min(len(multi_list[5]), 3)
                multi_list[5].sort(key=lambda x: x.score, reverse=True)
                for i in range(number):
                    node.children.append(multi_list[5][i])


def be_positive(node):
    result = []
    small = 9999999

    for child in node.children:
        score = child.score
        result.append(score)
        if score < small:
            small = score

    for i in range(len(result)):
        result[i] -= small
    node.positive = result


def sample(node):
    expansion(node)
    be_positive(node)
    all = sum(node.positive) / 2
    if all == 0:
        return node.children[0]
    else:
        for i in range(len(node.children)):
            all -= node.positive[i]
            if all <= 0:
                return node.children[i]


def simulation(thenode, start):
    if thenode.children is not None:
        i = 0
        sum_s = 0
        sum_b = 0

        while (nd.get_time_diff(start).seconds < 3) and (i < len(thenode.children)):
            child = thenode.children[i]
            potential_option = deepcopy(child)
            count = 0
            temp_s = 0
            temp_b = 0

            while ((potential_option.about_situation[0].get('活五', 0) > 0) or (potential_option.about_situation[1].get('活五', 0) > 0) or (not potential_option.empty)) and (count < 2):
                count += 1
                potential_option = sample(potential_option)
            if potential_option.about_situation[0].get('活五', 0) > 0:
                temp_b += 1
            elif not potential_option.empty:
                temp_b += 0.5
            else:
                if potential_option.score == 0:
                    temp_b += 0.5
                else:
                    if potential_option.score < 0:
                        temp_b += -1 * min(-potential_option.score, 10000)/20000 + 0.5
                    else:
                        temp_b += 1 * min(potential_option.score, 10000)/20000 + 0.5

            temp_s += 1
            thenode.children[i].simulation_t = temp_s
            sum_s += temp_s
            thenode.children[i].beat_t = temp_b
            sum_b += temp_b
            i += 1
        back_prop(thenode, sum_s, sum_b)


def back_prop(node, sum_s, sum_b):
    while node is not None:
        node.simulation_t += sum_s
        node.beat_t += sum_b
        node = node.parent



