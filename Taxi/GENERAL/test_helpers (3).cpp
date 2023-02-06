#include "test_helpers.hpp"

#include <fmt/format.h>

#include <userver/formats/json.hpp>
#include <userver/testsuite/testpoint.hpp>

namespace utils {

void CreateErrorInjectorTestpoint(const std::string& prefix) {
  TESTPOINT_CALLBACK(fmt::format("{}::error-injector", prefix),
                     formats::json::Value(),
                     [](const formats::json::Value& doc) {
                       if (doc.IsObject()) {
                         if (doc["inject_failure"].As<bool>())
                           throw std::runtime_error("injected error");
                       }
                     });
}

}  // namespace utils
