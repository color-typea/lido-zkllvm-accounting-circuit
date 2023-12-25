from typing import Dict
import ssz
import constants

from ssz.hashable_container import HashableContainer
from ssz.hashable_list import HashableList
from ssz.hashable_vector import HashableVector
from ssz.sedes import (
    Bitlist,
    Bitvector,
    ByteVector,
    List,
    Vector,
    boolean,
    byte,
    bytes4,
    bytes32,
    bytes48,
    uint8,
    uint64,
    uint256
)
from ssz.hash import hash_eth2

Hash32 = bytes32
Root = bytes32
Gwei = uint64
Epoch = uint64
Slot = uint64
CommitteeIndex = uint64
ValidatorIndex = uint64
BLSPubkey = bytes48
ExecutionAddress = ByteVector(20)
WithdrawalIndex = uint64
ParticipationFlags = uint8
Version = bytes4

USE_SIGNED_CONTAINER_BY_DEFAULT = False

class EnhancedHashableContainer(HashableContainer):
    def as_dict(self):
        return {field_name: getattr(self, field_name) for field_name in self._meta.field_names}


    @classmethod
    def _clone_field(cls, field_name, sedes, object):
        field_value = getattr(object, field_name)
        if isinstance(field_value, EnhancedHashableContainer):
            return field_value.clone(field_value)
        elif isinstance(field_value, (HashableVector, HashableList)):
            return field_value.evolver()
        return field_value

    @classmethod
    def _clone_fields(cls, object):
        return {
            field_name: cls._clone_field(field_name, sedes, object) for field_name, sedes in cls._meta.fields
        }
    @classmethod
    def clone(cls, object):
        cloned_fields = cls._clone_fields(object)
        return cls.create(**cloned_fields)

class Fork(EnhancedHashableContainer):
    fields = [
        ("previous_version", bytes4),
        ("current_version", bytes4),
        ("epoch", Epoch)  # Epoch of latest fork
    ]


class Checkpoint(EnhancedHashableContainer):
    fields = [
        ("epoch", Epoch),
        ("root", Root)
    ]


class BeaconBlockHeader(EnhancedHashableContainer):
    fields = [
        ("slot", Slot),
        ("proposer_index", ValidatorIndex),
        ("parent_root", Root),
        ("state_root", Root),
        ("body_root", Root),
    ]


class Eth1Data(EnhancedHashableContainer):
    fields = [
        ("deposit_root", Root),
        ("deposit_count", uint64),
        ("block_hash", Hash32),
    ]


class Validator(EnhancedHashableContainer):
    fields = [
        ("pubkey", BLSPubkey),
        ("withdrawal_credentials", bytes32),  # Commitment to pubkey for withdrawals
        ("effective_balance", Gwei),  # Balance at stake
        ("slashed", boolean),
        # Status epochs
        ("activation_eligibility_epoch", Epoch),  # When criteria for activation were met
        ("activation_epoch", Epoch),
        ("exit_epoch", Epoch),
        ("withdrawable_epoch", Epoch),  # When validator can withdraw funds
    ]


class AttestationData(EnhancedHashableContainer):
    fields = [
        ("slot", Slot),
        ("index", CommitteeIndex),
        ("beacon_block_root", Root),
        ("source", Checkpoint),
        ("target", Checkpoint),
    ]


class PendingAttestation(EnhancedHashableContainer):
    fields = [
        ("aggregation_bits", Bitlist(constants.MAX_VALIDATORS_PER_COMMITTEE)),
        ("data", AttestationData),
        ("inclusion_delay", Slot),
        ("proposer_index", ValidatorIndex),
    ]


class SyncCommittee(EnhancedHashableContainer):
    fields = [
        ("pubkeys", Vector(BLSPubkey, constants.SYNC_COMMITTEE_SIZE)),
        ("aggregate_pubkey", BLSPubkey),
    ]


