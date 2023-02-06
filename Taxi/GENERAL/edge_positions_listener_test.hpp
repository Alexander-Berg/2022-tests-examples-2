#pragma once

#include <channels/edge_positions/lowlevel_edge_positions_generator.hpp>
#include <geobus/channels/edge_positions/listener.hpp>
#include <geobus/channels/edge_positions/plugin_test.hpp>
#include <geobus/test/listener_tester_test.hpp>

#include <userver/utest/utest.hpp>

namespace geobus::clients {

using EdgePositionsListenerTester =
    ::geobus::test::GeobusListenerTester<EdgePositionsListener>;

class EdgePositionsListenerFixture
    : public testing::Test,
      public generators::LowlevelEdgePositionsGenerator,
      public test::EdgePositionsTestPlugin {};

class EdgePositionsChannelFixture
    : public testing::Test,
      public generators::LowlevelEdgePositionsGenerator,
      public test::EdgePositionsTestPlugin {};

}  // namespace geobus::clients
