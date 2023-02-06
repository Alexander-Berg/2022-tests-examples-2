#include "test_case.hpp"

namespace hejmdal::models::postgres {

bool TestCase::operator==(const TestCase& other) const {
  return Introspect() == other.Introspect();
}

}  // namespace hejmdal::models::postgres
