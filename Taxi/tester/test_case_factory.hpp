#pragma once

#include <radio/circuit.hpp>
#include <radio/tester/test_case_base.hpp>

namespace hejmdal::models::postgres {
struct TestCase;
}

namespace hejmdal::radio::tester {

class TestCaseFactory {
 public:
  [[nodiscard]] static TestCasePtr Build(
      CircuitPtr circuit, models::postgres::TestCase pg_test_case);
};

}  // namespace hejmdal::radio::tester
