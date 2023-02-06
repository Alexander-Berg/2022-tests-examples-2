#pragma once

#include <pybind11/pybind11.h>

namespace zoo {
namespace utils {
namespace statistics {
namespace adhoc_tests {

namespace py = pybind11;

void AddToPyModule(py::module& module);

} // namespace adhoc_tests
} // namespace statistics
} // namespace utils
} // namespace zoo
