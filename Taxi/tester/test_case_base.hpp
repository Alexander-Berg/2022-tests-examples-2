#pragma once

#include <functional>
#include <list>

#include <userver/formats/json.hpp>

#include <radio/circuit.hpp>
#include <utils/time.hpp>

namespace hejmdal::radio::tester {

using OutputConsumer = hejmdal::radio::blocks::OutputConsumer;
using Meta = hejmdal::radio::blocks::Meta;
using State = hejmdal::radio::blocks::State;

using StateInCallbackFunc =
    std::function<void(const time::TimePoint& tp, const State& state)>;

class TestCaseBase;

class TestCaseBlock : public OutputConsumer {
 public:
  TestCaseBlock(int test_case_id, StateInCallbackFunc callback);

  virtual formats::json::Value Serialize() const override;
  virtual const std::string& GetType() const override;

  void StateIn(const Meta&, const time::TimePoint& tp,
               const State& state) override;

 private:
  StateInCallbackFunc callback_;
};

struct TestCaseResult {
  int test_case_id;
  std::string check_type;
  bool passed = true;
  bool ignored = false;
  std::string description;
  std::optional<std::string> error_message = std::nullopt;

  TestCaseResult(int id, std::string type, std::string description)
      : test_case_id(std::move(id)),
        check_type(std::move(type)),
        description(std::move(description)) {}
};

class TestCaseBase {
 public:
  TestCaseBase(int test_case_id, std::string description,
               time::TimeRange range);

  template <class TTestCase>
  static typename std::enable_if_t<std::is_base_of_v<TestCaseBase, TTestCase>,
                                   std::shared_ptr<TestCaseBase>>
  Build(int test_case_id, std::string&& description, time::TimeRange&& range,
        formats::json::Value&& params, OutPointAccess&& out_point);

  int GetId() const { return id_; };
  std::string GetDescription() const { return description_; };
  time::TimeRange GetTimeRange() const { return time_range_; };

  virtual const std::string& GetType() const = 0;
  virtual TestCaseResult GetResult() const = 0;

 private:
  void SetCallback(OutPointAccess&& out_point);

  virtual void Initialize(formats::json::Value params) = 0;
  virtual void StateInCallback(const time::TimePoint& tp,
                               const State& state) = 0;

 private:
  const int id_;
  const std::string description_;
  const time::TimeRange time_range_;
};

template <class TTestCase>
typename std::enable_if_t<std::is_base_of_v<TestCaseBase, TTestCase>,
                          std::shared_ptr<TestCaseBase>>
TestCaseBase::Build(int test_case_id, std::string&& description,
                    time::TimeRange&& range, formats::json::Value&& params,
                    OutPointAccess&& out_point) {
  try {
    auto ptr = std::make_shared<TTestCase>(test_case_id, std::move(description),
                                           std::move(range));
    ptr->Initialize(std::move(params));
    ptr->SetCallback(std::move(out_point));
    return ptr;
  } catch (std::exception& ex) {
    throw except::Error("Could not build test case with id '{}': {}",
                        test_case_id, ex.what());
  }
}

using TestCasePtr = std::shared_ptr<TestCaseBase>;

}  // namespace hejmdal::radio::tester
