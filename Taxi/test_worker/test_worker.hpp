#pragma once

#include "workers/ivr/algorithm_workers/base_algorithm_worker.hpp"
#include "workers/ivr/algorithm_workers/base_context.hpp"

namespace ivr_dispatcher::models {
struct ActionForLogging;
}

namespace ivr_dispatcher::workers::ivr::test {
namespace base = ivr_dispatcher::workers::ivr;

class TestWorker : public base::BaseIvrAlgorithmWorker<base::BaseContext> {
 public:
  static constexpr const char* kName = "test_worker";

  TestWorker(const components::ComponentConfig& config,
             const components::ComponentContext& context);

 private:
  ivr_dispatcher::models::ActionForLogging ProcessInit(
      const handlers::ActionRequest& request, BaseContext& context) override;
  ivr_dispatcher::models::ActionForLogging ProcessAsk(
      const handlers::ActionRequest& request, BaseContext& context) override;
};
}  // namespace ivr_dispatcher::workers::ivr::test
