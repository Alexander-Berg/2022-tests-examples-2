#pragma once

#include <js-pipeline/resource_management/component.hpp>
#include <js-pipeline/resource_management/typed/resource.hpp>

namespace resources::test_typed_resource {

using Params = /* specify params type */;
using Data = /* specify data type */;
using Base = js_pipeline::resource_management::typed::Resource<Params, Data>;

class Resource: public Base {
  static inline const std::string kName = "test_typed_resource";

 public:
  Resource(const components::ComponentContext&,
           const components::ComponentConfig&, js_pipeline::ResourceMetadata);

  Data GetData(const Params& params) const override;
};

}
