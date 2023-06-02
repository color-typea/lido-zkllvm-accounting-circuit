#ifdef TEST_TRACING
#include <iostream>

// Copied from boost/random/detail/vector_io.hpp
template<class CharT, class Traits, class T>
void print_vector(std::basic_ostream<CharT, Traits>& os,
                  const std::vector<T>& vec)
{
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
}
#endif