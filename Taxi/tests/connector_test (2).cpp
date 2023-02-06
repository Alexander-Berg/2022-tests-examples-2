#include "loveka/components/utils/observer.hpp"

#include <gtest/gtest.h>

using namespace loveka::components::utils;

class test_observer : public observer<uint8_t> {
private:
    int i = 0;

public:
    void
    data(observable<uint8_t>& src, uint8_t& nd)
    {
        i = 1;
    }

    int
    get()
    {
        return i;
    }
};

class test_observer2 : public observer<uint8_t> {
private:
    int i = 0;

public:
    void
    data(observable<uint8_t>& src, uint8_t& nd)
    {
        i = 1;
    }

    int
    get()
    {
        return i;
    }
};

class test_observer_multi : public observer<uint8_t>, public observer<uint16_t> {
private:
    int i = 0;

public:
    void
    data(observable<uint8_t>& src, uint8_t& nd)
    {
        i = 1;
    }

    void
    data(observable<uint16_t>& src, uint16_t& nd)
    {
        i = 6;
    }

    int
    get()
    {
        return i;
    }
};

TEST(connector_test, basic_two_observe)
{
    test_observer       obs1;
    observable<uint8_t> res1;
    res1.add_observer(obs1);

    uint8_t nd = {0};
    res1.notify_observers(nd);
    EXPECT_EQ(obs1.get(), 1);
}

TEST(connector_test, basic_add_observe)
{
    test_observer       obs1;
    observable<uint8_t> res1;
    res1.add_observer(obs1);

    uint8_t nd = {0};
    res1.notify_observers(nd);
    EXPECT_EQ(obs1.get(), 1);
}

TEST(connector_test, basic_add_observe_multi)
{
    test_observer       obs1;
    test_observer       obs2;
    test_observer       obs3;
    test_observer       obs4;
    observable<uint8_t> res1;
    res1.add_observer(obs1);
    res1.add_observer(obs2);
    res1.add_observer(obs3);
    res1.add_observer(obs4);

    uint8_t nd = {0};
    res1.notify_observers(nd);
    EXPECT_EQ(obs1.get(), 1);
    EXPECT_EQ(obs2.get(), 1);
    EXPECT_EQ(obs3.get(), 1);
    EXPECT_EQ(obs4.get(), 1);
}

TEST(connector_test, basic_add_observe_multi_diff)
{
    test_observer        obs1;
    test_observer        obs2;
    test_observer        obs3;
    test_observer_multi  obs4;
    observable<uint8_t>  res1;
    observable<uint16_t> res2;
    res1.add_observer(obs1);
    res1.add_observer(obs2);
    res1.add_observer(obs3);
    res1.add_observer(obs4);
    res2.add_observer(obs4);

    uint8_t  nd  = {0};
    uint16_t nd2 = {0};
    res1.remove_observer(obs4);
    res1.notify_observers(nd);
    res2.notify_observers(nd2);
    EXPECT_EQ(obs1.get(), 1);
    EXPECT_EQ(obs2.get(), 1);
    EXPECT_EQ(obs3.get(), 1);
    EXPECT_EQ(obs4.get(), 6);
}
