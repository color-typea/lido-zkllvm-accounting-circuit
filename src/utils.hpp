#pragma once

template <std::size_t Last = 0, typename TF, typename TArray, typename... TRest>
constexpr auto with_acc_sizes(TF &&func, const TArray &array, const TRest &...rest) {
    func(array, std::integral_constant<std::size_t, Last>{});

    if constexpr (sizeof...(TRest) != 0)
    {
        with_acc_sizes<Last + std::tuple_size_v<TArray>>(func, rest...);
    }
}

template <typename T, std::size_t... Sizes>
constexpr auto concat(const std::array<T, Sizes> &...arrays) {
    std::array<T, (Sizes + ...)> result{};

    with_acc_sizes([&](const auto &arr, auto offset)
                    { std::copy(arr.begin(), arr.end(), result.begin() + offset); },
                    arrays...);

    return result;
}

template <typename T, std::size_t InSize, std::size_t OutSize>
constexpr std::array<T, OutSize> padTo(const std::array<T, InSize> &array, const T &elem) {
    constexpr size_t paddingSize = OutSize - InSize;
    static_assert(paddingSize > 0);
    std::array<T, paddingSize> padding {};
    padding.fill(elem);

    return concat(array, padding);
}

template<typename TVal> TVal toLittleEndian(TVal value);

template<> uint32_t toLittleEndian<uint32_t>(uint32_t value) {
    return __builtin_bswap32(value);
}

template<> uint64_t toLittleEndian<uint64_t>(uint64_t value) {
    return __builtin_bswap64(value);
}