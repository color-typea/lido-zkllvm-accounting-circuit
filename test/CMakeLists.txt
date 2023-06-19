#---------------------------------------------------------------------------#
# Copyright (c) 2018-2020 Mikhail Komarov <nemo@nil.foundation>
#
# Distributed under the Boost Software License, Version 1.0
# See accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt
#---------------------------------------------------------------------------#

include(CMTest)

if(NOT Boost_UNIT_TEST_FRAMEWORK_FOUND)
    cm_find_package(Boost REQUIRED COMPONENTS unit_test_framework)
endif()

cm_test_link_libraries(${Boost_LIBRARIES} template_lib)
option(TEST_TRACING "OUTPUT TRACE DATA" OFF)

macro(define_test name)
    cm_test(NAME ${name}_test SOURCES ${name}.cpp)

    set_target_properties(${name}_test PROPERTIES CXX_STANDARD 20 CXX_STANDARD_REQUIRED TRUE)

    get_target_property(target_type Boost::unit_test_framework TYPE)
    if(target_type STREQUAL "SHARED_LIB")
        target_compile_definitions(${name}_test PRIVATE BOOST_TEST_DYN_LINK)
    elseif(target_type STREQUAL "STATIC_LIB")
    endif()
endmacro()

set(TESTS_NAMES
    "hash"
)

foreach(TEST_NAME ${TESTS_NAMES})
    define_test(${TEST_NAME})
endforeach()