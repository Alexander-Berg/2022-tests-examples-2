#include <gtest/gtest.h>

#include <sstream>
#include <limits>
#include <climits>

#include <yson/scalar.hpp>
#include "detail/writer.hpp"


namespace {

constexpr
yson::string_ref operator "" _sv(const char* str, size_t len)
{
    return {str, len};
}

template<typename Writer, typename Function>
std::string with_writer(Function&& function)
{
    std::ostringstream stream;
    auto writer = yson::detail::make_writer<Writer>(
        yson::output::from_ostream(stream),
        yson::stream_type::node
    );

    function(writer);

    return stream.str();
}

template<typename Writer>
std::string to_yson_string(const yson::scalar& value)
{
    return with_writer<Writer>([&](yson::writer& writer) {
        writer.begin_stream().scalar(value).end_stream();
    });
}

template<typename T>
std::string to_yson_binary_string(T&& value)
{
    return to_yson_string<yson::detail::binary_writer>(std::forward<T>(value));
}

template<typename T>
std::string to_yson_text_string(T&& value)
{
    return to_yson_string<yson::detail::text_writer>(std::forward<T>(value));
}

} // anonymous namespace


// =================== Text format =====================

TEST(writer, text_entity)
{
    EXPECT_EQ(
        "#",
        to_yson_text_string(yson::scalar {})
    );
}


TEST(writer, text_boolean)
{
    EXPECT_EQ(
        "%false",
        to_yson_text_string(yson::scalar {false})
    );
    EXPECT_EQ(
        "%true",
        to_yson_text_string(yson::scalar {true})
    );
}


TEST(writer, text_int64)
{
    EXPECT_EQ(
        "0",
        to_yson_text_string(yson::scalar {int64_t {0}})
    );
    EXPECT_EQ(
        "200",
        to_yson_text_string(yson::scalar {int64_t {200}})
    );
    EXPECT_EQ(
        "20000",
        to_yson_text_string(yson::scalar {int64_t {20000}})
    );
    EXPECT_EQ(
        "200000000",
        to_yson_text_string(yson::scalar {int64_t {200000000}})
    );
    EXPECT_EQ(
        "20000000000000000",
        to_yson_text_string(yson::scalar {int64_t {20000000000000000}})
    );
    EXPECT_EQ(
        "9223372036854775807",
        to_yson_text_string(yson::scalar {int64_t {INT64_MAX}})
    );

    EXPECT_EQ(
        "-200",
        to_yson_text_string(yson::scalar {int64_t {-200}})
    );
    EXPECT_EQ(
        "-20000",
        to_yson_text_string(yson::scalar {int64_t {-20000}})
    );
    EXPECT_EQ(
        "-200000000",
        to_yson_text_string(yson::scalar {int64_t {-200000000}})
    );
    EXPECT_EQ(
        "-20000000000000000",
        to_yson_text_string(yson::scalar {int64_t {-20000000000000000}})
    );
    EXPECT_EQ(
        "-9223372036854775808",
        to_yson_text_string(yson::scalar {int64_t {INT64_MIN}})
    );
}


TEST(writer, text_uint64)
{
    EXPECT_EQ(
        "0u",
        to_yson_text_string(yson::scalar {uint64_t {0}})
    );
    EXPECT_EQ(
        "200u",
        to_yson_text_string(yson::scalar {uint64_t {200}})
    );
    EXPECT_EQ(
        "20000u",
        to_yson_text_string(yson::scalar {uint64_t {20000}})
    );
    EXPECT_EQ(
        "200000000u",
        to_yson_text_string(yson::scalar {uint64_t {200000000}})
    );
    EXPECT_EQ(
        "20000000000000000u",
        to_yson_text_string(yson::scalar {uint64_t {20000000000000000}})
    );
    EXPECT_EQ(
        "9223372036854775807u",
        to_yson_text_string(yson::scalar {uint64_t {INT64_MAX}})
    );
    EXPECT_EQ(
        "18446744073709551615u",
        to_yson_text_string(yson::scalar {uint64_t {UINT64_MAX}})
    );
}


TEST(writer, text_float64)
{
    // XXX: How?
    EXPECT_EQ(
        "%inf",
        to_yson_text_string(yson::scalar {
            std::numeric_limits<double>::infinity()
        })
    );
    EXPECT_EQ(
        "%-inf",
        to_yson_text_string(yson::scalar {
            -std::numeric_limits<double>::infinity()
        })
    );
    EXPECT_EQ(
        "%nan",
        to_yson_text_string(yson::scalar {
            std::numeric_limits<double>::quiet_NaN()
        })
    );
}

TEST(writer, text_string)
{
    EXPECT_EQ(
        R"("")",
        to_yson_text_string(yson::scalar {""})
    );
    EXPECT_EQ(
        R"("hello")",
        to_yson_text_string(yson::scalar {"hello"})
    );
    EXPECT_EQ(
        R"("hello\nworld")",
        to_yson_text_string(yson::scalar {"hello\nworld"})
    );
}


