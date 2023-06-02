#include <iostream>
#include <iomanip>

// Copied from boost/random/detail/vector_io.hpp
template<class CharT, class Traits, class T>
void print_vector(std::basic_ostream<CharT, Traits>& os,
                  const std::vector<T>& vec)
{
    // #ifdef TEST_TRACING
    typename std::vector<T>::const_iterator
        iter = vec.begin(),
        end =  vec.end();
    os << os.widen('[');
    if(iter != end) {
        os << *iter;
        ++iter;
        for(; iter != end; ++iter)
        {
            os << os.widen(' ') << *iter;
        }
    }
    os << os.widen(']');
    // #endif
}

template <typename BlockType>
void printBlockType(BlockType &block_value) {
    // #ifdef TEST_TRACING
    constexpr size_t value_size =  sizeof(typename BlockType::value_type);
    for (auto value: block_value) {
        std::cout << std::hex << std::setfill('0') << std::setw(value_size * 2) << value;
    }
    std::cout << "\n";
    // #endif
}