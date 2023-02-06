#pragma once

#include <endpoints/common/core/service_level/extension.hpp>
#include <endpoints/common/core/service_level/models.hpp>

#include <functional>

namespace routestats::test {

using Configurator = std::function<void(core::ServiceLevel&)>;

core::ServiceLevel MockDefaultServiceLevel(
    const std::string& class_name, std::optional<Configurator> = std::nullopt);

void ApplyExtensions(core::ServiceLevelExtensionsMap results,
                     std::vector<core::ServiceLevel>& levels);

}  // namespace routestats::test
