import os
import random
from typing import List

from eth_consensus_layer_ssz import Balances
from scripts import config
from hashlib import sha256

MAX_GWEI = 2 ** 64 - 1
OUTPUT = os.path.join(config.TEMP_FOLDER, "gen_balances.ssz")
MILLIETH = 10**15
DEBUG = True

BALANCES_TREE_HEIGHT = 38

def gen_random_balance(min=0, max=MAX_GWEI) -> int:
    return random.randint(min, max)

def gen_balances(count=50, min=0, max=MAX_GWEI) -> List[int]:
    return [
        gen_random_balance(min, max) for _ in range(count)
    ]

def get_fixed_balances(count=50) -> List[int]:
    return [i for i in range(1, count+1)]

# ZEROHASHES[0] = 0; ZEROHASHES[i+1] = sha(ZEROHASHES[i], ZEROHASHES[i])
ZEROHASHES = [
    bytes.fromhex("0000000000000000000000000000000000000000000000000000000000000000"),
    bytes.fromhex("f5a5fd42d16a20302798ef6ed309979b43003d2320d9f0e8ea9831a92759fb4b"),
    bytes.fromhex("db56114e00fdd4c1f85c892bf35ac9a89289aaecb1ebd0a96cde606a748b5d71"),
    bytes.fromhex("c78009fdf07fc56a11f122370658a353aaa542ed63e44c4bc15ff4cd105ab33c"),
    bytes.fromhex("536d98837f2dd165a55d5eeae91485954472d56f246df256bf3cae19352a123c"),
    bytes.fromhex("9efde052aa15429fae05bad4d0b1d7c64da64d03d7a1854a588c2cb8430c0d30"),
    bytes.fromhex("d88ddfeed400a8755596b21942c1497e114c302e6118290f91e6772976041fa1"),
    bytes.fromhex("87eb0ddba57e35f6d286673802a4af5975e22506c7cf4c64bb6be5ee11527f2c"),
    bytes.fromhex("26846476fd5fc54a5d43385167c95144f2643f533cc85bb9d16b782f8d7db193"),
    bytes.fromhex("506d86582d252405b840018792cad2bf1259f1ef5aa5f887e13cb2f0094f51e1"),
    bytes.fromhex("ffff0ad7e659772f9534c195c815efc4014ef1e1daed4404c06385d11192e92b"),
    bytes.fromhex("6cf04127db05441cd833107a52be852868890e4317e6a02ab47683aa75964220"),
    bytes.fromhex("b7d05f875f140027ef5118a2247bbb84ce8f2f0f1123623085daf7960c329f5f"),
    bytes.fromhex("df6af5f5bbdb6be9ef8aa618e4bf8073960867171e29676f8b284dea6a08a85e"),
    bytes.fromhex("b58d900f5e182e3c50ef74969ea16c7726c549757cc23523c369587da7293784"),
    bytes.fromhex("d49a7502ffcfb0340b1d7885688500ca308161a7f96b62df9d083b71fcc8f2bb"),
    bytes.fromhex("8fe6b1689256c0d385f42f5bbe2027a22c1996e110ba97c171d3e5948de92beb"),
    bytes.fromhex("8d0d63c39ebade8509e0ae3c9c3876fb5fa112be18f905ecacfecb92057603ab"),
    bytes.fromhex("95eec8b2e541cad4e91de38385f2e046619f54496c2382cb6cacd5b98c26f5a4"),
    bytes.fromhex("f893e908917775b62bff23294dbbe3a1cd8e6cc1c35b4801887b646a6f81f17f"),
    bytes.fromhex("cddba7b592e3133393c16194fac7431abf2f5485ed711db282183c819e08ebaa"),
    bytes.fromhex("8a8d7fe3af8caa085a7639a832001457dfb9128a8061142ad0335629ff23ff9c"),
    bytes.fromhex("feb3c337d7a51a6fbf00b9e34c52e1c9195c969bd4e7a0bfd51d5c5bed9c1167"),
    bytes.fromhex("e71f0aa83cc32edfbefa9f4d3e0174ca85182eec9f3a09f6a6c0df6377a510d7"),
    bytes.fromhex("31206fa80a50bb6abe29085058f16212212a60eec8f049fecb92d8c8e0a84bc0"),
    bytes.fromhex("21352bfecbeddde993839f614c3dac0a3ee37543f9b412b16199dc158e23b544"),
    bytes.fromhex("619e312724bb6d7c3153ed9de791d764a366b389af13c58bf8a8d90481a46765"),
    bytes.fromhex("7cdd2986268250628d0c10e385c58c6191e6fbe05191bcc04f133f2cea72c1c4"),
    bytes.fromhex("848930bd7ba8cac54661072113fb278869e07bb8587f91392933374d017bcbe1"),
    bytes.fromhex("8869ff2c22b28cc10510d9853292803328be4fb0e80495e8bb8d271f5b889636"),
    bytes.fromhex("b5fe28e79f1b850f8658246ce9b6a1e7b49fc06db7143e8fe0b4f2b0c5523a5c"),
    bytes.fromhex("985e929f70af28d0bdd1a90a808f977f597c7c778c489e98d3bd8910d31ac0f7"),
    bytes.fromhex("c6f67e02e6e4e1bdefb994c6098953f34636ba2b6ca20a4721d2b26a886722ff"),
    bytes.fromhex("1c9a7e5ff1cf48b4ad1582d3f4e4a1004f3b20d8c5a2b71387a4254ad933ebc5"),
    bytes.fromhex("2f075ae229646b6f6aed19a5e372cf295081401eb893ff599b3f9acc0c0d3e7d"),
    bytes.fromhex("328921deb59612076801e8cd61592107b5c67c79b846595cc6320c395b46362c"),
    bytes.fromhex("bfb909fdb236ad2411b4e4883810a074b840464689986c3f8a8091827e17c327"),
    bytes.fromhex("55d8fb3687ba3ba49f342c77f5a1f89bec83d811446e1a467139213d640b6a74"),
    bytes.fromhex("f7210d4f8e7e1039790e7bf4efa207555a10a6db1dd4b95da313aaa88b88fe76"),
    bytes.fromhex("ad21b516cbc645ffe34ab5de1c8aef8cd4e7f8d2b51e8e1456adc7563cda206f"),
]

