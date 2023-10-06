# ZKLLVM Circuit: trustless sanity check for Lido accounting module

Deciphering the name: 

* ZKLLVM Circuit - [circuit][circuit] for generating ZK proofs, based on [ZKLLVM][zkllvm] by [Nil Foundation][nil-foundation]
* Lido accounting module - [accounting module][accounting-module] of [Lido][lido] [oracle][lido-oracle]
* Trustless - requires no trusted setup/operations
* Sanity Check - at this point, the circuit only partially covers accounting module responsibility, and
  and is intended to serve as additional sanity check to prevent wrong or malicious reporting. In the future
  it might grow to completely replace accounting module.

[circuit]: https://docs.nil.foundation/zkllvm/circuit-development/circuit-generation
[zkllvm]: https://docs.nil.foundation/zkllvm/overview/what-is-zkllvm
[nil-foundation]: https://nil.foundation/
[accounting-module]: https://github.com/lidofinance/lido-oracle/tree/develop/src/modules/accounting
[lido]: https://lido.fi/
[lido-oracle]: https://github.com/lidofinance/lido-oracle

## Why, what, how?

See [Detailed Spec][spec] and [Proposal][proposal]   

[spec]: https://docs.google.com/document/d/1d5Ru7WWae-yilXzOVgNS5DNweAMj6FNJrZllvD00mB0
[proposal]: https://research.lido.fi/t/zkllvm-trustless-zk-proof-tvl-oracle/5028

## Input format

**Type aliases:**
* block_type = nil::crypto3::hashes::sha2<256>::block_type


| Argument                                | Type                                        | Description                                                                     |
|-----------------------------------------|---------------------------------------------|---------------------------------------------------------------------------------|
| actual_validator_count                  | size_t                                      | Number of real, non-empty validators and balances in use                        |
| validator_balances                      | std::array<uint64_t, VALIDATORS_COUNT>      | Array of validator balances                                                     |
| validators_pubkeys                      | std::array<block_type, VALIDATORS_COUNT>    | Validators' public keys                                                         |
| validators_withdrawal_credentials       | std::array<block_type, VALIDATORS_COUNT>    | Validators' withdrawal keys                                                     |
| validators_effective_balances           | std::array<uint64_t, VALIDATORS_COUNT>      | Validators' effective balances                                                  |
| validators_slashed                      | std::array<uint64_t, VALIDATORS_COUNT>      | If validator was slashed                                                        |
| validators_activation_eligibility_epoch | std::array<uint64_t, VALIDATORS_COUNT>      | Validators' eligibility epoch                                                   |
| validators_activation_epoch             | std::array<uint64_t, VALIDATORS_COUNT>      | Validators' activation epoch                                                    |
| validators_exit_epoch                   | std::array<uint64_t, VALIDATORS_COUNT>      | Validators' exit epoch                                                          |
| validators_withdrawable_epoch           | std::array<uint64_t, VALIDATORS_COUNT>      | Validators' withdrawable epoch                                                  |
| lido_withdrawal_credentials             | nil::crypto3::hashes::sha2<256>::block_type | Lido withdrawal credentals[^1]                                                  |
| slot                                    | uint64_t                                    | Report slot                                                                     |
| epoch                                   | uint64_t                                    | Report epoch                                                                    |
| expected_total_balance                  | uint64_t                                    | Computed total balance belonging to Lido validators                             |
| expected_all_lido_validators            | uint64_t                                    | Count of all Lido validators                                                    |
| expected_exited_lido_validators         | uint64_t                                    | Count of exited Lido validators                                                 |
| expected_balances_hash                  | block_type                                  | [SSZ Merkleization][ssz] of all balances (`validator_balances` field)           |
| expected_validators_hash                | block_type                                  | [SSZ Merkleization][ssz] of all Validators (all other `validator_*` fields)     |
| beacon_state_hash                       | block_type                                  | Beacon State hash for the corresponding slot                                    |
| beacon_block_hash                       | block_type                                  | Beacon Block hash for the corresponding slot                                    |
| balances_hash_inclusion_proof           | std::array<block_type, 5>                   | Merkle tree inclusion proof for `expected_balances_hash` in `beacon_state_hash` |
| validators_hash_inclusion_proof         | std::array<block_type, 5>                   | Merkle tree inclusion proof for `expected_validators_hash` in `beacon_state_hash` |
| beacon_block_fields                     | std::array<block_type, 5>                   | BeaconBlockHeader fields (for beacon block hash checking)                       |

[ssz]: https://www.ssz.dev/

**Note about VALIDATORS_COUNT constant:** Due to how ZK proof is constructed, the size of the input need 
to be know at compile time; however, actual number of validators in Ethereum network is constantly changing.
To overcome this, we use an `std::array<..., VALIDATORS_COUNT>` that's bigger than an actual count of validators.
This also has direct implications on some "compile-time" steps of preparing the circuit[^2], and also 
significant impact on "runtime" - computational power needed to generate proofs. Hence, while theoretical maximum
is 2**40 ([Validator Registry Limit constant][validator-registry-limit]), we further limit it to a smaller value
that still guarantees to fit validator growth in the near future.

[validator-registry-limit]: https://github.com/ethereum/consensus-specs/blob/dev/specs/phase0/beacon-chain.md#state-list-lengths

[^1]: Withdrawal credentials used by Lido validators
[^2]: namely, memory and time needed to generate assignment and constraints tables