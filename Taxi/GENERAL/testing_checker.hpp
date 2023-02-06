#pragma once

#include <userver/components/component_config.hpp>
#include <userver/components/component_context.hpp>
#include <userver/components/loggable_component_base.hpp>
#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/source.hpp>

namespace eats_performer_statistics::components {

class TestingChecker final : public ::components::LoggableComponentBase {
 public:
  static constexpr auto kName = "testing-checker";

  TestingChecker(const ::components::ComponentConfig& config,
                 const ::components::ComponentContext& context);

  bool IsTesting() const;

  ~TestingChecker() = default;

 private:
  bool is_testing_;
};

}  // namespace eats_performer_statistics::components
