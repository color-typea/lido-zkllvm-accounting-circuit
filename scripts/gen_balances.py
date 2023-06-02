import os
import random
from typing import List

from eth_consensus_layer_ssz import Balances, Gwei
from scripts import config

MAX_GWEI = 2 ** 64 - 1
OUTPUT = os.path.join(config.TEMP_FOLDER, "gen_balances.ssz")
MILLIETH = 10**15

def gen_random_balance(min=0, max=MAX_GWEI) -> int:
    return random.randint(min, max)

def gen_balances(count=50, min=0, max=MAX_GWEI) -> List[int]:
    return [
        gen_random_balance(min, max) for _ in range(count)
    ]

def get_fixed_balances(count=50) -> List[int]:
    return [i * MILLIETH for i in range(count)]

def main():
    balances = get_fixed_balances()
    hash_tree_root = Balances.get_hash_tree_root(balances)
    with open(OUTPUT, "w") as output_file:
        output_file.writelines(str(balance) +"\n" for balance in balances)
    print(f"Hash: {hash_tree_root.hex()}\nSum : {sum(balances)}")

if __name__ == "__main__":
    main()
