#include <resources/test_typed_resource/resource.hpp>

namespace resources::test_typed_resource {

Resource::Resource(const components::ComponentContext&,
                   const components::ComponentConfig&,
                   js_pipeline::ResourceMetadata metadata)
    : Base(kName, std::move(metadata))
{}

Data Resource::GetData(const Params& params) const {
  // Write implementation here
}

}
