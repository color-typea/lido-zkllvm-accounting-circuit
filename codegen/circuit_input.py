from abc import ABCMeta, abstractmethod, ABC
from typing import Any, Iterable, NewType, List, Optional, Callable, TypeVar

from eth_typing import HexStr, Hash32
from ssz.hash import hash_eth2

from eth_ssz_utils import make_validator, make_beacon_block_state, Constants, make_validator_padding
from eth_consensus_layer_ssz import Validators, Balances, Validator
from hexbytes import HexBytes

import ssz

import dataclasses

EpochNumber = NewType('EpochNumber', int)
FrameNumber = NewType('FrameNumber', int)
StateRoot = NewType('StateRoot', HexStr)
BlockRoot = NewType('BlockRoot', HexStr)
SlotNumber = NewType('SlotNumber', int)

BlockHash = NewType('BlockHash', HexStr)
BlockNumber = NewType('BlockNumber', int)

Gwei = NewType('Gwei', int)
HashType = (str, str)
T = TypeVar("T")
TOut = TypeVar("TOut")

@dataclasses.dataclass
class BlockHeaderMessage:
    slot: str
    proposer_index: str
    parent_root: BlockRoot
    state_root: StateRoot
    body_root: str


class DataclassConvenience:
    def as_tuple(self):
        return tuple(self.as_dict().values())

    def as_dict(self):
        return dataclasses.asdict(self)


@dataclasses.dataclass
class PublicInput:
    lido_withdrawal_credentials: Hash32
    beacon_state_hash: Hash32
    beacon_block_hash: Hash32
    slot: SlotNumber
    epoch: EpochNumber


@dataclasses.dataclass
class PrivateInput:
    validators: Validators
    balances: Balances
    balances_hash: Hash32
    validators_hash: Hash32
    balances_hash_inclusion_proof: List[HexBytes]
    validators_hash_inclusion_proof: List[HexBytes]
    beacon_block_fields: List[HexBytes]


@dataclasses.dataclass
class OracleReportData(DataclassConvenience):
    slot: SlotNumber
    epoch: EpochNumber
    lidoWithdrawalCredentials: HexBytes
    allLidoValidators: int
    exitedValidators: int
    totalValueLocked: int

    def as_tuple(self):
        return (
            self.slot,
            self.epoch,
            self.lidoWithdrawalCredentials,
            self.allLidoValidators,
            self.exitedValidators,
            self.totalValueLocked,
        )


@dataclasses.dataclass
class OracleProof(DataclassConvenience):
    balances_hash: HexBytes
    validators_hash: HexBytes
    beacon_state_hash: HexBytes
    beacon_block_hash: HexBytes

    def as_tuple(self):
        return (
            self.balances_hash,
            self.validators_hash,
            self.beacon_state_hash,
            self.beacon_block_hash,
        )

    def as_dict_for_logging(self):
        as_dict = dataclasses.asdict(self)
        as_dict['zk_proof'] = as_dict['zk_proof'].hex()
        as_dict['balances_hash'] = as_dict['balances_hash'].hex()
        as_dict['validators_hash'] = as_dict['validators_hash'].hex()
        as_dict['beacon_state_hash'] = as_dict['beacon_state_hash'].hex()
        as_dict['beacon_block_hash'] = as_dict['beacon_block_hash'].hex()

        del as_dict['zk_proof']
        # as_dict['zk_proof'] = as_dict['zk_proof'][:20] + b'\x01020304' + as_dict['zk_proof'][:-20]

        return as_dict


@dataclasses.dataclass
class OracleReport(DataclassConvenience):
    data: OracleReportData
    proof: OracleProof

    def as_tuple(self):
        return (self.data.as_tuple(), self.proof.as_tuple())


class WithdrawalCreds:
    Lido = HexBytes("010000000000000000000000b9d7934878b5fb9610b3fe8a5e441e8fad7e293f")
    Other = HexBytes(b"\01"*32)


class InputBase(ABC):
    @classmethod
    def as_int(cls, val):
        return {"int": val}

    @classmethod
    def as_array(cls, val: Iterable[T], mapper: Callable[[T], TOut]):
        return cls._iterable("array", val, mapper)

    @classmethod
    def as_vector(cls, val, mapper: Callable[[T], TOut]):
        return cls._iterable("verctor", val, mapper)

    @classmethod
    def _iterable(cls, type_label, value, mapper: Callable[[T], TOut]):
        mapped_values = [mapper(item) for item in value]
        return {type_label: mapped_values}

    @classmethod
    def as_field(cls, value: bytes) -> HashType:
        assert len(value) <= 16, f"Serializing as field only support values shorter than 16 bytes, {len(value)} given"
        return {"field": str(int.from_bytes(value, 'little', signed=False))}

    @classmethod
    def as_hash(cls, value: bytes) -> HashType:
        assert len(value) <= 32, f"Serializing as hash only support values shorter than 32 bytes, {len(value)} given"
        return {"vector": [cls.as_field(value[:16]), cls.as_field(value[16:])]}

    @classmethod
    def as_struct(clscls, value: T, mapper: Callable[[T], List[Any]]):
        return {"struct": [mapper(value)]}

    @abstractmethod
    def serialize_public_for_proof_generator(self):
        pass

    @abstractmethod
    def serialize_private_for_proof_generator(self):
        pass

