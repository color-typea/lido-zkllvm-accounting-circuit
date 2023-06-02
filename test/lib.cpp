#define BOOST_TEST_MODULE Test1
#include <boost/test/included/unit_test.hpp>
#include <include/circuit/lib.hpp>

BOOST_AUTO_TEST_CASE(test1a)
{
	BOOST_CHECK(sum(1, 2) == 3);
	BOOST_CHECK(sum(3, 4) == 7);
}
