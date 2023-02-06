#include "loveka/common/models/circular_buffer.hpp"

#include <gtest/gtest.h>

#include <cstring>

TEST(circullar_test, basic_push_pull)
{
    using namespace loveka::common::models;
    circular_buffer<uint8_t, 8> buffer;
    EXPECT_EQ(buffer.capacity(), 8);

    std::size_t sz;
    buffer.push_array_back(reinterpret_cast<const uint8_t*>("12345"), 5);
    sz = buffer.size();
    EXPECT_EQ(sz, 5);
    char ch = '1';
    for (int j = 0; j < sz; j++) {
        EXPECT_EQ(buffer.begin().operator*(), ch++);
        buffer.pop_front();
    }
    EXPECT_EQ(buffer.size(), 0);
}

TEST(circullar_test, basic_push_pull_mass)
{
    using namespace loveka::common::models;
    circular_buffer<uint8_t, 8> buffer;
    EXPECT_EQ(buffer.capacity(), 8);

    std::size_t sz;
    buffer.push_array_back(reinterpret_cast<const uint8_t*>("12345"), 5);
    sz = buffer.end() - buffer.begin();
    EXPECT_EQ(sz, 5);
    char ch = '1';
    for (auto& item : buffer) {
        EXPECT_EQ(item, ch++);
    }
    buffer.pop_front_count(sz);
    EXPECT_EQ(buffer.size(), 0);
}

TEST(circullar_test, basic_push_pull_overburn)
{
    using namespace loveka::common::models;
    circular_buffer<uint8_t, 10> buffer;
    EXPECT_EQ(buffer.capacity(), 10);

    std::size_t sz;
    buffer.push_array_back(reinterpret_cast<const uint8_t*>("abcdefgh"), 8);
    buffer.push_array_back(reinterpret_cast<const uint8_t*>("ijklmnop"), 8);
    sz = buffer.size();
    EXPECT_EQ(sz, 10);
    char ch = 'g';
    for (int j = 0; j < sz; j++) {
        EXPECT_EQ(buffer.begin().operator*(), ch++);
        buffer.pop_front();
    }
    EXPECT_EQ(buffer.size(), 0);
}

TEST(circullar_test, basic_push_pull_array)
{
    using namespace loveka::common::models;
    circular_buffer<uint8_t, 10> buffer;
    EXPECT_EQ(buffer.capacity(), 10);

    std::size_t sz;
    std::string msg1{"abcdefgh"};
    std::string msg2{"ijklmnop"};
    buffer.push_array_back(reinterpret_cast<const uint8_t*>(msg1.begin().base()), 8);
    buffer.push_array_back(reinterpret_cast<const uint8_t*>(msg2.begin().base()), 8);
    sz = buffer.end() - buffer.begin();
    EXPECT_EQ(sz, 10);
    char ch   = 'g';
    auto ret1 = buffer.pop_front_array<4>();
    for (auto& item : ret1) {
        EXPECT_EQ(item, ch++);
    }
    sz = buffer.end() - buffer.begin();
    EXPECT_EQ(sz, 6);
    ch        = 'k';
    auto ret2 = buffer.pop_front_array<6>();
    for (auto& item : ret2) {
        EXPECT_EQ(item, ch++);
    }
    EXPECT_EQ(buffer.size(), 0);
}

TEST(circullar_test, basic_push_pull_mass_overburn)
{
    using namespace loveka::common::models;
    circular_buffer<uint8_t, 10> buffer;
    EXPECT_EQ(buffer.capacity(), 10);

    std::size_t sz;
    buffer.push_array_back(reinterpret_cast<const uint8_t*>("abcdefgh"), 8);
    buffer.push_array_back(reinterpret_cast<const uint8_t*>("ijklmnop"), 8);
    sz = buffer.end() - buffer.begin();
    EXPECT_EQ(sz, 10);
    char ch = 'g';
    for (auto& item : buffer) {
        EXPECT_EQ(item, ch++);
    }
    buffer.pop_front_count(sz);
    EXPECT_EQ(buffer.size(), 0);
}

TEST(circullar_test, basic_update_head)
{
    using namespace loveka::common::models;
    circular_buffer<uint8_t, 10> buffer;
    EXPECT_EQ(buffer.capacity(), 10);
    memcpy(buffer.storage(), reinterpret_cast<const void*>("abcdefghij"), 10);

    std::size_t sz;
    buffer.update_head(4);
    sz = buffer.end() - buffer.begin();
    EXPECT_EQ(sz, 4);
    char ch = 'a';
    for (int j = 0; j < sz; j++) {
        EXPECT_EQ(buffer.begin().operator*(), ch++);
        buffer.pop_front();
    }
    EXPECT_EQ(buffer.size(), 0);
    buffer.update_head(8);
    sz = buffer.end() - buffer.begin();
    EXPECT_EQ(sz, 4);
    ch = 'e';
    for (int j = 0; j < sz; j++) {
        EXPECT_EQ(buffer.begin().operator*(), ch++);
        buffer.pop_front();
    }
    EXPECT_EQ(buffer.size(), 0);
}

TEST(circullar_test, basic_update_head_overburn)
{
    using namespace loveka::common::models;
    circular_buffer<uint8_t, 10> buffer;
    EXPECT_EQ(buffer.capacity(), 10);
    memcpy(buffer.storage(), reinterpret_cast<const uint8_t*>("abcdefghij"), 10);

    std::size_t sz;
    buffer.update_head(8);
    sz = buffer.end() - buffer.begin();
    EXPECT_EQ(sz, 8);
    char ch = 'a';
    for (auto& item : buffer) {
        EXPECT_EQ(item, ch++);
    }
    buffer.pop_front_count(sz);
    EXPECT_EQ(buffer.size(), 0);
}

TEST(circullar_test, basic_time_measure_push)
{
    using namespace loveka::common::models;
    circular_buffer<uint8_t, 1024> buffer;
    EXPECT_EQ(buffer.capacity(), 1024);

    for (std::size_t i = 0; i < 10000000; i++) {
        buffer.push_array_back(reinterpret_cast<const uint8_t*>("ijklmnop"), 8);
    }
}

TEST(circullar_test, basic_time_measure_push_pop)
{
    using namespace loveka::common::models;
    circular_buffer<uint8_t, 1024> buffer;
    EXPECT_EQ(buffer.capacity(), 1024);

    for (std::size_t i = 0; i < 10000000; i++) {
        buffer.push_array_back(reinterpret_cast<const uint8_t*>("ijklmnop"), 8);
        buffer.pop_front_count(3);
    }
}
