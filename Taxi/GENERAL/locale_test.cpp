#include <userver/utest/utest.hpp>

#include "locale.hpp"

namespace aul = autoaccept::utils::locale;

TEST(Locale, FindBestMatch) {
  ASSERT_EQ(aul::FindBestMatch("fr-CH, fr;q=0.9, en;q=0.8, de;q=0.7",
                               {"fr-CH", "fr", "en", "de"}, {}),
            "fr-CH");
  ASSERT_EQ(aul::FindBestMatch("fr-CH, fr;q=0.9, en;q=0.8, de;q=0.7",
                               {"en", "de"}, {}),
            "en");
  ASSERT_EQ(aul::FindBestMatch("fr-CH, fr;q=0.9, en;q=0.8, de;q=0.7",
                               {"fr-CH", "fr", "en", "de"}, {{"fr-CH", "fr"}}),
            "fr");
  ASSERT_EQ(aul::FindBestMatch("fr-CH, fr;q=0.9, en;q=0.8, de;q=0.7", {}, {}),
            "en");
}
