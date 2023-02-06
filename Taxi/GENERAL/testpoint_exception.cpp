#include "testpoint_exception.hpp"

namespace united_dispatch::testsuite {

void RaiseTestpointException(const formats::json::Value& body) {
  if (body["raise_exception"].As<bool>(false)) {
    throw TestpointException{};
  }
}

}  // namespace united_dispatch::testsuite
