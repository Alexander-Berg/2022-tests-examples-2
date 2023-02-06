#pragma once

#include <userver/testsuite/testpoint.hpp>

namespace united_dispatch::testsuite {

class TestpointException : public std::runtime_error {
 public:
  TestpointException() : std::runtime_error{"testsuite: interrupt point"} {}
};

void RaiseTestpointException(const formats::json::Value& body);

// register exception throw via testsuite
inline void ThrowTestpointException(const std::string& testpoint) {
  TESTPOINT_CALLBACK(testpoint, {},
                     &::united_dispatch::testsuite::RaiseTestpointException);
}

}  // namespace united_dispatch::testsuite
