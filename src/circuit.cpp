#include <nil/crypto3/hash/algorithm/hash.hpp>
#include <nil/crypto3/hash/sha2.hpp>
#include <nil/crypto3/algebra/curves/pallas.hpp>

using namespace nil::crypto3;
using namespace nil::crypto3::algebra::curves;

using hash_type = hashes::sha2<256>;
using block_type = hash_type::block_type;
using pallas_element = pallas::base_field_type::value_type;

[[circuit]] bool circuit(
    std::array<block_type, 16> balance_leafs,
    block_type expected_sum,
    block_type expected_hash
) {
    return true;
}