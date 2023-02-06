#include "test_case_base.hpp"

#include <fmt/format.h>

namespace hejmdal::radio::tester {

inline static const std::string kTestCaseBlockType = "test_case_block";

TestCaseBlock::TestCaseBlock(int test_case_id, StateInCallbackFunc callback)
    : OutputConsumer(fmt::format("test_case_{}", test_case_id)),
      callback_(callback) {}

void TestCaseBlock::StateIn(const Meta&, const time::TimePoint& tp,
                            const State& state) {
  callback_(tp, state);
}

const std::string& TestCaseBlock::GetType() const { return kTestCaseBlockType; }

formats::json::Value TestCaseBlock::Serialize() const {
  return formats::json::Value();
}

TestCaseBase::TestCaseBase(int test_case_id, std::string description,
                           time::TimeRange range)
    : id_(std::move(test_case_id)),
      description_(std::move(description)),
      time_range_(std::move(range)) {}

void TestCaseBase::SetCallback(OutPointAccess&& out_point) {
  out_point.OnStateOut(std::make_shared<TestCaseBlock>(
      id_, [this](const time::TimePoint& tp, const State& state) {
        return StateInCallback(tp, state);
      }));
}

}  // namespace hejmdal::radio::tester
