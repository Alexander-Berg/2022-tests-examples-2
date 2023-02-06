#include <resources/test_resource/resource.hpp>

namespace resources::test_resource {

Resource::Resource(const components::ComponentContext&,
                   const components::ComponentConfig&,
                   js_pipeline::ResourceMetadata metadata)
    : Base(kName, std::move(metadata))
{}

js_pipeline::resource_management::InstancePtr Resource::GetData(
    const formats::json::Value&) const {
  // Write implementation here
  return nullptr;
}

}
