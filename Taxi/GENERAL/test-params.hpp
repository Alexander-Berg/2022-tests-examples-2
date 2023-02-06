#pragma once

#include <agl/core/variant.hpp>
#include <core/config.hpp>

#include <unordered_map>

namespace api_proxy::models {

class TestParameters {
 public:
  using NonOwningStore =
      std::unordered_map<std::string, const agl::core::Variant*>;

 public:
  explicit TestParameters(NonOwningStore&& store) : store_(std::move(store)) {}
  const agl::core::Variant& Get(const std::string& name) const;

 private:
  const NonOwningStore store_;
};

class TestParametersFactory {
 public:
  using Parameter = api_proxy::core::ParsedTest::Parameter;
  static constexpr size_t kCombinationsLimit = 1 << 16;

 public:
  explicit TestParametersFactory(const std::vector<Parameter>& parameters);

  size_t NumberOfCombinations() const { return number_of_combos_; }
  std::string SubtestName(size_t combo_id) const;
  TestParameters MakeParameters(size_t combo_id) const;

 private:
  void ThrowIfOverflow(size_t combo_id) const;
  static size_t EstimateNumberOfCombinations(
      const std::vector<Parameter>& parameters);

 private:
  const std::vector<Parameter>& parameters_;
  const size_t number_of_combos_;
};

}  // namespace api_proxy::models
