import pisqpipe as pp
import re


""" This is the module where we use alpha-beta pruning to decide which available 
position on the board we should best consider. We will employ the knowledge learned 
through lab and homework to design minValue and maxValue method as well as Node and 
Tree kinds of representations to realize it."""


def overallAssess(board, turn):

    """ We specify all possible circumstances in the board such as 冲四, 眠三，死二
    and assign them to each score individually according to a github repository
    https://github.com/SimpCosm/Gomoku.  """

    situations = {"End5": ["11111"],
                  "End4": ["011110"],
                  "pWin4": ["011112", "211110", r"^11110", r"01111$", "0101110", "0111010", "0110110"],
                  "pWin31": ["01110", "010110", "011010"],
                  "pWin32": ["001112", r"00111$", "211100", r"^11100", "010112", r"01011$", "211010", r"^11010",
                             "011012",
                             r"01101$", "210110", r"^10110", "10011", "11001", "10101", "2011102", r"^011102",
                             r"201110$"],
                  "pWin21": ["00110", "01100", "01010", "010010"],
                  "pWin22": ["000112", r"00011$", "211000", r"^11000", "001012", r"00101$", "210100", r"^10100",
                             "010012",
                             r"01001$", "210010", r"^10010", "10001", "2010102", r"201010$", r"^010102", "2011002",
                             r"^011002", r"201100^", "2001102", r"200110$", r"^001102"],
                  "noWin4": ["211112", r"21111$", r"^11112"],
                  "noWin3": ["21112", r"2111$", r"^1112"],
                  "noWin2": ["2112", r"^112", r"211$"],
                  }

    scores = {"End5": 200000,
              "End4": 10000,
              "pWin4": 1000,
              "pWin31": 200,
              "pWin32": 50,
              "pWin21": 5,
              "pWin22": 3,
              "noWin4": -5,
              "noWin3": -5,
              "noWin2": -5
              }

    counter = {"End5": 0,  # A counter to record how many time each situation is appeared on the board
               "End4": 0,
               "pWin4": 0,
               "pWin31": 0,
               "pWin32": 0,
               "pWin21": 0,
               "pWin22": 0,
               "noWin4": 0,
               "noWin3": 0,
               "noWin2": 0,
               }

    if turn == 2:
        for i in range(pp.height):
            for j in range(pp.width):
                board[i][j] = (3 - board[i][j]) % 3

    for idx in range(pp.height):  # gather the total number of each situations in each row and record it in counter
        row = board[idx]
        theList = "".join(map(str, row))
        for key in situations:
            for i in range(len(situations[key])):
                counter[key] += len(re.findall(situations[key][i], theList))

    for idx in range(pp.width):  # gather the total number of each situations in each column and record it in counter
        c = []
        for j in board:
            c.append(j[idx])
        theList = "".join(map(str, c))
        for key in situations:
            for i in range(len(situations[key])):
                counter[key] += len(re.findall(situations[key][i], theList))

    for idx in range(-pp.width + 1, pp.height):  # gather the total number of each situations in each diagnal direction                                                # and record it in counter
        dia = []                                 # (from lower left to upper right)
        if idx < 0:
            rI, cI = 0, -idx
        else:
            rI, cI = idx, 0
        for i in range(rI, pp.height):
            for j in range(cI, pp.width):
                if i - j == idx:
                    dia.append(board[i][j])
        theList = "".join(map(str, dia))
        for key in situations:
            for i in range(len(situations[key])):
                counter[key] += len(re.findall(situations[key][i], theList))

    for idx in range(0, pp.width + pp.height - 1):  # gather the total number of each situations in each diagnal direction
        dia = []                                    # (from upper left to lower right)
        if idx < pp.height:
            rI, cI = idx, 0
        else:
            rI, cI = pp.height - 1, idx - pp.height + 1
        for i in range(rI, -1, -1):
            for j in range(cI, pp.width):
                if i + j == idx:
                    dia.append(board[i][j])
        theList = "".join(map(str, dia))
        for key in situations:
            for i in range(len(situations[key])):
                counter[key] += len(re.findall(situations[key][i], theList))

    return counter, scores  # return the counter and a list containing all responding scores


def sumUp(board):

    """ We call overallAssess in this method and further
    return the score we calculate for leaves in the tree."""

    score = 0
    c1, s1 = overallAssess(board, 1)
    c2, s2 = overallAssess(board, 2)

    for situation, num in c1.items():  # self turn
        score = score + s1[situation] * num
    for situation, num in c2.items():  # opponent turn
        if situation in ['End5', 'End4', 'pWin4']:
            score = score - 10 * s2[situation] * num
        else:
            score = score - s2[situation] * num

    return score

