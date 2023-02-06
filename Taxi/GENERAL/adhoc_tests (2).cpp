#include "adhoc_tests.hpp"

#include <pybind11/numpy.h>

#include <libs/zoo/utils/statistics/adhoc_tests.hpp>

namespace zoo {
namespace utils {
namespace statistics {
namespace adhoc_tests {

namespace {

decltype(&bootstrap_sum) get_eval_func(const std::string& metric) {
  if (metric == "sum") {
    return bootstrap_sum;
  } else if (metric == "median") {
    return bootstrap_median;
  } else if (metric == "variance") {
    return bootstrap_variance;
  } else if (metric == "std") {
    return bootstrap_std;
  } else if (metric == "mean") {
    return bootstrap_mean;
  }
  throw std::invalid_argument("Unknown metric: " + metric);
}

py::dict py_bootstrap_test(py::array_t<double> test,
                           py::array_t<double> control,
                           int iters_count,
                           int n_jobs = 1,
                           int random_seed = 42,
                           bool return_distribution = false,
                           const std::string& metric = "mean") {

  auto eval = get_eval_func(metric);
  py::buffer_info test_buf = test.request();
  double* test_buf_ptr = static_cast<double*>(test_buf.ptr);
  py::buffer_info control_buf = control.request();
  double* control_buf_ptr = static_cast<double*>(control_buf.ptr);
  auto test_result = bootstrap_test(eval, test_buf_ptr, test_buf.size,
                                    control_buf_ptr, control_buf.size,
                                    random_seed, iters_count, n_jobs);
  return py::dict(
      py::arg("diff") = test_result.diff,
      py::arg("pvalue") = test_result.pvalue,
      py::arg("distribution") = return_distribution ? py::array_t<double>(
          iters_count, test_result.distribution.data()
      ) : py::object(py::none())
  );
}

}

void AddToPyModule(py::module& module) {
  module.def(
      "bootstrap_test", &py_bootstrap_test,
      py::arg("test"), py::arg("control"),
      py::arg("iters_count"), py::arg("n_jobs") = 1,
      py::arg("random_seed") = 42,
      py::arg("return_distribution") = false,
      py::arg("metric") = "mean"
  );
}

} // namespace adhoc_tests
} // namespace statistics
} // namespace utils
} // namespace zoo
