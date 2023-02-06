#pragma once

#include <core/context/geobase_wrapper.hpp>
#include <geobase/models/geobase.hpp>

namespace routestats::test {

class GeobaseWrapperMock : public routestats::full::GeobaseWrapper {
 public:
  GeobaseWrapperMock() : GeobaseWrapper() {}

  std::string GetTimezoneByPosition([
      [maybe_unused]] const geometry::Position pos) const override {
    return "Europe/Moscow";
  }

  cctz::civil_second GetNowInTimeZone([
      [maybe_unused]] const geometry::Position pos) const override {
    return cctz::civil_second(2022, 6, 27, 12, 0, 0);
  }
};

}  // namespace routestats::test
