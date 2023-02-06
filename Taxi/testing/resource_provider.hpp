#pragma once

#include <js-pipeline/resource_management/interface.hpp>

namespace js_pipeline::testing {

class ResourceProvider : public resource_management::ResourceProvider {
  std::string test_name_;
  std::string testcase_name_;

 public:
  ResourceProvider(std::string test_name, std::string testcase_name);

  resource_management::Instances GetData(
      const resource_management::ResourceRequestByField&,
      resource_management::Cache*) const override;

  inline const std::string& GetTestName() const { return test_name_; }
  inline const std::string& GetTestcaseName() const { return testcase_name_; }
};

}  // namespace js_pipeline::testing
