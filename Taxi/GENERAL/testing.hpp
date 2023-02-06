#include <userver/dynamic_config/snapshot.hpp>
#include <userver/formats/json_fwd.hpp>
#include <userver/storages/redis/client.hpp>

#include <defs/all_definitions_fwd.hpp>
#include <handlers/dependencies_fwd.hpp>

namespace helpers::testing {

using handlers::TestStatus;

struct TestResults {
  TestStatus status;
  std::vector<formats::json::Value> responses;
  std::vector<std::string> errors;
};

class TestProcessor {
 public:
  TestProcessor(const std::shared_ptr<storages::redis::Client> storage,
                const dynamic_config::Snapshot& config);
  void StartTest(const std::string& test_id) const;
  void FinishTest(const std::string& test_id,
                  const std::vector<formats::json::Value>& responses,
                  const std::vector<std::string>& errors) const;
  std::optional<TestResults> GetTestResults(const std::string& test_id) const;

 private:
  const std::shared_ptr<storages::redis::Client> storage_;
  const storages::redis::CommandControl redis_cc_;
  const std::chrono::milliseconds redis_ttl_;
};

template <typename View>
void ExecuteTest(const std::string& test_id, std::size_t requests_count,
                 std::unordered_map<std::string, std::string>&& headers,
                 formats::json::Value&& request_json,
                 handlers::Dependencies&& dependencies);

}  // namespace helpers::testing
