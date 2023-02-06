#pragma once

#include <js-pipeline/resource_management/component.hpp>

namespace resources::test_resource {

class Resource: public js_pipeline::resource_management::Resource {
  using Base = js_pipeline::resource_management::Resource;

  static inline const std::string kName = "test_resource";

 public:
  Resource(const components::ComponentContext&,
           const components::ComponentConfig&, js_pipeline::ResourceMetadata);

  js_pipeline::resource_management::InstancePtr GetData(
      const formats::json::Value& params) const override;
};

}
