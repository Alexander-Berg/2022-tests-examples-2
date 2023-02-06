#include "test_config.hpp"

#include <fstream>

#include <models/configs.hpp>

namespace config {

DocsMap DocsMapForTest() {
  const std::string path{CONFIG_FALLBACK_DIR "/configs.json"};
  const auto fallback_values = models::configs::ReadFallback(path);
  return models::configs::JsonToDocsMap(fallback_values);
}

}  // namespace config
