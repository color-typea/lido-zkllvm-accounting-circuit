import time
import random
import secrets

from typing import List, Optional

import constants
from eth_consensus_layer_ssz import (
    BeaconState, Fork, BeaconBlockHeader, Validator, Checkpoint, Eth1Data,
    SyncCommittee, ExecutionPayloadHeader
)

class Constants:
    class Genesis:
        TIME = 123456
        VALIDATORS_ROOT: bytes = int(100200300400).to_bytes(32, 'little', signed=False)
        BLOCK_ROOT: bytes = str("== Root Block Hash ==").encode("utf-8") + b'\x00' * 11

    class Fork:
        PREVIOUS_VERSION: bytes = int(1).to_bytes(4, 'little', signed=False)
        CURRENT_VERSION: bytes = int(2).to_bytes(4, 'little', signed=False)


class Generators:
    @classmethod
    def hash_root(cls) -> bytes:
        return secrets.token_bytes(32)
    @classmethod
    def bls_signature(cls) -> bytes:
        return secrets.token_bytes(48)

    @classmethod
    def zero_int_vector(cls, length):
        return [0 for _ in range(length)]

    @classmethod
    def empty_hash_vector(cls, length):
        return [b"\x00" * 32 for _ in range(length)]

    @classmethod
    def empty_bls_sig_vector(cls, length):
        return [b"\x00" * 48 for _ in range(length)]

def make_validator(
        withdrawal_credentials: bytes, activation_eligibility_epoch: int, activation_epoch: int,
        exit_epoch: Optional[int] = None, pubkey = None
) -> Validator:
    pubkey = secrets.token_bytes(48) if pubkey is None else pubkey
    assert len(withdrawal_credentials) == 32
    assert activation_eligibility_epoch < activation_epoch
    if exit_epoch is not None:
        assert exit_epoch >= activation_epoch
    return Validator.create(
        pubkey = pubkey,
        withdrawal_credentials =  withdrawal_credentials,
        effective_balance =  32 * 10**9,
        slashed =  False,
        activation_eligibility_epoch =  activation_eligibility_epoch,
        activation_epoch =  activation_epoch,
        exit_epoch =  exit_epoch if exit_epoch is not None else constants.FAR_FUTURE_EPOCH,
        withdrawable_epoch =  activation_epoch + 1,
    )

def make_validator_padding() -> Validator:
    return Validator.create(
        pubkey = b"\x00" * 48,
        withdrawal_credentials =  b"\x00" * 32,
        effective_balance =  0,
        slashed =  False,
        activation_eligibility_epoch =  constants.FAR_FUTURE_EPOCH,
        activation_epoch =  constants.FAR_FUTURE_EPOCH,
        exit_epoch =  constants.FAR_FUTURE_EPOCH,
        withdrawable_epoch =  constants.FAR_FUTURE_EPOCH,
    )

def make_beacon_block_state(
    slot: int,
    epoch: int,
    parent_root: bytes,
    validators: List[Validator],
    balances: List[int],
    finalized_epoch: Optional[int] = None,
    previous_epoch: Optional[int] = None,
) -> BeaconState:
    finalized_epoch = finalized_epoch if finalized_epoch is not None else epoch
    previous_epoch = previous_epoch if previous_epoch is not None else epoch
    assert len(parent_root) == 32
    deposit_count = random.randint(0, 100000)
    current_timestamp = int(time.time())
    return BeaconState.create(
        genesis_time = Constants.Genesis.TIME,
        genesis_validators_root = Constants.Genesis.VALIDATORS_ROOT,
        slot = slot,
        fork = Fork.create(
            previous_version=Constants.Fork.PREVIOUS_VERSION,
            current_version=Constants.Fork.PREVIOUS_VERSION,
            epoch=epoch
        ),
        latest_block_header = BeaconBlockHeader.create(
            slot = slot,
            proposer_index = random.randint(0, 100000),
            parent_root = parent_root,
            state_root = Generators.hash_root(),
            body_root = Generators.hash_root(),
        ),
        block_roots = Generators.empty_hash_vector(constants.SLOTS_PER_HISTORICAL_ROOT),
        state_roots = Generators.empty_hash_vector(constants.SLOTS_PER_HISTORICAL_ROOT),
        historical_roots = [],
        eth1_data = Eth1Data.create(
            deposit_root = Generators.hash_root(),
            deposit_count = deposit_count,
            block_hash = Generators.hash_root(),
        ),
        eth1_data_votes = [],
        eth1_deposit_index = deposit_count,
        validators = validators,
        balances = balances,
        randao_mixes = Generators.empty_hash_vector(constants.EPOCHS_PER_HISTORICAL_VECTOR),
        slashings = Generators.zero_int_vector(constants.EPOCHS_PER_SLASHINGS_VECTOR),
        previous_epoch_participation = [],
        current_epoch_participation = [],
        justification_bits = b"\x00\x00\x00\x00",
        previous_justified_checkpoint = Checkpoint.create(epoch = previous_epoch, root = Generators.hash_root()),
        current_justified_checkpoint = Checkpoint.create(epoch = epoch, root = Generators.hash_root()),
        finalized_checkpoint = Checkpoint.create(epoch = finalized_epoch, root = Generators.hash_root()),
        inactivity_scores = [],
        current_sync_committee = SyncCommittee.create(
            pubkeys=Generators.empty_bls_sig_vector(constants.SYNC_COMMITTEE_SIZE),
            aggregate_pubkey=Generators.bls_signature()
        ),
        next_sync_committee = SyncCommittee.create(
            pubkeys=Generators.empty_bls_sig_vector(constants.SYNC_COMMITTEE_SIZE),
            aggregate_pubkey=Generators.bls_signature()
        ),
        latest_execution_payload_header = ExecutionPayloadHeader.create(
            parent_hash = parent_root,
            fee_recipient = b"\x00" * 20,
            state_root = Generators.hash_root(),
            receipts_root = Generators.hash_root(),
            logs_bloom = b"\x00" * constants.BYTES_PER_LOGS_BLOOM,
            prev_randao = Generators.hash_root(),
            block_number = slot + 10000000,
            gas_limit = 10 ** 12,
            gas_used = 1234567890,
            timestamp = current_timestamp - 60 * 60,
            extra_data = b"",
            base_fee_per_gas = 1000,
            block_hash = Generators.hash_root(),
            transactions_root = Generators.hash_root(),
            withdrawals_root = Generators.hash_root(),
        ),
        next_withdrawal_index = 0,
        next_withdrawal_validator_index = 1,
        historical_summaries = [],
    )