// =================== Binary format =====================

TEST(writer, binary_entity)
{
    EXPECT_EQ(
        "#",
        to_yson_binary_string(yson::scalar {})
    );
}


TEST(writer, binary_boolean)
{
    EXPECT_EQ(
        "\x4"_sv,
        to_yson_binary_string(yson::scalar {false})
    );
    EXPECT_EQ(
        "\x5"_sv,
        to_yson_binary_string(yson::scalar {true})
    );
}


TEST(writer, binary_int64)
{
    EXPECT_EQ(
        "\x2\0"_sv,
        to_yson_binary_string(yson::scalar {int64_t {0}})
    );
    EXPECT_EQ(
        "\x2\x90\x3"_sv,
        to_yson_binary_string(yson::scalar {int64_t {200}})
    );
    EXPECT_EQ(
        "\x2\xC0\xB8\x2"_sv,
        to_yson_binary_string(yson::scalar {int64_t {20000}})
    );
    EXPECT_EQ(
        "\x2\x80\x88\xDE\xBE\x1"_sv,
        to_yson_binary_string(yson::scalar {int64_t {200000000}})
    );
    EXPECT_EQ(
        "\x2\x80\x80\x90\xF8\x9B\xF9\x86G"_sv,
        to_yson_binary_string(yson::scalar {int64_t {20000000000000000}})
    );
    EXPECT_EQ(
        "\x2\xFE\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x1"_sv,
        to_yson_binary_string(yson::scalar {int64_t {INT64_MAX}})
    );

    EXPECT_EQ(
        "\x2\x8F\x3"_sv,
        to_yson_binary_string(yson::scalar {int64_t {-200}})
    );
    EXPECT_EQ(
        "\x2\xBF\xB8\x2"_sv,
        to_yson_binary_string(yson::scalar {int64_t {-20000}})
    );
    EXPECT_EQ(
        "\x2\xFF\x87\xDE\xBE\x1"_sv,
        to_yson_binary_string(yson::scalar {int64_t {-200000000}})
    );
    EXPECT_EQ(
        "\x2\xFF\xFF\x8F\xF8\x9B\xF9\x86G"_sv,
        to_yson_binary_string(yson::scalar {int64_t {-20000000000000000}})
    );
    EXPECT_EQ(
        "\x2\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x1"_sv,
        to_yson_binary_string(yson::scalar {int64_t {INT64_MIN}})
    );
}


TEST(writer, binary_uint64)
{
    EXPECT_EQ(
        "\x6\0"_sv,
        to_yson_binary_string(yson::scalar {uint64_t {0}})
    );
    EXPECT_EQ(
        "\x6\xC8\x1"_sv,
        to_yson_binary_string(yson::scalar {uint64_t {200}})
    );
    EXPECT_EQ(
        "\x6\xA0\x9C\x1"_sv,
        to_yson_binary_string(yson::scalar {uint64_t {20000}})
    );
    EXPECT_EQ(
        "\x6\x80\x84\xAF_"_sv,
        to_yson_binary_string(yson::scalar {uint64_t {200000000}})
    );
    EXPECT_EQ(
        "\x6\x80\x80\x88\xFC\xCD\xBC\xC3#"_sv,
        to_yson_binary_string(yson::scalar {uint64_t {20000000000000000}})
    );
    EXPECT_EQ(
        "\x6\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x7F"_sv,
        to_yson_binary_string(yson::scalar {uint64_t {INT64_MAX}})
    );
    EXPECT_EQ(
        "\x6\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x1"_sv,
        to_yson_binary_string(yson::scalar {uint64_t {UINT64_MAX}})
    );
}


TEST(writer, binary_float64)
{
    // XXX: How?
    EXPECT_EQ(
        "\x03\x00\x00\x00\x00\x00\x00\xf0\x7f"_sv,
        to_yson_binary_string(yson::scalar {
            std::numeric_limits<double>::infinity()
        })
    );
    EXPECT_EQ(
        "\x03\x00\x00\x00\x00\x00\x00\xf0\xff"_sv,
        to_yson_binary_string(yson::scalar {
            -std::numeric_limits<double>::infinity()
        })
    );
    EXPECT_EQ(
        "\x03\x00\x00\x00\x00\x00\x00\xf8\x7f"_sv,
        to_yson_binary_string(yson::scalar {
            std::numeric_limits<double>::quiet_NaN()
        })
    );
}

TEST(writer, binary_string)
{
    EXPECT_EQ(
        "\x1\0"_sv,
        to_yson_binary_string(yson::scalar {""})
    );
    EXPECT_EQ(
        "\x1\nhello"_sv,
        to_yson_binary_string(yson::scalar {"hello"})
    );
    EXPECT_EQ(
        "\x1\x16hello\nworld"_sv,
        to_yson_binary_string(yson::scalar {"hello\nworld"})
    );
}
