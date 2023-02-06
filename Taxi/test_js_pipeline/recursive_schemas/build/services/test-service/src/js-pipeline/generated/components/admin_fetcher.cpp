/* THIS FILE IS AUTOGENERATED, DON'T EDIT! */

#include "admin_fetcher.hpp"

#include <js-pipeline/fetching/schema/registry.hpp>
#include <js-pipeline/generated/consumers.hpp>

namespace js_pipeline::generated::components {

using ::js_pipeline::generated::consumers::TestConsumerTag;

namespace {

template <typename... ConsumerTags>
std::vector<const char*> ConsumerNames() {
  static_assert((fetching::schema::IsConsumerTag<ConsumerTags>() && ...));
  return {ConsumerTags::kName...};
}

}  // namespace

AdminFetcher::AdminFetcher(const ::components::ComponentConfig& config,
                           const ::components::ComponentContext& context)
    : fetching::admin_pipeline::Component(ConsumerNames<TestConsumerTag>(),
                                          config, context) {}

}  // namespace js_pipeline::generated::components