#include <chrono>
#include <string>

#include <fmt/format.h>
#include <userver/engine/sleep.hpp>
#include <userver/formats/json.hpp>
#include <userver/logging/log.hpp>
#include <userver/testsuite/testpoint.hpp>

namespace signalq_billing::utils {

inline void TestpointLogSleep(const std::string& testpoint_name,
                              const std::string& log_info_msg,
                              const std::chrono::seconds& delay_seconds) {
  TESTPOINT(testpoint_name, formats::json::Value{});

  LOG_INFO() << log_info_msg;
  engine::InterruptibleSleepFor(delay_seconds);
}

}  // namespace signalq_billing::utils
