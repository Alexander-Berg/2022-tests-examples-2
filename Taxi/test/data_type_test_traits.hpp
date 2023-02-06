#pragma once

namespace geobus::test {
// Undefined, must provide specialization for every type.
// Test traits must inherit DataTypeTraits
template <typename T>
struct DataTypeTestTraits;

}  // namespace geobus::test
