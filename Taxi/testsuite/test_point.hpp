#pragma once

#include <string>

#include <json/value.h>
#include <threads/async.hpp>

namespace utils {
namespace testsuite {

class TestPointControl {
 public:
  TestPointControl(const Async& async, const std::string& url, int timeout);
  ~TestPointControl();
};

Json::Value TestPoint(const std::string& name, const Json::Value& data,
                      const LogExtra& log_extra);
bool IsTestPointEnabled();

}  // namespace testsuite
}  // namespace utils