@dataclasses.dataclass
class CircuitInput(InputBase):
    actual_validator_count: int
    public_input: PublicInput
    private_input: PrivateInput
    report_data: OracleReportData

    @property
    def validators(self):
        return self.private_input.validators

    @property
    def balances(self):
        return self.private_input.balances

    def validator_field_for_merkleization(self, extractor: Callable[[Validator], T]) -> List[T]:
        return [extractor(validator) for validator in self.validators]

    def merkelize_pubkey(self, value):
        return ssz.get_hash_tree_root(value)

    def serialize_public_for_proof_generator(self):
        return [
            # "Configuration parameters"
            self.as_hash(self.public_input.lido_withdrawal_credentials),
            self.as_int(self.public_input.slot),
            self.as_int(self.public_input.epoch),

            # Report values
            self.as_int(self.report_data.totalValueLocked),
            self.as_int(self.report_data.allLidoValidators),
            self.as_int(self.report_data.exitedValidators),

            # Block hashes
            self.as_hash(HexBytes(self.public_input.beacon_state_hash)),
            self.as_hash(HexBytes(self.public_input.beacon_block_hash)),
        ]

    def serialize_private_for_proof_generator(self):
        return [
            self.as_int(self.actual_validator_count),
            self.as_array(self.balances, self.as_int),
            # Validator parts
            self.as_array(
                self.validator_field_for_merkleization(lambda validator: hash_eth2(validator.pubkey + b'\x00' * 16)),
                self.as_hash
            ),
            self.as_array(
                self.validator_field_for_merkleization(lambda validator: validator.withdrawal_credentials), self.as_hash
            ),
            self.as_array(
                self.validator_field_for_merkleization(lambda validator: validator.effective_balance), self.as_int
            ),
            self.as_array(
                self.validator_field_for_merkleization(lambda validator: 1 if validator.slashed else 0), self.as_int
            ),
            self.as_array(
                self.validator_field_for_merkleization(lambda validator: validator.activation_eligibility_epoch),
                self.as_int
            ),
            self.as_array(
                self.validator_field_for_merkleization(lambda validator: validator.activation_epoch), self.as_int
            ),
            self.as_array(self.validator_field_for_merkleization(lambda validator: validator.exit_epoch), self.as_int),
            self.as_array(
                self.validator_field_for_merkleization(lambda validator: validator.withdrawable_epoch), self.as_int
            ),

            # Expected hashes
            self.as_hash(self.private_input.balances_hash),
            self.as_hash(self.private_input.validators_hash),

            # Inclusion proofs
            self.as_array(self.private_input.balances_hash_inclusion_proof, self.as_hash),
            self.as_array(self.private_input.validators_hash_inclusion_proof, self.as_hash),

            # Beacon block fields
            self.as_array(self.private_input.beacon_block_fields, self.as_hash),
        ]

def generate_input(problem_size: int, total_validator_count: int, lido_validator_count: int) -> CircuitInput:
    assert lido_validator_count <= problem_size
    passing = problem_size - total_validator_count

    balances = [(10+i) * (10 ** 9) for i in range(total_validator_count)] + [0] * passing
    validators = [
        make_validator(WithdrawalCreds.Lido, i, i+1, None, pubkey=b"\x01"*48)
        for i in range(lido_validator_count)
    ] + [
        make_validator(WithdrawalCreds.Other, i, i+1, None, pubkey=b"\x01"*48)
        for i in range(lido_validator_count, total_validator_count)
    ] + [
        make_validator_padding() for _ in range(total_validator_count, problem_size)
    ]

    lido_sum = sum(balances[:lido_validator_count])

    slot, epoch = SlotNumber(6652831), EpochNumber(207900)
    beacon_state = make_beacon_block_state(
        slot, epoch, Constants.Genesis.BLOCK_ROOT, validators, balances
    )

    mtr = ssz.get_hash_tree_root(beacon_state).hex()

    field_hash = Validators.get_hash_tree_root(beacon_state.validators)
    inclusion = beacon_state.construct_inclusion_proof('validators', field_hash)

    balances_hash = HexBytes(ssz.get_hash_tree_root(beacon_state.balances))
    validators_hash = HexBytes(ssz.get_hash_tree_root(beacon_state.validators))
    beacon_state_hash = HexBytes(ssz.get_hash_tree_root(beacon_state))

    balances_inclusion_proof = beacon_state.construct_inclusion_proof('balances', balances_hash)
    validators_inclusion_proof = beacon_state.construct_inclusion_proof('validators', validators_hash)

    report_data = OracleReportData(slot, epoch, WithdrawalCreds.Lido, lido_validator_count, 0, lido_sum)

    block_header = BlockHeaderMessage(
        str(slot),
        str(123456),
        BlockRoot(HexStr("fd3cbb81972aa7478f4f4788854428c527771a0b2ef0da5afe1b9325af8f3a7d")),
        StateRoot(HexStr(beacon_state_hash.hex())),
        ((b"\x01" + b"\x00" * 14 + b"\x02") + (b"\x03" + b"\x00" * 14 + b"\x04")).hex()
    )
    beacon_block_fields = [
        int(block_header.slot).to_bytes(32, 'little', signed=False),
        int(block_header.proposer_index).to_bytes(32, 'little', signed=False),
        HexBytes(block_header.parent_root),
        HexBytes(block_header.state_root),
        HexBytes(block_header.body_root)
    ]

    return CircuitInput(
        total_validator_count,
        PublicInput(
            WithdrawalCreds.Lido,
            balances_hash,
            validators_hash,
            slot, epoch
        ),
        PrivateInput(
            validators = beacon_state.validators,
            balances = beacon_state.balances,
            balances_hash = balances_hash,
            validators_hash = validators_hash,
            balances_hash_inclusion_proof = balances_inclusion_proof,
            validators_hash_inclusion_proof = validators_inclusion_proof,
            beacon_block_fields = beacon_block_fields
        ),
        report_data
    )
