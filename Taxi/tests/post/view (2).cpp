#include "view.hpp"

#include <models/tests.hpp>
#include <models/validation.hpp>
#include <views/utils/response.hpp>

namespace handlers::admin_v2_endpoints_tests::post {

namespace types = api_proxy::models::admin::types;
namespace errors = api_proxy::models::admin::errors;
namespace utils = api_proxy::views::utils;

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  Response200 response;

  try {
    const auto code = types::FromHandlerFormat(request.body);
    const auto operators_registry = *dependencies.extra.operators_registry_;

    const auto uuid =
        types::EndpointUUID{types::ClusterID{request.cluster}, request.id};

    api_proxy::models::RunEndpointTests(uuid, code, dependencies.extra.secdist_,
                                        dependencies.pg_api_proxy->GetCluster(),
                                        operators_registry,
                                        dependencies.extra.modules_manager_);

    api_proxy::models::RunEndpointValidations(
        uuid, code, operators_registry, dependencies.extra.modules_manager_,
        dependencies.extra.configuration_, dependencies.extra.taxi_config_,
        dependencies.extra.dynamic_config_client_updater_);

  } catch (errors::TestsFailed& err) {
    return utils::MakeResponse<Response400>(request, dependencies, err);
  } catch (errors::ValidationFailed& err) {
    return utils::MakeResponse<Response400>(request, dependencies, err);
  } catch (errors::ResourcesNotExists& err) {
    return utils::MakeResponse<Response400>(request, dependencies, err);
  }

  return response;
}

}  // namespace handlers::admin_v2_endpoints_tests::post
