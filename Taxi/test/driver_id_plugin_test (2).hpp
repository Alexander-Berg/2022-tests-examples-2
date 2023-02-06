#pragma once

#include <driver-id/test/driver_id_plugin_test.hpp>
#include <geobus/types/driver_id.hpp>

#include <geobus/generators/driver_id_generator.hpp>

#include <gtest/gtest.h>

namespace geobus::test {

/// This plugin provides functions to create high-level and low-level
/// driver id's. Uuid and dbid are always the same for same salt
struct DriverIdTestPlugin : public driver_id::test::DriverIdTestPlugin,
                            public geobus::generators::DriverIdGenerator {
  using geobus::generators::DriverIdGenerator::CreateDriverId;

  /// Calling with same argument will provide same result
  static auto CreateDbid_Uuid(const size_t salt) {
    const auto result =
        geobus::generators::DriverIdGenerator::CreateDriverId(salt);
    EXPECT_TRUE(result.IsValid());
    return result;
  }
  /// Calling with same argument will provide same result
  static auto CreateInvalidDbid_Uuid(const size_t) {
    const auto result = ::geobus::types::DriverId{""};
    EXPECT_FALSE(result.IsValid());
    return result;
  }
};

}  // namespace geobus::test
