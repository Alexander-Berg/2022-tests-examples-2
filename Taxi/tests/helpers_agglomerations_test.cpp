#include <userver/utest/utest.hpp>

#include <subvention-rule-utils/helpers/agglomerations.hpp>

namespace sru = subvention_rule_utils;

TEST(HelpersAgglomerations, GetNodeName) {
  EXPECT_EQ(sru::helpers::GetNodeName("one/two"), "two");
  EXPECT_EQ(
      sru::helpers::GetNodeName("br_root/br_russia/br_tsentralnyj_fo/"
                                "br_moskovskaja_obl/br_moscow/br_moscow_adm"),
      "br_moscow_adm");
  EXPECT_EQ(sru::helpers::GetNodeName("br_root"), "br_root");
  EXPECT_EQ(sru::helpers::GetNodeName("/"), "");
  EXPECT_EQ(sru::helpers::GetNodeName("/ore"), "ore");
  EXPECT_EQ(sru::helpers::GetNodeName("bad/"), "");
}
