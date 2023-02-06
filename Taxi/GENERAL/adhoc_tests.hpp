#pragma once

#include <random>
#include <vector>
#include <future>
#include <algorithm>
#include <string>

namespace zoo {
namespace utils {
namespace statistics {
namespace adhoc_tests {

template<typename EvalSampleFunction>
std::vector<double> bootstrap_values(
    const EvalSampleFunction& eval,
    const double* const test, size_t test_size,
    const double* const control, size_t control_size,
    int seed, int iters_count
) {
  std::mt19937 engine(seed);
  std::vector<double> result;
  result.reserve(iters_count);
  for (int iter = 0; iter < iters_count; ++iter) {
    auto test_value = eval(test, test_size, &engine);
    auto control_value = eval(control, control_size, &engine);
    result.push_back(test_value - control_value);
  }
  return result;
}

struct BootstrapTestResult {
  double diff = 0;
  double pvalue = 1;
  std::vector<double> distribution;
};

template<typename EvalSampleFunction>
BootstrapTestResult bootstrap_test(
    const EvalSampleFunction& eval,
    const double* const test, size_t test_size,
    const double* const control, size_t control_size,
    int seed, int iters_count, int n_jobs
) {
  BootstrapTestResult result;
  if (n_jobs == 1) {
    result.distribution = bootstrap_values(eval,
                                           test,
                                           test_size,
                                           control,
                                           control_size,
                                           seed,
                                           iters_count);
  } else {
    result.distribution.reserve(iters_count);
    std::vector<std::future<std::vector<double>>> distributions;
    const int task_size = (iters_count + n_jobs - 1) / n_jobs;
    for (int iter_start = 0; iter_start < iters_count;
         iter_start += task_size) {
      int batch_size = std::min(iters_count,
                                iter_start + task_size) - iter_start;
      distributions.emplace_back(std::async(
          std::launch::async,
          bootstrap_values<EvalSampleFunction>,
          std::cref(eval),
          test, test_size,
          control, control_size,
          seed + iter_start, batch_size
      ));
    }
    for (auto& async_batch : distributions) {
      const auto batch = async_batch.get();
      result.distribution.insert(
          result.distribution.end(), batch.begin(), batch.end()
      );
    }
  }
  result.diff = eval(test, test_size, nullptr)
      - eval(control, control_size, nullptr);
  double pvalue = 0;
  for (const auto& value : result.distribution) {
    pvalue += (value < 0) + 0.5 * (value == 0);
  }
  pvalue /= iters_count;
  result.pvalue = std::min(pvalue, 1 - pvalue) * 2;
  return result;
}

template<size_t numerator, size_t denominator>
double bootstrap_percentile(const double* const values,
                            const size_t size, std::mt19937* const engine) {
  std::vector<double> sampled_values;
  sampled_values.reserve(size);
  std::uniform_int_distribution<size_t> rand_index(0, size - 1);
  for (size_t num = 0; num < size; ++num) {
    const size_t index = engine ? rand_index(*engine) : num;
    sampled_values.push_back(values[index]);
  }
  const size_t result_index = size * numerator / denominator;
  std::nth_element(sampled_values.begin(),
                   sampled_values.begin() + result_index, sampled_values.end());
  return sampled_values[result_index];
}

double bootstrap_mean(const double* const values,
                      const size_t size, std::mt19937* const engine = nullptr);

double bootstrap_sum(const double* const values,
                     const size_t size, std::mt19937* const engine = nullptr);

double bootstrap_variance(const double* const values,
                          const size_t size,
                          std::mt19937* const engine = nullptr);

double bootstrap_std(const double* const values,
                     const size_t size, std::mt19937* const engine = nullptr);

double bootstrap_median(const double* const values,
                        const size_t size,
                        std::mt19937* const engine = nullptr);

} // adhoc_tests namespace
} // statistics namespace
} // utils namespace
} // zoo namespace
