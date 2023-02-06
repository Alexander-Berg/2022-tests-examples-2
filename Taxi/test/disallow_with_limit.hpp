#pragma once

#include <candidates/filters/test/disallow_with_limit_info.hpp>
#include <candidates/filters/test/dummy.hpp>

namespace candidates::filters::test {

class DisallowWithLimitFactory : public Factory {
 public:
  DisallowWithLimitFactory() : Factory(info::kDisallowWithLimit) {}

  std::unique_ptr<Filter> Create(
      [[maybe_unused]] const formats::json::Value& params,
      [[maybe_unused]] const FactoryEnvironment& env) const override {
    return std::make_unique<DisallowAll>(info());
  }
};

}  // namespace candidates::filters::test
