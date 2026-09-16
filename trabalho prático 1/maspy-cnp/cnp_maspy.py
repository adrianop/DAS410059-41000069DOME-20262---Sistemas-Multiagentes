"""
Contract Net Protocol (CNP) implemented with the MASPY library.

This is the MASPY counterpart of the Jason/JaCaMo implementation found in
../np1.3/my1st-app/src/agt/{cnp_initiator,cnp_participant}.asl, built for the
"Trabalho Pratico - Contract Net Protocol" assignment (UFSC, Sistemas
Multiagentes, Prof. Jomi Hubner). The assignment's "Alternativa" allows
replacing the Jason-scaling study with a second agent language implementing
the same protocol, for the sake of comparison; MASPY (Python, BDI) is the
language suggested in the statement.

Protocol (mirrors https://en.wikipedia.org/wiki/Contract_Net_Protocol):
    1. An Initiator broadcasts a Call For Proposal (cfp) for a task to every
       known Participant.
    2. Each Participant that offers the requested service replies with a
       proposal (price), computed with its own strategy.
    3. After a fixed deadline, the Initiator picks the cheapest proposal,
       awards the task to that Participant and rejects every other one.
    4. The winning Participant "executes" the task and informs completion.

Parameters requested by the assignment:
    n = number of Initiator agents        (1 < n < 200)
    m = number of Participant agents      (1 < m < 50)
    i = parallel contracts per Initiator  (0 < i < 10)

Usage:
    python cnp_maspy.py --n 3 --m 4 --i 1
"""

from __future__ import annotations

import argparse
import random
import threading
import time
from typing import Callable, Dict, List, Tuple

from maspy import Admin, Agent, Any, Belief, Goal, gain, pl, tell

SERVICE = "delivery"
CFP_TIMEOUT = 1.0    # seconds an Initiator waits for proposals before deciding
AWARD_DELAY = 0.2    # seconds a Participant takes to "execute" an awarded task


# --------------------------------------------------------------------------
# Proposal strategies: each Participant offers a single service, but the
# assignment explicitly asks for "differentiated proposal strategies", so
# three price strategies are provided and rotated across Participants.
# --------------------------------------------------------------------------

def fixed_price(base_price: float) -> Callable[[str], float]:
    """Always proposes the same base price."""
    def strategy(_task_id: str) -> float:
        return base_price
    return strategy


def randomized_price(base_price: float, spread: float = 3.0, seed: int = 0) -> Callable[[str], float]:
    """Proposes the base price plus random noise (models uncertain costs)."""
    rnd = random.Random(seed)
    def strategy(_task_id: str) -> float:
        return round(base_price + rnd.uniform(-spread, spread), 2)
    return strategy


def eager_price(base_price: float, discount_step: float = 1.5) -> Callable[[str], float]:
    """Gets cheaper on every subsequent proposal (models an agent hungry for work)."""
    state = {"count": 0}
    lock = threading.Lock()
    def strategy(_task_id: str) -> float:
        with lock:
            state["count"] += 1
            n = state["count"]
        return round(max(base_price - discount_step * (n - 1), 1.0), 2)
    return strategy


STRATEGIES = [fixed_price, randomized_price, eager_price]


# --------------------------------------------------------------------------
# Agents
# --------------------------------------------------------------------------

class Participant(Agent):
    """Offers a single type of service, using its own proposal strategy."""

    def __init__(self, name: str, service: str, price_strategy: Callable[[str], float]):
        super().__init__(name)
        self.service = service
        self.price_strategy = price_strategy

    @pl(gain, Belief("cfp", (Any, Any, Any)))
    def on_cfp(self, src, cfp_data):
        task_id, service, initiator = cfp_data
        if service != self.service:
            return
        price = self.price_strategy(task_id)
        self.send(src, tell, Belief("propose", (task_id, self.my_name, price)))
        self.print(f"proposed {price} for {task_id} (cfp from {initiator})")

    @pl(gain, Belief("award", (Any, Any, Any, Any)))
    def on_award(self, src, award_data):
        task_id, service, price, initiator = award_data
        self.print(f"WON {task_id} for {price}, executing '{service}'...")
        time.sleep(AWARD_DELAY)
        self.send(src, tell, Belief("completed", (task_id, self.my_name)))

    @pl(gain, Belief("reject", Any))
    def on_reject(self, src, task_id):
        self.print(f"lost {task_id}")


