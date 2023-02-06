#pragma once

#include "internal/setting/repository.hpp"

#include "tests/internal/models_test.hpp"

#include <functional>

namespace sweet_home::mocks {

using GetDefinitionsHandler =
    std::function<setting::SettingDefinitionsMap(const std::string&)>;

class SettingDefinitionRepositoryMock
    : public setting::SettingDefinitionRepository {
 private:
  GetDefinitionsHandler handler_;

 public:
  SettingDefinitionRepositoryMock() = default;

  void SetStub_GetDefinitions(const GetDefinitionsHandler& handler) {
    handler_ = handler;
  }

  setting::SettingDefinitionsMap GetDefinitions(
      const std::string& service_id) const override {
    if (handler_) {
      return handler_(service_id);
    }
    return tests::MakeSettingDefinitionMap(
        {tests::MakeDefinition("global_setting_id", "global_default_value"),
         tests::MakeDefinition("service_setting_id", "another_default_value",
                               true, true)});
  }
};

}  // namespace sweet_home::mocks
