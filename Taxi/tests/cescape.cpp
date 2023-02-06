#include <gtest/gtest.h>

#include "detail/cescape.hpp"
#include "detail/print.hpp"

using namespace yson::detail;

namespace {

void test_roundtrip(const std::string& str)
{
    auto tmp = cescape::encode(str);
    auto dest = cescape::decode(tmp);
    //println("A[", str.size(), "]: ", str);
    //println("B[", tmp.size(), "]: ", tmp);
    //println("C[", dest.size(), "]: ", dest);
    EXPECT_EQ(str, dest)
        << "A[" << str.size() << "]: " << str << '\n'
        << "B[" << tmp.size() << "]: " << tmp << '\n'
        << "C[" << dest.size() << "]: " << dest;
}

template<size_t N>
void test_exhaustive(std::string& str)
{
    for (int i = 0; i < 256; ++i) {
        str[str.size() - N] = static_cast<char>(i);
        test_exhaustive<N-1>(str);
    }
}

template<>
void test_exhaustive<0>(std::string& str)
{
    test_roundtrip(str);
}

template<size_t N>
void test_exhaustive()
{
    std::string str (N, ' ');
    //println("str: ", str.size(), " ", str);
    test_exhaustive<N>(str);
}


} // anonymous namespace


TEST(cescape, exhaustive_one_char)
{
    test_exhaustive<1>();
}

TEST(cescape, exhaustive_two_chars)
{
    test_exhaustive<2>();
}

TEST(cescape, exhaustive_three_chars)
{
    test_exhaustive<3>();
}

TEST(cescape, special_escape_encode)
{
    //EXPECT_EQ(R"(\b)", cescape::encode("\b"));
    //EXPECT_EQ(R"(\f)", cescape::encode("\f"));
    EXPECT_EQ(R"(\n)", cescape::encode("\n"));
    EXPECT_EQ(R"(\r)", cescape::encode("\r"));
    EXPECT_EQ(R"(\t)", cescape::encode("\t"));
}

TEST(cescape, special_escape_decode)
{
    EXPECT_EQ("\b", cescape::decode(R"(\b)"));
    EXPECT_EQ("\f", cescape::decode(R"(\f)"));
    EXPECT_EQ("\n", cescape::decode(R"(\n)"));
    EXPECT_EQ("\r", cescape::decode(R"(\r)"));
    EXPECT_EQ("\t", cescape::decode(R"(\t)"));
}
