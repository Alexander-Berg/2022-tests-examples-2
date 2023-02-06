#pragma once

#include <js-pipeline/resource_management/component.hpp>

#include <utils/js_typed_resource.hpp>

#include <defs/internal/js_test.hpp>

namespace resources::test {

struct Processor {
  inline static const std::string kName = "test";

  using In = ::defs::internal::js_test::Input;
  using Out = ::defs::internal::js_test::Output;

  Processor(const ::components::ComponentContext&,
            const ::components::ComponentConfig&) {}

  Out operator()(In&& input) const;
};

using Base = ::grocery_surge::utils::JsTypedResource<Processor>;

// Hopefully would be enough in most cases
// using Resource = Base;

// For test purposes - override WrapResult method
class Resource : public Base {
 public:
  using Base::Base;

  js_pipeline::resource_management::InstancePtr WrapResult(
      formats::json::Value&& val) const override;
};

}  // namespace resources::test
