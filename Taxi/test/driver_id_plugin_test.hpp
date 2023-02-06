#pragma once

#include <fmt/format.h>
#include <gtest/gtest.h>

#include <driver-id/driver_id.hpp>
#include <driver-id/generators/driver_id_generator.hpp>

namespace driver_id::test {

/// This plugin provides functions to create high-level and low-level
/// driver id's. Uuid and dbid are always the same for same salt
struct DriverIdTestPlugin : public generators::DriverIdGenerator {
  using DriverIdGenerator::CreateDriverId;

  void PluginSetUp() {}
  void PluginTearDown() {}
  static void PluginSetUpTestSuite() {}
  static void PluginTearDownTestSuite() {}
};

}  // namespace driver_id::test
