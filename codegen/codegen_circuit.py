import json
import math
import os
from typing import Dict
import dataclasses
from jinja2 import Template

from circuit_input import generate_input

CUR_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.dirname(CUR_DIR)
CIRCUIT_DIR = os.path.join(PROJECT_DIR, "src")

CIRCUIT = os.path.join(CIRCUIT_DIR, "circuit.cpp")
PRIVATE_INPUT = os.path.join(CIRCUIT_DIR, "circuit_private.inp")
PUBLIC_INPUT = os.path.join(CIRCUIT_DIR, "circuit_public.inp")

from typing import Callable, Iterable, TypeVar

HashType = (str, str)
T = TypeVar("T")
TOut = TypeVar("TOut")


class InputWriter:
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
    def as_hash(cls, value: bytes) -> HashType:
        assert len(value) <= 32, f"Serializing as hash only support values shorter than 32 bytes, {len(value)} given"
        low = int.from_bytes(value[:16], 'little', signed=False)
        high = int.from_bytes(value[16:], 'little', signed=False)
        return {"vector": [{"field": str(low)}, {"field": str(high)}]}

@dataclasses.dataclass
class TemplateParams:
    problem_size_log2: int
    subproblem_count_log2: int

    def computed_values(self) -> Dict[str, any]:
        subproblem_count = 2 ** self.subproblem_count_log2
        return {
            "problem_size": self.problem_size,
            "subproblem_count": subproblem_count,
            "subproblem_size": math.ceil(self.problem_size / subproblem_count),
        }

    @property
    def problem_size(self):
        return 2 ** self.problem_size_log2

    def to_template(self):
        return {
            **dataclasses.asdict(self),
            **self.computed_values()
        }
    
def main():
    with open(os.path.join(CUR_DIR, "circuit.cpp")) as template_file:
        template = Template(template_file.read())

    problem_size_log2 = 4
    subproblem_count_log2 = 2
    total_validator_count = 12
    lido_validators_count = 7
    assert(2**problem_size_log2 >= total_validator_count >= lido_validators_count)

    template_input = TemplateParams(
        problem_size_log2 = problem_size_log2,
        subproblem_count_log2 = subproblem_count_log2,
    )

    with open(CIRCUIT, "w") as circuit_file:
        circuit_file.write(template.render(template_input.to_template()))

    circuit_input = generate_input(2**problem_size_log2, total_validator_count, lido_validators_count)
    with open(PRIVATE_INPUT, "w") as private_input_file:
        json.dump(
            circuit_input.serialize_public_for_proof_generator(),
            private_input_file,
            indent=True,
        )

    with open(PUBLIC_INPUT, "w") as public_input_file:
        json.dump(
            circuit_input.serialize_private_for_proof_generator(),
            public_input_file,
            indent=True,
        )


if __name__ == '__main__':
    main()