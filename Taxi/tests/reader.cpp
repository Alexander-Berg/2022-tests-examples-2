#include <gtest/gtest.h>

#include <climits>

#include <yson/reader.hpp>
#include <yson/range.hpp>
#include <yson/exceptions.hpp>

#include "detail/macros.hpp"
#include "detail/cescape.hpp"

namespace {

constexpr
yson::string_ref operator "" _sv(const char* str, size_t len)
{
    return {str, len};
}

yson::reader memory_reader(yson::string_ref data, yson::stream_type mode)
{
    return yson::reader(
        yson::input::from_memory(data),
        mode
    );
}

template<typename T>
void expect_scalar(const yson::scalar& scalar, T value) {
    ASSERT_EQ(yson::scalar {value}, scalar);
}

template<>
void expect_scalar(const yson::scalar& scalar, double value) {
    ASSERT_EQ(yson::scalar_type::float64, scalar.type());
    ASSERT_DOUBLE_EQ(value, scalar.as_float64());
}

template<typename T>
void test_scalar(yson::string_ref data, T value)
{
    SCOPED_TRACE(yson::detail::cescape::quote(data));
    auto reader = memory_reader(data, yson::stream_type::node);

    try {
        ASSERT_EQ(yson::event_type::begin_stream, reader.next_event().type());
        {
            auto& event = reader.next_event();
            ASSERT_EQ(yson::event_type::scalar, event.type());
            expect_scalar(event.as_scalar(), value);
        }
        ASSERT_EQ(yson::event_type::end_stream, reader.next_event().type());
    } catch (const std::exception& err) {
        ADD_FAILURE() << err.what();
    }
}

void consume(yson::string_ref data, yson::stream_type mode = yson::stream_type::node)
{
    SCOPED_TRACE(yson::detail::cescape::quote(data));
    auto input_range = yson::stream_events_range(
        yson::input::from_memory(data),
        mode
    );
    for(auto& event: input_range) {
        (void) event;
    }
}

#define ACCEPT(...) EXPECT_NO_THROW(consume(__VA_ARGS__))
#define REJECT(...) EXPECT_THROW(consume(__VA_ARGS__), yson::exception::bad_input)

} // anonymous namespace


TEST(reader, scalar_entity)
{
    test_scalar("#"_sv, yson::scalar {});
}


TEST(reader, scalar_boolean)
{
    test_scalar("%true"_sv, true);
    test_scalar("%false"_sv, false);

    test_scalar("\x05"_sv, true);
    test_scalar("\x04"_sv, false);

    REJECT("%");
    REJECT("%trueth");
    REJECT("%tru");
    REJECT("%falseth");
    REJECT("%fals");
    REJECT("%hithere");
}


TEST(reader, scalar_int64)
{
    test_scalar("1"_sv, int64_t {1});
    test_scalar("+1"_sv, int64_t {1});
    test_scalar("100000"_sv, int64_t {100000});
    test_scalar("+100000"_sv, int64_t {100000});
    test_scalar("-100000"_sv, int64_t {-100000});
    test_scalar("9223372036854775807"_sv, int64_t {9223372036854775807});
    test_scalar("+9223372036854775807"_sv, int64_t {9223372036854775807});

    test_scalar("\x02\x02"_sv, int64_t {1});
    test_scalar("\x02\xc0\x9a\x0c"_sv, int64_t {100000});
    test_scalar("\x02\xbf\x9a\x0c"_sv, int64_t {-100000});
    test_scalar("\x02\xfe\xff\xff\xff\xff\xff\xff\xff\xff\x01"_sv, int64_t {9223372036854775807});

    REJECT("1a2");
    REJECT("1-1-1-1");
    REJECT("1+0");
}

TEST(reader, scalar_uint64)
{
    test_scalar("1u"_sv, uint64_t {1});
    test_scalar("+1u"_sv, uint64_t {1});
    test_scalar("100000u"_sv, uint64_t {100000});
    test_scalar("+100000u"_sv, uint64_t {100000});
    test_scalar("9223372036854775807u"_sv, uint64_t {9223372036854775807u});
    test_scalar("+9223372036854775807u"_sv, uint64_t {9223372036854775807u});
    test_scalar("18446744073709551615u"_sv, uint64_t {18446744073709551615u});
    test_scalar("+18446744073709551615u"_sv, uint64_t {18446744073709551615u});

    REJECT("1a2u");
    REJECT("1-1-1-1u");
    REJECT("1+0u");

    // TODO: binary
}

