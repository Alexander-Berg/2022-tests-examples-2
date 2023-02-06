#include "mock_translator.hpp"

namespace zoneinfo {

Translator MockTranslator(std::optional<TranslateHandler> handler) {
  if (!handler) {
    handler = [](const std::string& keyset, const std::string& key,
                 const std::string& locale) {
      return keyset + "_" + key + "_tr_" + locale;
    };
  }
  return std::make_shared<TestTranslator>(*handler);
}

void AssertTankerKey(const TankerKey& left, const TankerKey& right) {
  ASSERT_EQ(left.keyset, right.keyset);
  ASSERT_EQ(left.key, right.key);
}

}  // namespace zoneinfo
