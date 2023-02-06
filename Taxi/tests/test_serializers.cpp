#include <gtest/gtest.h>
#include <models/tanker_keyset.hpp>

using namespace localizations_replica::models;

TEST(TestSerializers, TestSerializersTankerKeyset) {
  Translations translation1({
      {"ru", {{1, "form1"}, {2, "form2"}}},
      {"en", {{1, "translate"}}},
  });

  Translations translation2({
      {"ru", {{1, "form1"}, {2, "form2"}}},
      {"en", {{1, "translate"}}},
  });

  TankerKeyset tanker_keyset1;
  tanker_keyset1.SetKey("moskow", std::move(translation1));
  tanker_keyset1.SetKey("spb", std::move(translation2));

  formats::bson::Value bson = SerializeToBson(std::move(tanker_keyset1));

  TankerKeyset tanker_keyset2 = ParseTankerKeyset(bson);

  // check keyset
  KeysetTranslations keyset = tanker_keyset2.GetMap();

  for (const auto& [key, translations] : keyset) {
    EXPECT_TRUE((key == "moskow") || (key == "spb"));
    for (const auto& [locale, forms] : translations) {
      EXPECT_TRUE((locale == "ru") || (locale == "en"));
      for (const auto& [form, translation] : forms) {
        if ((key == "moskow") && (locale == "ru")) {
          EXPECT_TRUE((translation == "form1") || (translation == "form2"));
        }
        if ((key == "spb") && (locale == "ru")) {
          EXPECT_TRUE((translation == "form1") || (translation == "form2"));
        }
        if (locale == "en") {
          EXPECT_TRUE(translation == "translate");
        }
      }
    }
  }
}
