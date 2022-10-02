import argparse
import string
import random
import itertools as it
import graphlib as gl

State = tuple[int, ...]
StateGraph = dict[State, list[State]]


def fibonacci_cache():
    cache = [1, 2]

    def fibonacci(n: int) -> int:
        while n >= len(cache):
            cache.append(cache[-1] + cache[-2])
        return cache[n]

    return fibonacci


fibonacci = fibonacci_cache()


def fibonacci_index_cache():
    cache = {1: 0}
    best = 1

    def index(n: int) -> int:
        nonlocal best
        while best < n:
            i = cache[best] + 1
            cache[best := fibonacci(i)] = i
        return cache.get(n, -1)

    return index


fibonacci_index = fibonacci_index_cache()


def evaluate(state: State) -> int:
    return sum(count * fibonacci(i) for i, count in enumerate(state))


def show(state: State) -> str:
    return " ".join(
        it.chain(
            *(it.repeat(str(fibonacci(i)), count) for i, count in enumerate(state))
        )
    )


def parse(move: str) -> State:
    state: list[int] = []
    for n in map(int, move.strip().split()):
        i = fibonacci_index(n)
        if i == -1:
            return ()
        while i >= len(state):
            state.append(0)
        state[i] += 1
    return (*state,)


def final(state: State) -> bool:
    last = 0
    for count in state:
        if count > 1 or count and last:
            return False
        last = count
    return True


def evolve(state: State):
    # 1+1=2 rule
    if state[0] >= 2:
        new = [*state]
        new[0] -= 2
        if len(new) == 1:
            new.append(1)
        else:
            new[1] += 1
        yield (*new,)

    # 2+2=1+3 rule
    if len(state) >= 2 and state[1] >= 2:
        new = [*state]
        new[1] -= 2
        new[0] += 1
        if len(new) == 2:
            new.append(1)
        else:
            new[2] += 1
        yield (*new,)

    # merge duplicates rule
    for i in range(2, len(state)):
        if state[i] < 2:
            continue

        new = [*state]
        new[i] -= 2
        new[i - 2] += 1
        if i + 1 == len(new):
            new.append(1)
        else:
            new[i + 1] += 1
        yield (*new,)

    # merge consecutives rule
    for i in range(len(state) - 1):
        if not (state[i] and state[i + 1]):
            continue

        new = [*state]
        new[i] -= 1
        new[i + 1] -= 1
        if i + 2 == len(new):
            new.append(1)
        else:
            new[i + 2] += 1
        yield (*new,)


def generate(n: int):
    graph: StateGraph = {(n,): []}
    options: list[State] = [(n,)]
    while options:
        state = options.pop()
        for child in evolve(state):
            graph[state].append(child)

            if final(child) or child in graph:
                continue
            graph[child] = []
            options.append(child)
    return graph


def strategize(graph: StateGraph) -> StateGraph:
    order = iter(gl.TopologicalSorter(graph).static_order())
    strategy: StateGraph = {next(order): []}
    for state in order:
        moves = [child for child in graph[state] if not strategy[child]]
        strategy[state] = moves
    return strategy


def interact(n: int):
    graph = generate(n)
    strategy = strategize(graph)
    state: State = (n,)
    if strategy[state]:
        print("heads up, you're gonna lose!")
        print()

    while True:

        if final(state):
            print("ha! i win!")
            return

        print(f"current state: {show(state)}")

        moves = {key: child for key, child in zip(string.ascii_lowercase, graph[state])}
        if len(moves) == 1:
            move = next(iter(moves.values()))
            print(f"your only move is: {show(move)}")
        else:
            print("your available moves:")
            for key, child in moves.items():
                print(f"  [{key}]: {show(child)}")

            while (
                key := input(f'your turn [{"/".join(moves.keys())}]: ').strip()
            ) not in moves:
                print("  invalid move, try again!")
            move = moves[key]
            print(f"you chose: {move}")

        responses = strategy[move]

        if not responses:
            print("i surrender!")
            return

        state = random.choice(responses)
        print(f"i respond: {show(state)}")

        print()


def main():
    parser = argparse.ArgumentParser("fibonacci-game")
    parser.add_argument("n", type=int)
    args = parser.parse_args()
    print(f"starting a game with n={args.n}")
    print()
    interact(args.n)


if __name__ == "__main__":
    main()
