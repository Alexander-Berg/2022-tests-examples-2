#pragma once

#include <memory>
#include <string>

#include <candidates/filters/filter.hpp>

namespace candidates::filters::test {

class AllowAll : public Filter {
 public:
  static constexpr const char* kName = "test/allow_all";

  AllowAll(const FilterInfo& info) : Filter(info) {}

  Result Process(const GeoMember&, Context&) const override {
    return Result::kAllow;
  }
};

class IgnoreAll : public Filter {
 public:
  static constexpr const char* kName = "test/ignore_all";

  IgnoreAll(const FilterInfo& info) : Filter(info) {}

  Result Process(const GeoMember&, Context&) const override {
    return Result::kIgnore;
  }
};

class DisallowAll : public Filter {
 public:
  static constexpr const char* kName = "test/disallow_all";

  DisallowAll(const FilterInfo& info) : Filter(info) {}

  Result Process(const GeoMember&, Context&) const override {
    return Result::kDisallow;
  }
};

template <typename T>
class DummyFactory : public Factory {
 public:
  DummyFactory() : Factory(FilterInfo{T::kName, {}, {}, false, {}}) {}
  explicit DummyFactory(const FilterInfo& info) : Factory(info) {}

  std::unique_ptr<Filter> Create(const formats::json::Value&,
                                 const FactoryEnvironment&) const override {
    return std::make_unique<T>(info());
  }
};

}  // namespace candidates::filters::test
