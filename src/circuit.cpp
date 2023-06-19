#include "lib.hpp"

using namespace nil::crypto3;
using namespace nil::crypto3::algebra::curves;

[[circuit]] pallas::base_field_type::value_type circuit(
    std::array<typename pallas::base_field_type::value_type, 0x20> layer_0_leaves
) {
    return merkle_tree_poseidon(layer_0_leaves);
}