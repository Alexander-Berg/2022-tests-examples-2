#pragma once
#include <userver/cache/cache_config.hpp>
#include <userver/dynamic_config/snapshot.hpp>
#include <userver/formats/bson.hpp>
#include <userver/formats/json.hpp>
#include <userver/fs/blocking/read.hpp>
#include <userver/utest/utest.hpp>

#include <optional>

namespace routehistory::test {

template <typename T>
struct IOWrap {
  IOWrap(const T& ref) : ref(ref) {}
  bool operator==(const IOWrap& rhs) const { return ref == rhs.ref; }
  bool operator!=(const IOWrap& rhs) const { return ref != rhs.ref; }
  const T& ref;
};

template <typename T>
std::ostream& operator<<(std::ostream& s, const IOWrap<T>& self) {
  return s << self.ref;
}

inline std::ostream& operator<<(
    std::ostream& s,
    const IOWrap<std::chrono::system_clock::time_point>& self) {
  return s << ::utils::datetime::Timestring(self.ref);
}

template <typename T>
std::ostream& operator<<(std::ostream& s,
                         const IOWrap<std::optional<T>>& self) {
  if (self.ref) {
    return s << IOWrap(*self.ref);
  }
  return s << "std::nullopt";
}

}  // namespace routehistory::test
