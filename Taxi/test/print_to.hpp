#pragma once

#include <driver-id/types.hpp>

namespace driver_id {

inline void PrintTo(const DriverDbidView& value, std::ostream* os) {
  *os << value.GetUnderlying();
}

inline void PrintTo(const DriverUuidView& value, std::ostream* os) {
  *os << value.GetUnderlying();
}

inline void PrintTo(const DriverDbid& value, std::ostream* os) {
  *os << value.GetUnderlying();
}

inline void PrintTo(const DriverUuid& value, std::ostream* os) {
  *os << value.GetUnderlying();
}

inline void PrintTo(const DriverDbidUndscrUuid& value, std::ostream* os) {
  *os << value.GetDbidUndscrUuid();
}

inline void PrintTo(const DriverIdView& driver_id, std::ostream* os) {
  *os << "[dbid, uuid]: " << driver_id.dbid.GetUnderlying() << ","
      << driver_id.uuid.GetUnderlying();
}

}  // namespace driver_id
