#pragma once

#include "endpoints/full/core/context.hpp"
#include "endpoints/full/core/input.hpp"
#include "endpoints/full/plugins/base.hpp"
#include "endpoints/lightweight/plugins/base.hpp"

namespace routestats::test {

core::WalletsPtr GetDefaultUserWallets();
core::TaxiConfigsPtr GetDefaultTaxiConfigs();
core::Configs3 GetDefaultConfigs3();
const core::Experiments& GetDefaultExperiments();
core::Zone GetDefaultZone();

namespace full {
std::shared_ptr<const plugins::top_level::Context> MakeTopLevelContext(
    routestats::full::ContextData);

routestats::full::ContextData GetDefaultContext();

routestats::full::RoutestatsInput GetDefaultInput();

routestats::full::User GetDefaultUser();

routestats::full::RenderingContext GetDefaultRendering();
}  // namespace full

namespace lightweight {
std::shared_ptr<const routestats::lightweight::Context> MakeTopLevelContext(
    routestats::lightweight::ContextData);

routestats::lightweight::ContextData GetDefaultContext();
}  // namespace lightweight

}  // namespace routestats::test
