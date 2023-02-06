#include "adhoc_tests.hpp"

#include <cmath>

#include <pybind11/numpy.h>

namespace projects {
namespace common {
namespace statistics {

double BootstrapSum(const double* const values, const size_t size,
                    std::mt19937* const engine) {
  std::uniform_int_distribution<size_t> rand_index(0, size - 1);
  double sum = 0;
  for (size_t num = 0; num < size; ++num) {
    const size_t index = engine ? rand_index(*engine) : num;
    sum += values[index];
  }
  return sum;
}

double BootstrapMean(const double* const values, const size_t size,
                     std::mt19937* const engine) {
  return BootstrapSum(values, size, engine) / size;
}

double BootstrapVariance(const double* const values, const size_t size,
                         std::mt19937* const engine) {
  std::uniform_int_distribution<size_t> rand_index(0, size - 1);
  double sum = 0;
  double sq_sum = 0;
  for (size_t num = 0; num < size; ++num) {
    const size_t index = engine ? rand_index(*engine) : num;
    const double value = values[index];
    sum += value;
    sq_sum += value * value;
  }
  const double mean = sum / size;
  return sq_sum / size - mean * mean;
}

double BootstrapStd(const double* const values, const size_t size,
                    std::mt19937* const engine) {
  return std::sqrt(BootstrapVariance(values, size, engine));
}

double BootstrapMedian(const double* const values, const size_t size,
                       std::mt19937* const engine) {
  return BootstrapPercentile<1u, 2u>(values, size, engine);
}

namespace {

decltype(&BootstrapSum) get_eval_func(const std::string& metric) {
  if (metric == "sum") {
    return BootstrapSum;
  } else if (metric == "median") {
    return BootstrapMedian;
  } else if (metric == "variance") {
    return BootstrapVariance;
  } else if (metric == "std") {
    return BootstrapStd;
  } else if (metric == "mean") {
    return BootstrapMean;
  }
  throw std::invalid_argument("Unknown metric: " + metric);
}

py::dict py_bootstrap_test(py::array_t<double> test,
                           py::array_t<double> control, int iters_count,
                           int n_jobs = 1, int random_seed = 42,
                           bool return_distribution = false,
                           const std::string& metric = "mean") {
  auto eval = get_eval_func(metric);
  py::buffer_info test_buf = test.request();
  double* test_buf_ptr = static_cast<double*>(test_buf.ptr);
  py::buffer_info control_buf = control.request();
  double* control_buf_ptr = static_cast<double*>(control_buf.ptr);
  auto test_result =
      DoBootstrapTest(eval, test_buf_ptr, test_buf.size, control_buf_ptr,
                      control_buf.size, random_seed, iters_count, n_jobs);
  return py::dict(py::arg("diff") = test_result.diff,
                  py::arg("pvalue") = test_result.pvalue,
                  py::arg("distribution") =
                      return_distribution
                          ? py::array_t<double>(iters_count,
                                                test_result.distribution.data())
                          : py::object(py::none()));
}

}  // namespace

void AddAdhocTestsToPyModule(py::module& module) {
  module.def("bootstrap_test", &py_bootstrap_test, py::arg("test"),
             py::arg("control"), py::arg("iters_count"), py::arg("n_jobs") = 1,
             py::arg("random_seed") = 42,
             py::arg("return_distribution") = false,
             py::arg("metric") = "mean");
}

}  // namespace statistics
}  // namespace common
}  // namespace projects