class ExecutionPayloadHeader(EnhancedHashableContainer):
    # Execution block header fields
    fields = [
        ("parent_hash", Hash32),
        ("fee_recipient", ExecutionAddress),
        ("state_root", bytes32),
        ("receipts_root", bytes32),
        ("logs_bloom", ByteVector(constants.BYTES_PER_LOGS_BLOOM)),
        ("prev_randao", bytes32),
        ("block_number", uint64),
        ("gas_limit", uint64),
        ("gas_used", uint64),
        ("timestamp", uint64),
        # ("extra_data", ByteList(constants.MAX_EXTRA_DATA_BYTES)),
        # workaround - looks like ByteList is partially broken, but extra data is exactly bytes32
        ("extra_data", List(byte, constants.MAX_EXTRA_DATA_BYTES)),
        ("base_fee_per_gas", uint256),
        ("block_hash", Hash32),
        ("transactions_root", Root),
        ("withdrawals_root", Root),
        # ("excess_data_gas: uint256", uint256),
    ]


class HistoricalSummary(EnhancedHashableContainer):
    """
    `HistoricalSummary` matches the components of the phase0 `HistoricalBatch`
    making the two hash_tree_root-compatible.
    """
    fields = [
        ("block_summary_root", Root),
        ("state_summary_root", Root),
    ]


Balances = List(Gwei, constants.VALIDATOR_REGISTRY_LIMIT)
Validators = List(Validator, constants.VALIDATOR_REGISTRY_LIMIT)


class BeaconState(EnhancedHashableContainer):
    fields = [
        # Versioning
        ("genesis_time", uint64),
        ("genesis_validators_root", Root),
        ("slot", Slot),
        ("fork", Fork),
        # History
        ("latest_block_header", BeaconBlockHeader),
        ("block_roots", Vector(Root, constants.SLOTS_PER_HISTORICAL_ROOT)),
        ("state_roots", Vector(Root, constants.SLOTS_PER_HISTORICAL_ROOT)),
        ("historical_roots", List(Root, constants.HISTORICAL_ROOTS_LIMIT)),
        # Frozen in Capella, replaced by historical_summaries
        # Eth1
        ("eth1_data", Eth1Data),
        ("eth1_data_votes",
         List(Eth1Data, constants.EPOCHS_PER_ETH1_VOTING_PERIOD * constants.SLOTS_PER_EPOCH)),
        ("eth1_deposit_index", uint64),
        # Registry
        ("validators", Validators),
        ("balances", Balances),
        # Randomness
        ("randao_mixes", Vector(bytes32, constants.EPOCHS_PER_HISTORICAL_VECTOR)),
        # Slashings
        ("slashings", Vector(Gwei, constants.EPOCHS_PER_SLASHINGS_VECTOR)),
        # Per-epoch sums of slashed effective balances
        # Participation
        ("previous_epoch_participation", List(ParticipationFlags, constants.VALIDATOR_REGISTRY_LIMIT)),
        ("current_epoch_participation", List(ParticipationFlags, constants.VALIDATOR_REGISTRY_LIMIT)),
        # Finality
        ("justification_bits", Bitvector(constants.JUSTIFICATION_BITS_LENGTH)),
        # Bit set for every recent justified epoch
        ("previous_justified_checkpoint", Checkpoint),
        ("current_justified_checkpoint", Checkpoint),
        ("finalized_checkpoint", Checkpoint),
        # Inactivity
        ("inactivity_scores", List(uint64, constants.VALIDATOR_REGISTRY_LIMIT)),
        # Sync
        ("current_sync_committee", SyncCommittee),
        ("next_sync_committee", SyncCommittee),
        # Execution
        ("latest_execution_payload_header", ExecutionPayloadHeader),  # (Modified in Capella)
        # Withdrawals
        ("next_withdrawal_index", WithdrawalIndex),  # (New in Capella)
        ("next_withdrawal_validator_index", ValidatorIndex),  # (New in Capella)
        # Deep history valid from Capella onwards
        ("historical_summaries", List(HistoricalSummary, constants.HISTORICAL_ROOTS_LIMIT)),
        # (New in Capella)
    ]

    @classmethod
    def from_ssz(cls, ssz_bytes: bytes) -> 'BeaconState':
        return ssz.decode(ssz_bytes, cls)

    @property
    def raw_hash_tree_for_inclusion(self):
        # Last layer only has one value that is the hash tree root
        return self.hash_tree.raw_hash_tree[:-1]

    def construct_inclusion_proof(self, field_name, field_hash):
        field_index = self._meta.field_names.index(field_name)

        raw_hash_tree = self.raw_hash_tree_for_inclusion
        result = []

        assert(field_hash == raw_hash_tree[0][field_index])
        for layer in raw_hash_tree:
            sibling_idx = field_index - 1 if field_index % 2 == 1 else field_index + 1
            result.append(layer[sibling_idx])
            field_index //= 2
        return result

    def verify_inclusion_proof(self, field_name, field_hash, inclusion_proof):
        field_index = self._meta.field_names.index(field_name)

        raw_hash_tree = self.raw_hash_tree_for_inclusion
        if len(inclusion_proof) != len(raw_hash_tree):
            return False

        current_hash = field_hash
        for idx in range(len(inclusion_proof)):
            inclusion_step, layer = inclusion_proof[idx], raw_hash_tree[idx]
            assert current_hash == layer[field_index], \
                (f"Verification failed at layer {idx}, field_index {field_index}.\n"
                 f"Expected{layer[field_index]}, got {current_hash}")
            if field_index % 2 == 1:
                current_hash = hash_eth2(layer[field_index - 1] + current_hash)
            else:
                current_hash = hash_eth2(current_hash + layer[field_index + 1])

            field_index //= 2

        return current_hash == self.hash_tree_root



