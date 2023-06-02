#define BOOST_TEST_MODULE LibTest
#include <boost/test/unit_test.hpp>
#include <boost/test/data/test_case.hpp>
#include <boost/algorithm/hex.hpp>

#include <nil/crypto3/hash/algorithm/hash.hpp>
#include <nil/crypto3/hash/sha2.hpp>

#include "hash.hpp"
#include "utils.hpp"

#include "tracing.hpp"

using hash_type = hashes::sha2<256>;
using half_block = std::array<hash_type::block_type::value_type, hash_type::block_words / 2>;
using word_type = hash_type::word_type;

BOOST_AUTO_TEST_SUITE(hash_test)

BOOST_AUTO_TEST_CASE(hash_single_zeroes) {
    std::string expected = "f5a5fd42d16a20302798ef6ed309979b43003d2320d9f0e8ea9831a92759fb4b";

    auto left = half_block {toLittleEndian(0u)};
    auto right = half_block {toLittleEndian(0u)};
    typename hash_type::block_type input = concat(left, right);
    
    typename hash_type::digest_type root = hash_one<hash_type>(input);
    auto actual = std::to_string(root);
    BOOST_TEST(actual == expected);
}

BOOST_AUTO_TEST_CASE(hash_single_uint32_partial_values) {
    std::string expected = "b92cecc8837b78ea9df93e9f3e2487c023eda0274819613b9b13ff1090149ee2";

    auto left = half_block {toLittleEndian(0xffffu)};
    auto right = half_block {toLittleEndian(0xabcdu)};
    typename hash_type::block_type input = concat(left, right);

    typename hash_type::digest_type root = hash_one<hash_type>(input);
    auto actual = std::to_string(root);
    BOOST_TEST(actual == expected);
}

BOOST_AUTO_TEST_CASE(hash_single_uint32_full_values) {
    std::string expected = "bc71002c1f7598515c518bf0bc9201e69f6c471388f4ede4334ee9acfbd06a88";

    auto left = half_block {toLittleEndian(0xffffffffu)};
    auto right = half_block {toLittleEndian(0xabcdef01u)};
    typename hash_type::block_type input = concat(left, right);

    typename hash_type::digest_type root = hash_one<hash_type>(input);
    auto actual = std::to_string(root);
    BOOST_TEST(actual == expected);
}

BOOST_AUTO_TEST_CASE(hash_single_uint64_partial_values) {
    std::string expectedStr = "2301efcdab000000000000000000000000000000000000000000000000000000eeddccbbaa000000000000000000000000000000000000000000000000000000";
    hash_type::block_type expected;    
    boost::algorithm::unhex(expectedStr, expected.begin());

    printBlockType(expected);
    
    hash_type::block_type block = padAndJoinToBlock<hash_type, 2, 2>(
        uint64ToLittleEndianWords<hash_type>(0xabcdef0123ul), 
        uint64ToLittleEndianWords<hash_type>(0xaabbccddeeul)
    );
    printBlockType(block);
    BOOST_TEST(block == expected);
}

BOOST_AUTO_TEST_CASE(hash_single_uint64_full_values) {
    std::string expectedStr = "452301efcdab0000000000000000000000000000000000000000000000000000ffeeddccbbaa0000000000000000000000000000000000000000000000000000";
    hash_type::block_type expected;    
    boost::algorithm::unhex(expectedStr, expected.begin());

    printBlockType(expected);
    
    hash_type::block_type block = padAndJoinToBlock<hash_type, 2, 2>(
        uint64ToLittleEndianWords<hash_type>(0xabcdef012345ul), 
        uint64ToLittleEndianWords<hash_type>(0xaabbccddeefful)
    );
    printBlockType(block);
    BOOST_TEST(block == expected);
}

BOOST_AUTO_TEST_SUITE_END()
