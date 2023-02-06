#include "testpoint_failure.hpp"

#include <userver/testsuite/testpoint.hpp>

namespace eats_full_text_search_indexer::utils {

void InjectTestpointFailure(const std::string& name) {
  TESTPOINT_CALLBACK(
      name, formats::json::Value(), [](const formats::json::Value& doc) {
        if (doc.IsObject()) {
          if (doc["inject_failure"].As<bool>()) {
            throw std::runtime_error(doc["error_text"].As<std::string>());
          }
        }
      });
}

}  // namespace eats_full_text_search_indexer::utils
