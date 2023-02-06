#pragma once

#include <testing/source_path.hpp>
#include <userver/utils/async.hpp>

#include <taxi/graph/libs/mapmatcher/matcher_config.h>

#include <memory>
#include <string>

namespace yaga::test {

/// This plugin provides few constants for fixtures that use mapmatcher
class MapmatcherFixturePlugin {
 protected:
  /// Path to mapmatcher's config file
  static constexpr const char* const kMapmatcherConfigFile =
      "configs/mapmatcher/online.conf";
  /// Returns new mapmatcher's config object
  static std::unique_ptr<NTaxi::NMapMatcher2::TMatcherConfig>
  CreateMatcherConfig() {
    std::string matcher_config_file =
        ::utils::CurrentSourcePath(kMapmatcherConfigFile);
    return std::make_unique<NTaxi::NMapMatcher2::TMatcherConfig>(
        matcher_config_file.c_str());
  }

 protected:
  void PluginSetUp() {}
  void PluginTearDown() {}

  static void PluginSetUpTestSuite() {}
  static void PluginTearDownTestSuite() {}
};

}  // namespace yaga::test
