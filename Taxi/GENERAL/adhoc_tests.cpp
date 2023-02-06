#include "adhoc_tests.hpp"

#include <cmath>

namespace zoo {
namespace utils {
namespace statistics {
namespace adhoc_tests {

double bootstrap_sum(const double* const values,
                     const size_t size, std::mt19937* const engine) {
  std::uniform_int_distribution<size_t> rand_index(0, size - 1);
  double sum = 0;
  for (size_t num = 0; num < size; ++num) {
    const size_t index = engine ? rand_index(*engine) : num;
    sum += values[index];
  }
  return sum;
}

double bootstrap_mean(const double* const values,
                      const size_t size, std::mt19937* const engine) {
  return bootstrap_sum(values, size, engine) / size;
}

double bootstrap_variance(const double* const values,
                          const size_t size, std::mt19937* const engine) {
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

double bootstrap_std(const double* const values,
                     const size_t size, std::mt19937* const engine) {
  return std::sqrt(bootstrap_variance(values, size, engine));
}

double bootstrap_median(const double* const values,
                        const size_t size, std::mt19937* const engine) {
  return bootstrap_percentile<1u, 2u>(values, size, engine);
}

} // adhoc_tests namespace
} // statistics namespace
} // utils namespace
} // zoo namespace
