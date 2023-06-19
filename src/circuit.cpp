#include "hash.hpp"

using namespace nil::crypto3;

// works like this, but hash_return_type is defined differently 
// and hashes::sha2<256>::block_type seems to have different length (512 vs. 255 bits)
// [[circuit]] hash_return_type circuit(
[[circuit]] hashes::sha2<256>::digest_type circuit(
    typename hashes::sha2<256>::block_type first_input_block,
    typename hashes::sha2<256>::block_type second_input_block
) {
    return sha256_pair(first_input_block, second_input_block);
}
