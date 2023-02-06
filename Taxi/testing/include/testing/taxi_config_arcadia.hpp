#include <library/cpp/resource/resource.h>

#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/source.hpp>
#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/dynamic_config/value.hpp>

namespace dynamic_config {

namespace impl {

inline const char* kResourceName = "tests:taxi_config_fallback.json";

inline dynamic_config::DocsMap ReadDefaultDocsMap() {
  std::string contents = NResource::Find(kResourceName);
  dynamic_config::DocsMap docs_map;
  docs_map.Parse(contents, false);
  return docs_map;
}

inline const dynamic_config::DocsMap& GetDefaultDocsMap() {
  static const auto default_docs_map = ReadDefaultDocsMap();
  return default_docs_map;
}

}  // namespace impl

inline dynamic_config::StorageMock MakeDefaultStorage(
    const std::vector<dynamic_config::KeyValue>& overrides) {
  return dynamic_config::StorageMock(impl::GetDefaultDocsMap(), overrides);
}

inline dynamic_config::Source GetDefaultSource() {
  static const auto storage = MakeDefaultStorage({});
  return storage.GetSource();
}

inline const dynamic_config::Snapshot& GetDefaultSnapshot() {
  static const auto snapshot = GetDefaultSource().GetSnapshot();
  return snapshot;
}

}  // namespace dynamic_config
