#pragma once

#include <gtest/gtest.h>

#include <gpssignal/test/print_to.hpp>

#include <geobus/types/driver_id.hpp>
#include <geobus/types/driver_position.hpp>
#include <geobus/types/gps_signal_extended.hpp>

namespace geobus::types {

inline void PrintTo(const DriverId& driver_id, std::ostream* os) {
  *os << "[dbid, uuid]: " << driver_id.GetDbid() << "," << driver_id.GetUuid();
}

inline void PrintTo(PositionSource source, std::ostream* os) {
  switch (source) {
    case PositionSource::Gps:
      *os << "GPS";
      break;
    case PositionSource::Navigator:
      *os << "Navi";
      break;
    case PositionSource::Adjuster:
      *os << "Adj";
      break;
    case PositionSource::Other:
      *os << "Other";
      break;
    default:
      *os << "Unkn";
      break;
  }
}
inline void PrintTo(const GpsSignalExtended& signal, std::ostream* os) {
  PrintTo(static_cast<const ::gpssignal::GpsSignal&>(signal), os);
  *os << " src: ";
  PrintTo(signal.source, os);
}

inline void PrintTo(const DriverPosition& driver_position, std::ostream* os) {
  ::geobus::types::PrintTo(driver_position.driver_id, os);
  *os << " ";
  PrintTo(driver_position.signal, os);
}
}  // namespace geobus::types
