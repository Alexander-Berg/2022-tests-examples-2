#include <gtest/gtest.h>

#include <geobus/generators/driver_id_generator.hpp>

using geobus::generators::DriverIdGenerator;

TEST(DriverIdGenerator, Packable) {
  DriverIdGenerator::CreatePackableDriverId(5);
  DriverIdGenerator::CreatePackableDriverId(105);
  DriverIdGenerator::CreatePackableDriverId(1000000);
}

TEST(DriverIdGenerator, Unpackable) {
  DriverIdGenerator::CreateUnpackableDriverId(5);
  DriverIdGenerator::CreateUnpackableDriverId(105);
  DriverIdGenerator::CreateUnpackableDriverId(1000000);
}
