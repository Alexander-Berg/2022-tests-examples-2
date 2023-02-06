#pragma once

#include <channels/positions/lowlevel.hpp>
#include <geobus/channels/positions/listener.hpp>
#include <geobus/test/listener_tester_test.hpp>

#include <userver/utest/utest.hpp>

#include <geobus/channels/positions/plugin_test.hpp>

namespace geobus::clients {

using PositionsListenerTester =
    ::geobus::test::GeobusListenerTester<PositionsListener>;

class PositionsListenerFixture : public testing::Test,
                                 public ::geobus::test::PositionsTestPlugin {};

}  // namespace geobus::clients
