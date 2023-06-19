#include <nil/crypto3/hash/algorithm/hash.hpp>
#include <nil/crypto3/hash/sha2.hpp>

using namespace nil::crypto3;

#ifdef __ZKLLVM__
// block_type = curves::pallas::base_field_type = fields::pallas_base_field = field<255> => 255 bits?
using hash_return_type = hashes::sha2<256>::block_type;
// copypasted from zkllvm/examples/sha2_256.cpp
hash_return_type sha256_pair(
    typename hashes::sha2<256>::block_type first_input_block,
    typename hashes::sha2<256>::block_type second_input_block
) {
    typename hashes::sha2<256>::block_type hash_result = hash<hashes::sha2<256>>(first_input_block, second_input_block);
    return hash_result;
}
#else
template<typename HashType>
typename HashType::digest_type hash_pair(typename HashType::block_type block0, typename HashType::block_type block1) {
  accumulator_set<HashType> acc;
  acc(block0, accumulators::bits = HashType::block_bits);
  acc(block1, accumulators::bits = HashType::block_bits);

  return accumulators::extract::hash<HashType>(acc);
}

// nil::crypto3::static_digest<256UL> = 4 * 8 * 16 = 256 bits
using hash_return_type = hashes::sha2<256>::digest_type;

hash_return_type sha256_pair(
    typename hashes::sha2<256>::block_type first_input_block,
    typename hashes::sha2<256>::block_type second_input_block
) {
    return hash_pair<hashes::sha2<256>>(first_input_block, second_input_block);
}
#endif
