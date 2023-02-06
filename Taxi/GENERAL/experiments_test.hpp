#pragma once

#include "experiments_base.hpp"

namespace yaga::internal {
class TestExperiments : public ExperimentsBase {
 public:
  Values GetExperimentsValues(const DriverIdKey&, const std::string&,
                              const std::vector<int>&
                              /* const DriverPos& */) const override {
    ++request_count;
    return result_;
  }

  void SetResult(Values&& result) { result_ = std::move(result); }
  void SetResult(const Values& result) { result_ = result; }

  size_t GetRequestCount() const { return request_count; }

 private:
  Values result_{};
  mutable size_t request_count = 0;
};
}  // namespace yaga::internal
