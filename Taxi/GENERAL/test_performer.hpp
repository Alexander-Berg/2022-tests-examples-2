#pragma once
#include "processes/performer.hpp"

namespace routehistory::processes {

struct TestData {
  std::optional<int> counter{};
  int from{};
  int to{};
};

TestData Parse(const ::formats::json::Value& data,
               ::formats::parse::To<TestData>);
::formats::json::Value Serialize(
    const TestData& data, ::formats::serialize::To<formats::json::Value>);

class TestPerformer : public TypedPerformer<TestData> {
 public:
  using TypedPerformer<TestData>::TypedPerformer;

  static constexpr const char* kType = "test";

  void Run(RunContext&) override;
};

}  // namespace routehistory::processes
