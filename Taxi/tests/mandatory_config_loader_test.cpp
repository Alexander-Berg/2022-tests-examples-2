#include <userver/engine/task/task.hpp>
#include <userver/utest/utest.hpp>

#include <clients/experiments3-proxy/client_mock_base.hpp>
#include <experiments3/models/experiment_type.hpp>
#include <experiments3/models/mandatory_config_loader.hpp>

#include <taxi_config/variables/EXPERIMENTS3_COMMON_LIBRARY_SETTINGS.hpp>
#include <testing/source_path.hpp>
#include <testing/taxi_config.hpp>

#include <boost/filesystem/operations.hpp>

namespace proxy = ::clients::experiments3_proxy;

namespace {
const std::string kFilesDir =
    utils::CurrentSourcePath("src/tests/static/mandatory_config_loader_test/");

const std::string kDumpDir = "/tmp/mandatory_config_loader_test_dir";
}  // namespace

class MockClient : public proxy::ClientMockBase {
 public:
  MockClient() {
    auto configs =
        formats::json::blocking::FromFile(kFilesDir + "test_configs.json");
    for (const auto& config : configs["configs"]) {
      configs_.insert({config["name"].As<std::string>(), std::move(config)});
    }
  }

  proxy::v1_configs::post::Response V1Configs(
      const proxy::v1_configs::post::Request& request,
      const proxy::CommandControl&) const override {
    times_called_++;
    if (return_error_) {
      throw ::clients::http::TimeoutException("test timeout", {});
    }
    if (overwritten_response_) {
      std::vector<proxy::Experiment> configs;
      for (const auto& config : *overwritten_response_) {
        configs.push_back({config});
      }
      return proxy::v1_configs::post::Response{{std::move(configs)}};
    }

    proxy::v1_configs::post::Response response;
    for (const auto& name : request.body.names) {
      if (configs_.count(name)) {
        response.values.push_back({configs_.at(name)});
      }
    }
    return response;
  }

  int TimesCalled() { return times_called_; }

  void ReturnError(bool flag) { return_error_ = flag; }

  void OverwriteResponse(std::vector<formats::json::Value>&& response) {
    overwritten_response_ = std::move(response);
  }

 private:
  std::unordered_map<std::string, formats::json::Value> configs_;
  mutable int times_called_ = 0;
  bool return_error_ = false;
  std::optional<std::vector<formats::json::Value>> overwritten_response_;
};

namespace {
void CleanupDumpDir() { boost::filesystem::remove_all(kDumpDir); }

auto MakeConfigStorage() {
  taxi_config::experiments3_common_library_settings::Generalsettings settings;
  settings.mandatory_config_loading_retries = 60;
  settings.mandatory_config_loading_retry_timeout = std::chrono::seconds(0);
  return dynamic_config::MakeDefaultStorage(
      {{taxi_config::EXPERIMENTS3_COMMON_LIBRARY_SETTINGS, {settings}}});
}

experiments3::models::MandatoryConfigLoader CreateLoader(
    const MockClient& client, const dynamic_config::StorageMock& storage) {
  auto config = storage.GetSource();
  return experiments3::models::MandatoryConfigLoader(
      client, engine::current_task::GetTaskProcessor(), config,
      {"test_config1", "test_config2", "test_config3"}, kDumpDir);
}
}  // namespace

UTEST(MandatoryConfigLoader, LoadConfigs) {
  MockClient client;
  auto storage = MakeConfigStorage();
  auto loader = CreateLoader(client, storage);
  auto configs = loader.LoadConfigs();
  ASSERT_EQ(configs.size(), 3);
  ASSERT_EQ(configs[0]["name"].As<std::string>(), "test_config1");
  ASSERT_EQ(configs[1]["name"].As<std::string>(), "test_config2");
  ASSERT_EQ(configs[2]["name"].As<std::string>(), "test_config3");
  ASSERT_EQ(client.TimesCalled(), 1);
  CleanupDumpDir();
}

UTEST(MandatoryConfigLoader, CheckDumpFiles) {
  MockClient client;
  auto storage = MakeConfigStorage();
  auto loader1 = CreateLoader(client, storage);
  auto configs1 = loader1.LoadConfigs();
  ASSERT_EQ(configs1.size(), 3);
  ASSERT_EQ(client.TimesCalled(), 1);

  client.ReturnError(true);
  auto loader2 = CreateLoader(client, storage);
  auto configs2 = loader2.LoadConfigs();
  ASSERT_EQ(configs1.size(), 3);
  // +61 attempts
  ASSERT_EQ(client.TimesCalled(), 62);

  ASSERT_EQ(configs1, configs2);
  CleanupDumpDir();
}

UTEST(MandatoryConfigLoader, FailedToStart) {
  MockClient client;
  auto storage = MakeConfigStorage();
  client.ReturnError(true);

  auto loader = CreateLoader(client, storage);
  ASSERT_THROW(loader.LoadConfigs(),
               experiments3::models::MandatoryConfigLoadingError);
  CleanupDumpDir();
}

UTEST(MandatoryConfigLoader, PartialConfigResponse) {
  auto configs = formats::json::blocking::FromFile(
                     kFilesDir + "test_configs.json")["configs"]
                     .As<std::vector<formats::json::Value>>();
  MockClient client;
  auto storage = MakeConfigStorage();
  client.OverwriteResponse({configs[0], configs[2]});
  auto loader = CreateLoader(client, storage);
  ASSERT_THROW(loader.LoadConfigs(),
               experiments3::models::MandatoryConfigLoadingError);

  client.OverwriteResponse({configs[0], configs[2], configs[0]});
  ASSERT_THROW(loader.LoadConfigs(),
               experiments3::models::MandatoryConfigLoadingError);
  CleanupDumpDir();
}

UTEST(MandatoryConfigLoader, PartialReadFromStorage) {
  MockClient client;
  auto storage = MakeConfigStorage();
  auto loader = CreateLoader(client, storage);
  auto configs = loader.LoadConfigs();
  ASSERT_EQ(configs.size(), 3);
  ASSERT_EQ(configs[0]["name"].As<std::string>(), "test_config1");
  ASSERT_EQ(configs[1]["name"].As<std::string>(), "test_config2");
  ASSERT_EQ(configs[2]["name"].As<std::string>(), "test_config3");
  ASSERT_EQ(client.TimesCalled(), 1);

  boost::filesystem::remove(kDumpDir +
                            "/__mandatory_configs/test_config1.json");
  client.ReturnError(true);
  ASSERT_THROW(loader.LoadConfigs(),
               experiments3::models::MandatoryConfigLoadingError);
}
