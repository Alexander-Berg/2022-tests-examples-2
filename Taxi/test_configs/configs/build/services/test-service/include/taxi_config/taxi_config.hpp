/* THIS FILE IS AUTOGENERATED, DON'T EDIT! */

#pragma once

#include <userver/dynamic_config/snapshot.hpp>
#include <userver/dynamic_config/value.hpp>

#include <taxi_config/variables/LOCALES_MAPPING.hpp>
#include <taxi_config/variables/LOCALES_SUPPORTED.hpp>
#include <taxi_config/variables/REF.hpp>

namespace taxi_config {

struct TaxiConfig final {
  explicit TaxiConfig(const dynamic_config::DocsMap& docs_map);

  ::taxi_config::locales_mapping::LocalesMapping locales_mapping;

  ::std::vector<std::string> locales_supported;

  ::taxi_config::common_ref::Obj ref;
};

}
