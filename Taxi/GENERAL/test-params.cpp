#include <agl/core/executer_state.hpp>
#include <models/test-params.hpp>

#include <fmt/format.h>

namespace api_proxy::models {

const agl::core::Variant& TestParameters::Get(const std::string& name) const {
  const auto it = store_.find(name);
  if (it == store_.cend() || !it->second) {
    throw std::runtime_error(
        fmt::format("test parameter is not defined: {}", name));
  }
  return *it->second;
}

TestParametersFactory::TestParametersFactory(
    const std::vector<Parameter>& parameters)
    : parameters_(parameters),
      number_of_combos_(EstimateNumberOfCombinations(parameters)) {}

TestParameters TestParametersFactory::MakeParameters(size_t combo_id) const {
  ThrowIfOverflow(combo_id);
  TestParameters::NonOwningStore store;

  for (const auto& param : parameters_) {
    const size_t value_id = combo_id % param.values.size();
    combo_id /= param.values.size();
    store.emplace(param.name, &param.values[value_id]);
  }

  return TestParameters(std::move(store));
}

std::string TestParametersFactory::SubtestName(size_t combo_id) const {
  ThrowIfOverflow(combo_id);

  std::vector<std::string> parts;
  for (const auto& param : parameters_) {
    const size_t value_id = combo_id % param.values.size();
    combo_id /= param.values.size();

    parts.push_back(fmt::format("{}{}", param.name, value_id));
  }

  return fmt::format("[{}]", fmt::join(parts, "-"));
}

void TestParametersFactory::ThrowIfOverflow(size_t combo_id) const {
  if (combo_id >= number_of_combos_) {
    throw std::runtime_error(
        fmt::format("test parameter combination id {} exceeds total number "
                    "of combinations ({})",
                    combo_id, number_of_combos_));
  }
}

size_t TestParametersFactory::EstimateNumberOfCombinations(
    const std::vector<Parameter>& parameters) {
  size_t n_combos = 1;
  bool overflow = false;
  for (const auto& values : parameters) {
    if (values.values.size() >= kCombinationsLimit) {
      overflow = true;
      break;
    }
    n_combos *= values.values.size();
    if (n_combos >= kCombinationsLimit) {
      overflow = true;
      break;
    }
  }

  if (overflow) {
    throw std::runtime_error(
        fmt::format("number of parameter combinations exceeds limit {}",
                    kCombinationsLimit));
  }
  return n_combos;
}

}  // namespace api_proxy::models
