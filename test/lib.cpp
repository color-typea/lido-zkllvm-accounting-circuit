#define BOOST_TEST_MODULE Test1
#include <boost/test/unit_test.hpp>
#include <boost/test/data/test_case.hpp>
#include <filesystem>

#include "lib.hpp"

#include <common.hpp>

#ifdef TEST_TRACING
#include <tracing.hpp>
#endif

using namespace std;
namespace fs = std::filesystem;


// vector<tuple<fs::path, string>> examples2 = {
// 	std::make_tuple(DATA_FOLDER / "balances_50sequential.inp", "517be596c3bafba3de9a35dc911215a2154b796fbccf2a64350609dd59ecfc9b"),
// };

vector<tuple<fs::path, unsigned long long, const char*>> examples2 = {
	std::make_tuple(
		DATA_FOLDER / "balances_50sequential.inp", 
		1225000000000000000ul,
		"517be596c3bafba3de9a35dc911215a2154b796fbccf2a64350609dd59ecfc9b"
	),
};


vector<tuple<int, int, int>> examples = {
	std::make_tuple(1, -1, 0),
	std::make_tuple(1, 2, 3),
	std::make_tuple(10, 1, 11),
	std::make_tuple(3, 4, 7),
};

BOOST_AUTO_TEST_SUITE(lib_test)

BOOST_DATA_TEST_CASE(test_sum, boost::unit_test::data::make(examples), left, right, expected_result) {
	BOOST_CHECK(sum(left, right) == expected_result);
}

BOOST_DATA_TEST_CASE(test_sum_list, boost::unit_test::data::make(examples2), input_file, expected_sum, expected_hash) {
	vector<unsigned long long> balances = readVectorFrom<unsigned long long>(input_file);
#ifdef TEST_TRACING
	std::cout << "\n===== Tracing ======\n";
	std::cout << "Balances:";
	print_vector(std::cout, balances);
	std::cout << "\n===== Tracing End ======\n";
#endif
	unsigned long long balance_sum = sum_balances(balances);
	BOOST_TEST(balance_sum == expected_sum);
}

BOOST_AUTO_TEST_SUITE_END()