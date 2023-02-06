#pragma once

#include <models/admin/types.hpp>

#include <string>
#include <vector>

#include <experiments3/components/experiments3_cache_fwd.hpp>
#include <userver/storages/postgres/postgres_fwd.hpp>

namespace agl::core {
class OperatorsRegistry;
}

namespace api_proxy::components {
class ConfigurationComponent;
}

namespace api_proxy::core {
struct ParsedTest;
}

namespace api_proxy::models {
class TestParameters;
}

namespace components {
class Secdist;
}

namespace agl::modules {
class Manager;
}

namespace api_proxy::models {

struct HandlerMatch;

/*!
 * \returns error message if test failed
 * */
std::optional<std::string> RunTest(
    const api_proxy::models::HandlerMatch& handler_match,
    const api_proxy::core::ParsedTest& test, const std::string& test_id,
    const std::optional<TestParameters> test_params,
    const ::components::Secdist& secdist,
    const std::vector<admin::types::Resource>& resources);

std::vector<std::string> RunTests(
    const api_proxy::models::HandlerMatch& handler_match,
    const ::components::Secdist& secdist,
    const storages::postgres::ClusterPtr& pg_cluster);

/*!
 * \throws errors::TestsFailed in case of test errors
 * */

void RunEndpointTests(const models::admin::types::Endpoint& endpoint,
                      const ::components::Secdist& secdist,
                      const storages::postgres::ClusterPtr& pg_cluster,
                      const agl::core::OperatorsRegistry& operators_registry,
                      const agl::modules::Manager& modules_manager);

void RunEndpointTests(handlers::EndpointWithoutPathDef&& endpoint,
                      const std::string& id, const std::string& path,
                      const ::components::Secdist& secdist,
                      const storages::postgres::ClusterPtr& pg_cluster,
                      const agl::core::OperatorsRegistry& operators_registry,
                      const agl::modules::Manager& modules_manager);

void RunEndpointTests(const admin::types::EndpointUUID& uuid,
                      const models::admin::types::EndpointCode& code,
                      const ::components::Secdist& secdist,
                      const storages::postgres::ClusterPtr& pg_cluster,
                      const agl::core::OperatorsRegistry& operators_registry,
                      const agl::modules::Manager& modules_manager);

}  // namespace api_proxy::models