TEST(reader, scalar_float64)
{
    test_scalar("0.0"_sv, double {0.0});
    test_scalar("+0.0"_sv, double {0.0});
    test_scalar("+.0"_sv, double {0.0});
    test_scalar("+.5"_sv, double {0.5});
    test_scalar("-.5"_sv, double {-0.5});
    test_scalar("1.0"_sv, double {1.0});
    test_scalar("+1.0"_sv, double {1.0});
    test_scalar("-1.0"_sv, double {-1.0});
    test_scalar("1000.0"_sv, double {1000.0});
    test_scalar("+1000.0"_sv, double {1000.0});
    test_scalar("-1000.0"_sv, double {-1000.0});
    test_scalar("1e12"_sv, double {1e12});
    test_scalar("1e+12"_sv, double {1e12});
    test_scalar("+1e+12"_sv, double {1e12});
    test_scalar("-1e+12"_sv, double {-1e12});
    test_scalar("1e-12"_sv, double {1e-12});
    test_scalar("+1e-12"_sv, double {1e-12});
    test_scalar("-1e-12"_sv, double {-1e-12});

    test_scalar("\x03\x00\x00\x00\x00\x00\x00\x00\x00"_sv, double {0.0});
    test_scalar(
        "\x03\x00\x00\x00\x00\x00\x00\xf0\x7f"_sv,
        double {std::numeric_limits<double>::infinity()}
    );
    test_scalar(
        "\x03\x00\x00\x00\x00\x00\x00\xf0\xff"_sv,
        double {-std::numeric_limits<double>::infinity()}
    );

    REJECT("++0.0");
    REJECT("++1.0");
    REJECT("++.1");
    REJECT("1.0.0");
    REJECT("1e+10000");
    REJECT("\x03\x00\x00\x00\x00\x00\x00\x00"_sv);

    // XXX: Questionable behaviour?
    ACCEPT("+.0");
    ACCEPT("-.0");
    // XXX: Rejected on Mac OS, accepted on Linux (?!)
    //REJECT(".0");
    //REJECT(".5");
}

TEST(reader, scalar_string)
{
    test_scalar(R"(foobar)"_sv, "foobar"_sv);
    test_scalar(R"(foobar11)"_sv, "foobar11"_sv);
    test_scalar(R"("foobar")"_sv, "foobar"_sv);
    // wat? "\x0cf" parsed as a single char? no way!
    test_scalar("\x01\x0c""foobar"_sv, "foobar"_sv);

    REJECT(R"("foobar)");
    REJECT("\x01\x0c""fooba"_sv);
    REJECT("\x01\x0d""foobar"_sv); // negative length
}

TEST(reader, empty_list)
{
    auto reader = memory_reader("[]", yson::stream_type::node);

    ASSERT_EQ(yson::event_type::begin_stream, reader.next_event().type());
    ASSERT_EQ(yson::event_type::begin_list, reader.next_event().type());
    ASSERT_EQ(yson::event_type::end_list, reader.next_event().type());
    ASSERT_EQ(yson::event_type::end_stream, reader.next_event().type());

    REJECT("[");
    REJECT("]");
}

TEST(reader, empty_map)
{
    auto reader = memory_reader("{}", yson::stream_type::node);

    ASSERT_EQ(yson::event_type::begin_stream, reader.next_event().type());
    ASSERT_EQ(yson::event_type::begin_map, reader.next_event().type());
    ASSERT_EQ(yson::event_type::end_map, reader.next_event().type());
    ASSERT_EQ(yson::event_type::end_stream, reader.next_event().type());

    REJECT("{");
    REJECT("}");
}


TEST(reader, sample)
{
    auto reader = memory_reader(
        R"({"11"=11;"nothing"=#;"zero"=0.;"foo"="bar";"list"=[1;2;3]})",
        yson::stream_type::node
    );

    ASSERT_EQ(yson::event_type::begin_stream, reader.next_event().type());
    ASSERT_EQ(yson::event_type::begin_map, reader.next_event().type());

    {
        auto& e = reader.next_event();
        ASSERT_EQ(yson::event_type::key, e.type());
        ASSERT_EQ("11"_sv, e.as_string());
    }
    {
        auto& e = reader.next_event();
        ASSERT_EQ(yson::event_type::scalar, e.type());
        ASSERT_EQ(yson::scalar {int64_t {11}}, e.as_scalar());
    }

    {
        auto& e = reader.next_event();
        ASSERT_EQ(yson::event_type::key, e.type());
        ASSERT_EQ("nothing"_sv, e.as_string());
    }
    {
        auto& e = reader.next_event();
        ASSERT_EQ(yson::event_type::scalar, e.type());
        ASSERT_EQ(yson::scalar {}, e.as_scalar());
    }

    {
        auto& e = reader.next_event();
        ASSERT_EQ(yson::event_type::key, e.type());
        ASSERT_EQ("zero"_sv, e.as_string());
    }
    {
        auto& e = reader.next_event();
        ASSERT_EQ(yson::event_type::scalar, e.type());
        ASSERT_EQ(yson::scalar {0.0}, e.as_scalar());
    }

    {
        auto& e = reader.next_event();
        ASSERT_EQ(yson::event_type::key, e.type());
        ASSERT_EQ("foo"_sv, e.as_string());
    }
    {
        auto& e = reader.next_event();
        ASSERT_EQ(yson::event_type::scalar, e.type());
        ASSERT_EQ(yson::scalar {"bar"_sv}, e.as_scalar());
    }

    {
        auto& e = reader.next_event();
        ASSERT_EQ(yson::event_type::key, e.type());
        ASSERT_EQ("list"_sv, e.as_string());
    }
    ASSERT_EQ(yson::event_type::begin_list, reader.next_event().type());
    {
        auto& e = reader.next_event();
        ASSERT_EQ(yson::event_type::scalar, e.type());
        ASSERT_EQ(yson::scalar {int64_t {1}}, e.as_scalar());
    }
    {
        auto& e = reader.next_event();
        ASSERT_EQ(yson::event_type::scalar, e.type());
        ASSERT_EQ(yson::scalar {int64_t {2}}, e.as_scalar());
    }
    {
        auto& e = reader.next_event();
        ASSERT_EQ(yson::event_type::scalar, e.type());
        ASSERT_EQ(yson::scalar {int64_t {3}}, e.as_scalar());
    }
    ASSERT_EQ(yson::event_type::end_list, reader.next_event().type());

    ASSERT_EQ(yson::event_type::end_map, reader.next_event().type());
    ASSERT_EQ(yson::event_type::end_stream, reader.next_event().type());
}

