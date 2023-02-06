#include "../tools/com/com_port.hpp"

#include <gtest/gtest.h>

using namespace common::tools::debugger;

TEST(com_port_test_win, basic_list)
{
    auto list = com_port::ports();
    EXPECT_FALSE(list.size() == 0);
}

TEST(com_port_test_win, basic_connect)
{
    auto list = com_port::ports();
    EXPECT_TRUE(list.size() > 1);
    com_port               com(list[1]);
    std::array<uint8_t, 5> data{0x01, 0x01, 0x01, 0x01, 0x01};
    com.write(data.data(), 5);
    com_port::delay(1000);
}

TEST(com_port_test_win, message)
{
    auto list = com_port::ports();
    EXPECT_TRUE(list.size() > 1);
    com_port com(list[1]);

    com.send_packet({'P', 'W'}, pwm_frame{1, 2, 3, 4});
    while (!com.size())
        ;
    EXPECT_TRUE(com.size() > 0);
}