class Initiator(Agent):
    """Runs `n_contracts` Contract Net Protocols in parallel over `participants`."""

    def __init__(self, name: str, participants: List[str], service: str,
                 n_contracts: int, timeout: float = CFP_TIMEOUT):
        super().__init__(name, max_intentions=max(5, n_contracts + 1))
        self.participants = participants
        self.service = service
        self.n_contracts = n_contracts
        self.timeout = timeout
        self.results: Dict[str, Tuple[str, float]] = {}
        self.timings: Dict[str, Dict[str, float]] = {}
        self.add(Goal("start"))

    @pl(gain, Goal("start"))
    def on_start(self, src):
        self.print(f"starting {self.n_contracts} parallel contract(s) "
                    f"over {len(self.participants)} participants")
        for k in range(1, self.n_contracts + 1):
            self.add(Goal("contract", k))

    @pl(gain, Goal("contract", Any))
    def on_contract(self, src, number):
        # Proposals are only accumulated as beliefs here; the winner is
        # decided once, below, with a single min() over everything received
        # by the deadline -- not by comparing each new proposal against a
        # running "best" belief as it arrives. The Jason/JaCaMo counterpart
        # of this file (../np1.3/my1st-app/src/agt/cnp_initiator.asl)
        # originally worked that way (two plans: "no best yet" / "cheaper
        # than current best"), and under i>1 concurrent contracts that turned
        # out to be a real read-then-write race: two proposals for the same
        # task arriving close together could both be evaluated against the
        # belief base before either's effect was applied, so both matched
        # "no best yet" and the wrong (non-cheapest) one could end up as the
        # decision. Collecting everything and picking the minimum once, after
        # the bidding window closes, has no such window regardless of arrival
        # order or how many contracts run in parallel.
        task_id = f"{self.my_name}-{number}"
        self.timings[task_id] = {"start": time.perf_counter()}
        for p in self.participants:
            self.send(p, tell, Belief("cfp", (task_id, self.service, self.my_name)))
        time.sleep(self.timeout)

        proposals = [b for b in self.belief_list
                     if b.name == "propose" and b.values[0] == task_id]
        if not proposals:
            self.print(f"no proposals received for {task_id}")
            return

        winner_belief = min(proposals, key=lambda b: b.values[2])
        _, winner, price = winner_belief.values

        for p in self.participants:
            if p == winner:
                self.send(p, tell, Belief("award", (task_id, self.service, price, self.my_name)))
            else:
                self.send(p, tell, Belief("reject", task_id))
        self.print(f"awarded {task_id} to {winner} for {price} "
                    f"({len(proposals)} proposal(s) received)")
        self.results[task_id] = (winner, price)
        self.rm(proposals)

    @pl(gain, Belief("completed", (Any, Any)))
    def on_completed(self, src, completed_data):
        task_id, participant = completed_data
        if task_id in self.timings:
            self.timings[task_id]["end"] = time.perf_counter()
        self.print(f"confirmed {task_id} completed by {participant}")


# --------------------------------------------------------------------------
# Experiment / demo runner
# --------------------------------------------------------------------------

BASE_PRICES = [30, 22, 27, 18, 25, 20, 33, 15, 28, 24]


def build_participants(m: int) -> List[Participant]:
    participants = []
    for idx in range(m):
        base = BASE_PRICES[idx % len(BASE_PRICES)] + 5 * (idx // len(BASE_PRICES))
        strategy = STRATEGIES[idx % len(STRATEGIES)](base)
        participants.append(Participant(f"participant{idx + 1}", SERVICE, strategy))
    return participants


def build_initiators(n: int, participant_names: List[str], i_contracts: int) -> List[Initiator]:
    return [
        Initiator(f"initiator{idx + 1}", participant_names, SERVICE, i_contracts)
        for idx in range(n)
    ]


def run(n: int, m: int, i: int) -> None:
    assert 1 < n < 200, "n (initiators) must satisfy 1 < n < 200"
    assert 1 < m < 50, "m (participants) must satisfy 1 < m < 50"
    assert 0 < i < 10, "i (parallel contracts per initiator) must satisfy 0 < i < 10"

    participants = build_participants(m)
    participant_names = [p.my_name for p in participants]
    initiators = build_initiators(n, participant_names, i)

    total_contracts = n * i
    start = time.time()

    def watchdog():
        deadline = start + CFP_TIMEOUT + AWARD_DELAY + 3 + 0.2 * total_contracts
        while time.time() < deadline:
            done = sum(len(ag.results) for ag in initiators)
            if done >= total_contracts:
                break
            time.sleep(0.05)
        time.sleep(0.3)
        Admin().stop_system()

    threading.Thread(target=watchdog, daemon=True).start()
    Admin().start_system()
    elapsed = time.time() - start

    latencies = []
    starts, ends = [], []
    for ag in initiators:
        for task_id, t in ag.timings.items():
            if "start" in t and "end" in t:
                latencies.append(t["end"] - t["start"])
                starts.append(t["start"])
                ends.append(t["end"])

    print("\n=== CNP Summary =========================================")
    print(f"n={n} initiators, m={m} participants, i={i} contract(s)/initiator")
    completed = sum(len(ag.results) for ag in initiators)
    print(f"contracts completed: {completed}/{total_contracts}")
    print(f"elapsed time: {elapsed:.3f}s")
    if latencies:
        protocol_span = max(ends) - min(starts)
        print(f"protocol_span_s={protocol_span:.3f}")
        print(f"avg_latency_s={sum(latencies)/len(latencies):.3f}")
        print(f"min_latency_s={min(latencies):.3f}")
        print(f"max_latency_s={max(latencies):.3f}")
    for ag in initiators:
        for task_id, (winner, price) in ag.results.items():
            print(f"  {task_id}: {winner} @ {price}")
    print("==========================================================")


def main():
    parser = argparse.ArgumentParser(description="Contract Net Protocol demo with MASPY")
    parser.add_argument("--n", type=int, default=3, help="number of initiators (1 < n < 200)")
    parser.add_argument("--m", type=int, default=4, help="number of participants (1 < m < 50)")
    parser.add_argument("--i", type=int, default=1, help="parallel contracts per initiator (0 < i < 10)")
    args = parser.parse_args()
    run(args.n, args.m, args.i)


if __name__ == "__main__":
    main()