def check_zerohashes():
    current = b'\x00' * 32
    for i in range(len(ZEROHASHES)):
        assert(current == ZEROHASHES[i])
        current = sha256(current + current).digest()
    print("ZEROHASHES correct")

def hash_pair(first: bytes, second: bytes) -> bytes:
    return sha256(first + second).digest()

def uint64_to_bytes(value) -> bytes:
    return value.to_bytes(8, 'little', signed=False)

def pack(value1, value2, value3, value4):
    """
    Packs 4 numbers into 32 byte (256 bit) block, little endian, unsigned
    Note that (-1).to_bytes(..., signed=False) DO NOT result in 2-complement, but raises an exception
    pack(1,2,3,4) == b'\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00'
    """
    assert(value1 > 0 and value2 > 0 and value3 > 0 and value4 > 0)
    result = uint64_to_bytes(value1) + uint64_to_bytes(value2) + uint64_to_bytes(value3) + uint64_to_bytes(value4)
    assert(len(result) == 32)
    return result

def slice_into_chunks(lst, chunk_len, fillvalue):
    """
    Slices lst into non-overlapping lists of `chunk_len`.
    The last chunk is padded to full length with fillvalue

    Examples:
    >>> slice_into_chunks([1,2,3,4,5,6], 2, -1) == [[1,2], [3,4], [5,6]]
    >>> slice_into_chunks([1,2,3,4,5,6], 3, -1) == [[1,2,3], [4,5,6]]
    >>> slice_into_chunks([1,2,3,4,5,6,7,8], 3, -1) == [[1,2,3], [4,5,6], [7,8,-1]]
    """
    remainder = len(lst) % chunk_len
    if remainder != 0:
        lst += [fillvalue] * (chunk_len - remainder)
    sliced_list = [lst[i:i+chunk_len] for i in range(0, len(lst), chunk_len)]
    return sliced_list

def print_bytes_array(array):
    print(list(value.hex() for value in array))


def merkelize(array, tree_height):
    working_copy = list(array)  # make a copy
    depth = 0
    while len(working_copy) > 1:
        into_pairs = slice_into_chunks(working_copy, 2, ZEROHASHES[depth])
        if DEBUG:
            print(f"Depth {depth:02}")
            print_bytes_array(working_copy)
        working_copy = [hash_pair(first, second) for (first, second) in into_pairs]
        depth += 1
    actual_data_hash = working_copy[0]
    tree_root = actual_data_hash
    if DEBUG:
        print(f"Actual data depth={depth:02}, hash={tree_root.hex()}")

    for cur_depth in range(depth, tree_height):
        tree_root = hash_pair(tree_root, ZEROHASHES[cur_depth])
        if DEBUG:
            print(f"Depth {cur_depth+1:02}: {tree_root.hex()}")

    return tree_root

def mix_in_size(root, size):
    return hash_pair(root, size.to_bytes(32, 'little', signed=False))

def main():
    balances = get_fixed_balances(count=20)
    # Computing merkle tree root via SSZ
    hash_tree_root = Balances.get_hash_tree_root(balances)
    with open(OUTPUT, "w") as output_file:
        output_file.writelines(str(balance) +"\n" for balance in balances)

    # Computing merkle tree root via standalone implementation
    packed_chunks = [pack(v1, v2, v3, v4) for (v1, v2, v3, v4) in slice_into_chunks(balances, 4, 0)]
    print("Merkle leafs:")
    print_bytes_array(packed_chunks)
    standalone_merkle = mix_in_size(
        merkelize(packed_chunks, BALANCES_TREE_HEIGHT),
        len(balances)
    )
    print(f"Standalone merkle: {standalone_merkle.hex()}")
    print(f"SSZ              : {hash_tree_root.hex()}")
    print(f"Sum : {sum(balances)}")

if __name__ == "__main__":
    main()
