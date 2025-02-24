from typing import Tuple, Deque
import random
from collections  import deque
from math import log, sqrt
from time import time

# Time to estimate each policy
TIME = 10

class State:
    def __init__(self, playerhand, househand, actor: int):
        self.initialize_deck(playerhand, househand)
        self.playerhand = playerhand
        self.househand = househand
        self.actor = actor # 0 for player, 1 for house

    def initialize_deck(self, playerhand, househand):
        """
            - Return a deck with all the cards except the ones in the player's and house's hands.
        """
        from hw3 import Deck
        self.deck = Deck()
        self.deck.deck = list(set(Deck().deck) - set(playerhand.cards) - set(househand.cards))
        return

    def is_terminal(self) -> bool:
        """
            - Return True if the state is terminal, False otherwise.
            - A state is terminal if the player's hand value is greater than or equal to 21.
        """
        return self.playerhand.get_value() >= 21 or self.househand.get_value() >= 21
    
    def successor(self, action: str) -> 'State':
        """
            - Return the successor state after taking the action.
            - The action is either 'hit' or 'stand'.
        """
        if self.actor == 0:    
            # Next actor must be 1 (house) 
            if action == 'hit':
                self.deck.shuffle()
                self.playerhand.add_card(self.deck.deal_card())
                return State(self.playerhand, self.househand, 1)
            else:
                # Action: stand
                return State(self.playerhand, self.househand, 1)
        else:
            # Next actor must be 0 (player)
            if action == 'hit':
                self.deck.shuffle()
                self.househand.add_card(self.deck.deal_card())
                return State(self.playerhand, self.househand, 0)
            else:
                # Action: stand
                return State(self.playerhand, self.househand, 0)
    
    def payoff(self) -> int:
        """
            - Return the payoff of a terminal state.
        """
        playerhand_value = self.playerhand.get_value()
        househand_value = self.househand.get_value()
        if playerhand_value > 21:
            return -1
        elif househand_value > 21:
            return 1
        elif playerhand_value > househand_value:
            return 1
        elif playerhand_value < househand_value:
            return -1
        else:
            return 0.5
        
    def simulate(self) -> int:
        """
            - Simulate a random playout of Blackjack from the current state.
            - Return the reward.
        """
        current_state = self
        while not current_state.is_terminal():
            if current_state.actor == 1 and current_state.househand.get_value() < 17:
                # Dealer always has to hit if their hand value is less than 17
                action = 'hit'
            else:
                action = random.choice(['hit', 'stand'])
            current_state = current_state.successor(action)
        return current_state.payoff()
    

class Node:
    def __init__(self, state: State):
        self.state = state
        self.visits = 0
        self.value = 0
        self.edges = [] # 2 edges: hit and stand
        self.parent = None

    def average_payoff(self) -> float:
        """
            - Return the average payoff of the node.
        """
        return self.value / self.visits if self.visits > 0 else 0

    def next_child_to_explore(self, state: State) -> 'Edge':
        """
            - implement UCB1 formula to select the next child to explore.
        """
        def ucb(edge: 'Edge') -> float:
            if edge.visits == 0:
                return float('inf')
            t = sum(e.visits for e in self.edges)
            return ((edge.child.value / edge.visits) if state.actor == 0 else (- edge.child.value / edge.visits)) + sqrt(2 * log(t) / edge.visits)
        return max(self.edges, key=ucb) 
    
    def traverse(self) -> Tuple['Node', Deque['Edge']]:
        """
            - Use UCB formula to guide tree traversal from the root node to a leaf node.
            - Return the leaf node and path(list of edges) traversed.
        """
        edges_to_leaf_node = deque()
        current = self
        while current.edges:
            next_action = current.next_child_to_explore(current.state)
            edges_to_leaf_node.appendleft(next_action)
            current = next_action.child
        return current, edges_to_leaf_node
    
    def expand(self) -> 'Edge':
        """
            - Add new edges to the current non-terminal node.
            - Return an arbitrary edge to a child node.
        """
        # Dealer has to hit if their hand score is less than 17
        actions = ["hit"] if self.state.actor == 1 and self.state.househand.get_value() < 17 else  ['hit', 'stand']
        for action in actions:
            child_state = self.state.successor(action)
            child_node = Node(child_state)
            edge = Edge(action, self, child_node)
            self.edges.append(edge)
        return random.choice(self.edges)
    
    def backpropagate(self, reward: int, edges_to_root: Deque['Edge']) -> None:
        """
            - Update the value and visit counts of the nodes and edges in the best path taken from the current node and the root
        """
        self.visits += 1
        self.value += reward
        while edges_to_root:
            edge = edges_to_root.popleft()
            edge.visits += 1
            edge.parent.value += reward
            edge.parent.visits += 1
        return 
            

class Edge:
    def __init__(self, action: str, parent: Node, child: Node):
        self.action = action
        self.parent = parent
        self.child = child
        self.visits = 0

    
def mcts(playerhand, househand) -> bool:
    """
        - Return True if player should hit, False otherwise.
        - Choice to hit or not is based on Monte Carlo Tree Search
    """
    random.seed(19)
    root_node = Node(State(playerhand, househand, 0))
    iteration_count = 0
    start_time = time()

    while time() - start_time < TIME:
        # Traverse: Choose path from root to best leaf node
        leaf_node, path = root_node.traverse()
        # Expand: Add a new child node to the leaf node if possible i.e. not terminal
        if not leaf_node.state.is_terminal():
            edge_to_child_node = leaf_node.expand()
            leaf_node = edge_to_child_node.child
            path.appendleft(edge_to_child_node)
        # Simulate: Run a simulation from the leaf node
        reward = leaf_node.state.simulate()
        # Backpropagate: Update the value of the nodes in the path from root to leaf node
        leaf_node.backpropagate(reward, path)
        iteration_count += 1
    
    # Choose the best action
    return max(root_node.edges, key=lambda edge: edge.child.average_payoff()).action if root_node.state.actor == 0 else min(root_node.edges, key=lambda edge: edge.child.average_payoff()).action