class BeaconStateModifier:
    def __init__(self, beacon_state: BeaconState):
        self._beacon_state = BeaconState.clone(beacon_state)

    def set_slot(self, slot):
        self._beacon_state.slot = slot
        return self

    def update_balance(self, idx: int, new_value: int) -> 'BeaconStateModifier':
        assert idx < len(self._beacon_state.balances)
        self._beacon_state.balances = self._beacon_state.balances.set(idx, new_value)
        return self

    def add_validator(self, validator: Validator, balance: int) -> 'BeaconStateModifier':
        self._beacon_state.validators = self._beacon_state.validators.append(validator)
        self._beacon_state.balances = self._beacon_state.balances.append(balance)
        return self

    def modify_validator(self, validator_idx: int, validator: Validator) -> 'BeaconStateModifier':
        assert validator_idx < len(self._beacon_state.validators)
        self._beacon_state.validators = self._beacon_state.validators.set(validator_idx, validator)
        return self

    def set_validator_exited(self, validator_idx: int, epoch: int) -> 'BeaconStateModifier':
        return self.modify_validator_fields(validator_idx, {"exit_epoch": epoch})

    def modify_validator_fields(self, validator_idx: int, fields: Dict[str, any]) -> 'BeaconStateModifier':
        assert validator_idx < len(self._beacon_state.validators)
        fields_to_set = set(fields.keys())
        existing_fields = set(Validator._meta.field_names)
        unexpected_fields = fields_to_set - existing_fields

        assert not unexpected_fields, f"Cannot update validator - unexpected fields: {unexpected_fields}, "

        validator = self._beacon_state.validators[validator_idx]
        mset_args = [
            item
            for key, value in fields.items()
            for item in (Validator._meta.field_names_to_element_indices[key], value)
        ]
        updated = validator.mset(*mset_args)
        self._beacon_state.validators = self._beacon_state.validators.set(validator_idx, updated)
        return self

    def get(self) -> BeaconState:
        # Second clone is needed to "materialize" changes into the unrlying immutable data
        return BeaconState.clone(self._beacon_state)
