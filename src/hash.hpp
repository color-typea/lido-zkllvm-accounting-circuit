#include <nil/crypto3/hash/algorithm/hash.hpp>
#include <nil/crypto3/hash/sha2.hpp>

#include "utils.hpp"

using namespace nil::crypto3;

#ifdef __ZKLLVM__
template<typename HashType>
typename HashType::digest_type hash_single(typename HashType::block_type block0) {
      return hash<HashType>(block0);
}

template<typename HashType>
typename HashType::digest_type hash_pair(
    typename HashType::block_type left,
    typename HashType::block_type right
) {
    return hash<HashType>(left, right);
}
#else
template<typename HashType>
typename HashType::digest_type hash_one(typename HashType::block_type block0) {
  accumulator_set<HashType> acc;
  acc(block0, accumulators::bits = HashType::block_bits);

  return accumulators::extract::hash<HashType>(acc);
}

template<typename HashType>
typename HashType::digest_type hash_pair(typename HashType::block_type block0, typename HashType::block_type block1) {
  accumulator_set<HashType> acc;
  acc(block0, accumulators::bits = HashType::block_bits);
  acc(block1, accumulators::bits = HashType::block_bits);

  return accumulators::extract::hash<HashType>(acc);
}
#endif

template<typename HashType>
std::array<typename HashType::word_type, sizeof(uint64_t) / sizeof(typename HashType::word_type)> uint64ToLittleEndianWords(uint64_t input);
// std::array<typename HashType::word_type, sizeof(uint64_t) / sizeof(typename HashType::word_type)> uint64ToLittleEndianWords(uint64_t input);
//     std::array<uint64_t, 1> value = {toLittleEndian(input});
//     return reinterpret_cast<std::array<typename HashType::word_type, sizeof(uint64_t) / sizeof(typename HashType::word_type)>>(value);
// }

template<> std::array<typename hashes::sha2<256>::word_type, 2> uint64ToLittleEndianWords<hashes::sha2<256>>(uint64_t input) {
    auto target = toLittleEndian(input);
    return std::array<typename hashes::sha2<256>::word_type, 2> {
        (target >> 32) & 0xffffffff,
        (target >>  0) & 0xffffffff
    };
}

template<typename HashType, size_t InSize>
typename HashType::block_type padToBlock(const std::array<typename HashType::word_type, InSize> &input) {
    typename HashType::word_type paddingElement = 0;
    return padTo<typename HashType::word_type, InSize, HashType::block_words>(input, paddingElement);
}

template<typename HashType, size_t InSize1, size_t InSize2>
typename HashType::block_type padAndJoinToBlock(
    const std::array<typename HashType::word_type, InSize1> &input1,
    const std::array<typename HashType::word_type, InSize1> &input2
) {
    constexpr size_t half_block_length = HashType::block_words / 2;

    return concat(
        padTo<typename HashType::word_type, InSize1, half_block_length>(input1, 0),
        padTo<typename HashType::word_type, InSize2, half_block_length>(input2, 0)
    );
}