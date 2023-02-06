#include "loveka/common/models/connector.hpp"

#include <gtest/gtest.h>

using namespace loveka::common::models;

class test_observer : public observer<uint8_t, 2> {
private:
    int i = 0;

public:
    void
    data(observable<uint8_t, 2>& src, std::array<uint8_t, 2>& nd)
    {
        i = 1;
    }

    void
    state_change(observable<uint8_t, 2>& src, state& state_new)
    {
        i = 2;
    }

    void
    disconnect(observable<uint8_t, 2>& src)
    {
        i = 3;
    }

    int
    get()
    {
        return i;
    }
};

class test_observer2 : public observer<uint8_t, 3> {
private:
    int i = 0;

public:
    void
    data(observable<uint8_t, 3>& src, std::array<uint8_t, 3> nd)
    {
        i = 1;
    }

    void
    state_change(observable<uint8_t, 3>& src, state state_new)
    {
        i = 2;
    }

    void
    disconnect(observable<uint8_t, 3>& src)
    {
        i = 3;
    }

    int
    get()
    {
        return i;
    }
};

class test_observer_multi : public observer<uint8_t, 2>, public observer<uint8_t, 3> {
private:
    int i = 0;

public:
    void
    data(observable<uint8_t, 2>& src, std::array<uint8_t, 2>& nd)
    {
        i = 1;
    }

    void
    state_change(observable<uint8_t, 2>& src, state& state_new)
    {
        i = 2;
    }

    void
    disconnect(observable<uint8_t, 2>& src)
    {
        i = 3;
    }

    void
    data(observable<uint8_t, 3>& src, std::array<uint8_t, 3>& nd)
    {
        i = 6;
    }

    void
    state_change(observable<uint8_t, 3>& src, state& state_new)
    {
        i = 6;
    }

    void
    disconnect(observable<uint8_t, 3>& src)
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
    test_observer          obs1;
    observable<uint8_t, 2> res1;
    res1.add_observer(obs1);

    std::array<uint8_t, 2> nd = {0, 0};
    res1.notify_observers(nd);
    EXPECT_EQ(obs1.get(), 1);

    state ns = {state::ok};
    res1.notify_observers(ns);
    EXPECT_EQ(obs1.get(), 2);

    notification_disconnect ndis = {};
    res1.notify_observers(ndis);
    EXPECT_EQ(obs1.get(), 3);
}

TEST(connector_test, basic_add_observe)
{
    test_observer          obs1;
    observable<uint8_t, 2> res1;
    res1.add_observer(obs1);

    std::array<uint8_t, 2> nd = {0, 0};
    res1.notify_observers(nd);
    EXPECT_EQ(obs1.get(), 1);

    state ns = {state::ok};
    res1.notify_observers(ns);
    EXPECT_EQ(obs1.get(), 2);

    notification_disconnect ndis = {};
    res1.notify_observers(ndis);
    EXPECT_EQ(obs1.get(), 3);
}

TEST(connector_test, basic_add_observe_multi)
{
    test_observer          obs1;
    test_observer          obs2;
    test_observer          obs3;
    test_observer          obs4;
    observable<uint8_t, 2> res1;
    res1.add_observer(obs1);
    res1.add_observer(obs2);
    res1.add_observer(obs3);
    res1.add_observer(obs4);

    std::array<uint8_t, 2> nd = {0, 0};
    res1.notify_observers(nd);
    EXPECT_EQ(obs1.get(), 1);
    EXPECT_EQ(obs2.get(), 1);
    EXPECT_EQ(obs3.get(), 1);
    EXPECT_EQ(obs4.get(), 1);

    state ns = {state::ok};
    res1.notify_observers(ns);
    EXPECT_EQ(obs1.get(), 2);
    EXPECT_EQ(obs2.get(), 2);
    EXPECT_EQ(obs3.get(), 2);
    EXPECT_EQ(obs4.get(), 2);

    notification_disconnect ndis = {};
    res1.notify_observers(ndis);
    EXPECT_EQ(obs1.get(), 3);
    EXPECT_EQ(obs2.get(), 3);
    EXPECT_EQ(obs3.get(), 3);
    EXPECT_EQ(obs4.get(), 3);
}

TEST(connector_test, basic_add_observe_multi_diff)
{
    test_observer          obs1;
    test_observer          obs2;
    test_observer          obs3;
    test_observer_multi    obs4;
    observable<uint8_t, 2> res1;
    observable<uint8_t, 3> res2;
    res1.add_observer(obs1);
    res1.add_observer(obs2);
    res1.add_observer(obs3);
    res1.add_observer(obs4);
    res2.add_observer(obs4);

    std::array<uint8_t, 2> nd  = {0, 0};
    std::array<uint8_t, 3> nd2 = {0, 0};
    res1.remove_observer(obs4);
    res1.notify_observers(nd);
    res2.notify_observers(nd2);
    EXPECT_EQ(obs1.get(), 1);
    EXPECT_EQ(obs2.get(), 1);
    EXPECT_EQ(obs3.get(), 1);
    EXPECT_EQ(obs4.get(), 6);

    state ns = {state::ok};
    res1.remove_observer(obs3);
    res1.notify_observers(ns);
    res2.notify_observers(nd2);
    EXPECT_EQ(obs1.get(), 2);
    EXPECT_EQ(obs2.get(), 2);
    EXPECT_EQ(obs3.get(), 1);
    EXPECT_EQ(obs4.get(), 6);

    notification_disconnect ndis = {};
    res1.remove_observer(obs2);
    res1.notify_observers(ndis);
    res2.notify_observers(nd2);
    EXPECT_EQ(obs1.get(), 3);
    EXPECT_EQ(obs2.get(), 2);
    EXPECT_EQ(obs3.get(), 1);
    EXPECT_EQ(obs4.get(), 6);
}