TEST(reader, accept)
{
    ACCEPT("[]");
    ACCEPT("{}");
    ACCEPT("<>[]");
    ACCEPT("<>{}");
    ACCEPT("[{};{};{}]");
    ACCEPT("[{};{};{};]");
    ACCEPT("[<>{};<>{};<>{}]");
    ACCEPT("[<>{};<>{};<>{};]");

    ACCEPT("foo");
    ACCEPT("[foo]");
    ACCEPT("[foo;]");
    ACCEPT("{foo=foo}");
    ACCEPT("{foo=foo;}");
    ACCEPT("<>{foo=foo}");
    ACCEPT("{foo=<foo=foo>foo}");
    ACCEPT("{foo=<foo=foo;>foo}");
    ACCEPT("{foo=<foo=foo>[foo;foo]}");
}

TEST(reader, reject)
{
    REJECT("[");
    REJECT("{");
    REJECT("<");

    REJECT("[[}]");
    REJECT("<>{]");
    REJECT("[>]");

    REJECT("<><>[]");
    REJECT("[<>;<>]");

    REJECT("{<>foo=foo}");
    REJECT("{foo=<>}");
    REJECT("{foo}");

    REJECT("<a=b>");
    REJECT("<>");
}

TEST(reader, read_past_end)
{
    auto reader = memory_reader("#", yson::stream_type::node);
    EXPECT_EQ(yson::event_type::begin_stream, reader.next_event().type());
    EXPECT_EQ(yson::event_type::scalar, reader.next_event().type());
    EXPECT_EQ(yson::event_type::end_stream, reader.next_event().type());
    EXPECT_THROW(reader.next_event(), yson::exception::bad_input);
}

TEST(reader, stream_type)
{
    REJECT("", yson::stream_type::node);
    ACCEPT("", yson::stream_type::list_fragment);
    ACCEPT("", yson::stream_type::map_fragment);

    ACCEPT("[1]", yson::stream_type::node);
    ACCEPT("[1]", yson::stream_type::list_fragment);
    REJECT("[1]", yson::stream_type::map_fragment);

    ACCEPT("<foo=bar>[1]", yson::stream_type::node);
    ACCEPT("<foo=bar>[1]", yson::stream_type::list_fragment);
    REJECT("<foo=bar>[1]", yson::stream_type::map_fragment);

    ACCEPT("           [1]   \t \t    ", yson::stream_type::node);
    ACCEPT("           [1]   \t \t    ", yson::stream_type::list_fragment);
    REJECT("           [1]   \t \t    ", yson::stream_type::map_fragment);

    REJECT("[1];", yson::stream_type::node);
    ACCEPT("[1];", yson::stream_type::list_fragment);
    REJECT("[1];", yson::stream_type::map_fragment);

    REJECT("[1]; foobar", yson::stream_type::node);
    ACCEPT("[1]; foobar", yson::stream_type::list_fragment);
    REJECT("[1]; foobar", yson::stream_type::map_fragment);

    REJECT("a=[1]", yson::stream_type::node);
    REJECT("a=[1]", yson::stream_type::list_fragment);
    ACCEPT("a=[1]", yson::stream_type::map_fragment);

    REJECT("a=[1]; ", yson::stream_type::node);
    REJECT("a=[1]; ", yson::stream_type::list_fragment);
    ACCEPT("a=[1]; ", yson::stream_type::map_fragment);

    REJECT("a=[1]; b=foobar", yson::stream_type::node);
    REJECT("a=[1]; b=foobar", yson::stream_type::list_fragment);
    ACCEPT("a=[1]; b=foobar", yson::stream_type::map_fragment);
}
