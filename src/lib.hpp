 #include <vector>
 #include <nil/crypto3/hash/algorithm/hash.hpp>
//  #include <nil/crypto3/hash/sha2.hpp>
#include <nil/crypto3/algebra/curves/pallas.hpp>
#include <nil/crypto3/hash/poseidon.hpp>

using namespace nil::crypto3;
using namespace nil::crypto3::algebra::curves;


using balance_type = unsigned long long;
//  using hash_type = hashes::sha2<256>;
//  using element_type = hash_type::block_type;

int sum(int a, int b) {
    return a + b;
}

unsigned long long sum_balances(std::vector<balance_type> input) {
    return std::accumulate(input.begin(), input.end(), 0ull);
}

pallas::base_field_type::value_type merkle_tree_poseidon(
    std::array<typename pallas::base_field_type::value_type, 0x20> layer_0_leaves
) {
    
    std::array<typename pallas::base_field_type::value_type, 0x10> layer_1_leaves;
    std::size_t layer_1_size = 0x10;
    std::array<typename pallas::base_field_type::value_type, 0x8> layer_2_leaves;
    std::size_t layer_2_size = 0x8;
    std::array<typename pallas::base_field_type::value_type, 0x4> layer_3_leaves;
    std::size_t layer_3_size = 0x4;
    std::array<typename pallas::base_field_type::value_type, 0x2> layer_4_leaves;
    std::size_t layer_4_size = 0x2;
    typename pallas::base_field_type::value_type root;

    for (std::size_t leaf_index = 0; leaf_index < layer_1_size; leaf_index++) {
    layer_1_leaves[leaf_index] =
        hash<hashes::poseidon>(layer_0_leaves[2 * leaf_index], layer_0_leaves[2 * leaf_index + 1]);
    }

    for (std::size_t leaf_index = 0; leaf_index < layer_2_size; leaf_index++) {
        layer_2_leaves[leaf_index] =
            hash<hashes::poseidon>(layer_1_leaves[2 * leaf_index], layer_1_leaves[2 * leaf_index + 1]);
    }

    for (std::size_t leaf_index = 0; leaf_index < layer_3_size; leaf_index++) {
        layer_3_leaves[leaf_index] =
            hash<hashes::poseidon>(layer_2_leaves[2 * leaf_index], layer_2_leaves[2 * leaf_index + 1]);
    }

    for (std::size_t leaf_index = 0; leaf_index < layer_4_size; leaf_index++) {
        layer_4_leaves[leaf_index] =
            hash<hashes::poseidon>(layer_3_leaves[2 * leaf_index], layer_3_leaves[2 * leaf_index + 1]);
    }

    root = hash<hashes::poseidon>(layer_4_leaves[0], layer_4_leaves[1]);

    return root;
}


// element_type 
// lift_into_hash_value(balance_type balance) {
//     // in ssz spec, if a value is < 32 bytes, it's hash is the value itself
//     element_type result;
//     for (size_t idx = 0; idx < sizeof(balance_type); idx++) {
//         result[idx] = balance && (0xff << idx);
//     }
//     return result;
// }

// element_type 
// hash2(element_type left, element_type right) {
//     return nil::crypto3::hash<hashes::sha2<256>, hashes::sha2<256>::block_type>(left, right);
// }

// element_type 
// hash_tree_root_(std::vector<element_type>& input) {
//     std::size_t current_layer_size = input.size();
//     std::vector<element_type> working_copy(input);
//     element_type zero = lift_into_hash_value(0);
//     element_type zerohash = hash2(zero, zero);

//     while (current_layer_size > 1) {
//         std::size_t next_layer_size = current_layer_size / 2;
//         // fast forward until before computing last new element
//         std::size_t fast_forward_steps = next_layer_size - 1;
//         for (std::size_t idx = 0; idx < fast_forward_steps; idx++) {
//             working_copy[idx] = hash2(working_copy[2 * idx], working_copy[2 * idx + 1]);
//         }
//         // compute the last new element
//         std::size_t last_new_element_idx = fast_forward_steps;
//         element_type last_new_element_right_leaf = (2 * last_new_element_idx + 1 < current_layer_size)
//             ? working_copy[2 * last_new_element_idx + 1]
//             : zerohash;
//         working_copy[last_new_element_idx] = hash2(working_copy[2 * last_new_element_idx], last_new_element_right_leaf);

//         // go one level up
//         zerohash = hash2(zerohash, zerohash);
//         current_layer_size = next_layer_size;
//     }

//     return working_copy[0];
// }


// element_type 
// hash_tree_root(std::vector<balance_type> input) {
//     std::vector<element_type> leafs;
//     std::transform(input.begin(), input.end(), back_inserter(leafs), lift_into_hash_value);
//     return hash_tree_root_(leafs);
// }