def PlantATree(board, action, turn, expansion):

    """ We construct a tree within this method so that we can do minimax with alpha-beta
    pruning later. When considering which node to append to the current one
    as a child, we utilize the nearPostion to find all suitable positions and
    evaluate them one by one using methods above so that only expansion（Int）
    number of positions will be included to secure the speed """

    suitableP = nearPosition(board)  # Find best available locations
    if suitableP is None:  # No where to go next
        return None
    node = Node(action=action, turn=turn)
    Children = []
    theList = []

    for position in suitableP:
        nextBoard = [[board[x][y] for y in range(pp.height)] for x in range(pp.width)]
        nextBoard[position[0]][position[1]] = turn

        if len(suitableP) < expansion:
            Children.append(
                Node(action=position, turn=3 - turn, value=sumUp(nextBoard), isLeaf=True))
        else:
            theList.append(sumUp(nextBoard))

    if len(suitableP) >= expansion:
        tempList = []
        for i in theList:
            tempList.append(i)
        tempList.sort(reverse=True)
        for v in tempList[0:expansion]:             # Only need the expansion number of positions from
            position = suitableP[theList.index(v)]  # a sorted list to secure speed and optimality
            Children.append(Node(action=position, turn=3 - turn, value=v, isLeaf=True))

    node.Children = Children
    return node

def nearPosition(board):

    """ We try to find all possible(and also awesome) positions
    still available on the board that we may choose to put our
    stone on this round. In the meantime, we only search for
    positions that surrounds the existing stones to ensure the
    relevance and further speed our program up."""

    candidates = []
    radius = [-1, 0, 1]          # The surrounding area, imagine the possible position is like a round's center
    for x in range(pp.width):    # with 1 as its radius, and we need that there is an existing stone within this round
        for y in range(pp.height):
            if board[x][y] == 0:
                for i in radius:
                    for j in radius:
                        x2 = x + i
                        y2 = y + j
                        if x2 < 0 or x2 >= pp.width or y2 < 0 or y2 >= pp.height:  # To ensure it's in the board bound
                            continue
                        if board[x2][y2] != 0:
                            candidates.append((x, y))
                            break
            else:
                continue

    if not candidates:
        return None
    return candidates


class Node:
    """Node of the tree.

    Attributes:
        action: the action about to take, e.g. (11, 12)
        turn: int, 1 or 2, 1 for brain turns and 2 for opponent turns
        value: value of the node
        Children: list of Node representing children of the current node
        isLeaf: bool, whether the node is a leaf or not

        We use this class to construct a tree in PlantATree method.
    """

    def __init__(self, action=None, turn=1, value=None, Children=None, isLeaf=False):
        self.action = action
        if Children is None:
            Children = []
        if turn == 1:
            self.rule = 'MAX'
        elif turn == 2:
            self.rule = 'MIN'
        self.value = value
        self.Children = Children
        self.isLeaf = isLeaf


def getValue(node, alpha, beta):
    """Get value for the given node.

       Args:
           node: class Node object
           alpha: float
           beta: float

       Returns:
           value of the node, the action about to take
       """
    if node.isLeaf:
        return node.value, None

    if node.rule == 'MAX':
        return maxValue(node, alpha, beta)
    else:
        return minValue(node, alpha, beta)


def maxValue(node, alpha, beta):
    """Get value for the given MAX node.

       Args:
           node: class Node object
           alpha: float
           beta: float

       Returns:
           value of the node, the action about to take
       """
    action = None
    v = float('-inf')
    for child in node.Children:
        if getValue(child, alpha, beta)[0] > v:
            v = getValue(child, alpha, beta)[0]
            action = child.action

        alpha = max(v, alpha)

        if v >= beta:
            return v, None
    return v, action


def minValue(node, alpha, beta):
    """Get value for the given MIN node.

           Args:
               node: class Node object
               alpha: float
               beta: float

           Returns:
               value of the node, the action about to take
           """
    action = None
    v = float('inf')
    for child in node.Children:
        if getValue(child, alpha, beta)[0] < v:
            v = getValue(child, alpha, beta)[0]
            action = child.action

        beta = min(v, beta)

        if v <= alpha:
            return v, None
    return v, action

