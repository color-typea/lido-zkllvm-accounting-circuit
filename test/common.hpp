#include <filesystem>
#include <iterator>
#include <fstream>
#include <stdexcept>
#include "boost/format.hpp"

namespace fs = std::filesystem;

using namespace std;

const fs::path DATA_FOLDER = fs::current_path() / "data";



template <typename TOut>
vector<TOut> readVectorFrom(fs::path source) {
    std::ifstream input_stream(source);
    if (!input_stream.is_open()) {
        auto message = boost::format("Couldn't open file %s") % source;
        throw std::runtime_error(message.str());
    }
    std::istream_iterator<TOut> start(input_stream), end;
    std::vector<TOut> result(start, end);

    input_stream.close();

    return result;
}