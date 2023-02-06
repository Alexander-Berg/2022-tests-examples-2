#include <taximeter-polling-power-policy/config.hpp>
#include "config_impl.hpp"

#include <iostream>

#include <gmock/gmock.h>

#include <gtest/gtest.h>

#include <testing/source_path.hpp>

#include <userver/formats/json/serialize.hpp>

#include <userver/dynamic_config/storage_mock.hpp>

namespace {

formats::json::Value GetJsonConfig(const std::string& path) {
  return formats::json::blocking::FromFile(
      utils::CurrentSourcePath("src/tests/static/" + path));
}

dynamic_config::StorageMock GetConfig() {
  return {{taxi_config::TAXIMETER_POLLING_POWER_POLICY_DELAYS,
           GetJsonConfig("polling_power_policy_delays.json")},
          {taxi_config::TAXIMETER_POLLING_MANAGER,
           GetJsonConfig("polling_manager.json")},
          {taxi_config::TAXIMETER_POLLING_SWITCHER,
           GetJsonConfig("polling_switcher.json")}};
}

TEST(TaximeterPollingPowerPolicyDelays, Parse) {
  const auto config = GetConfig();
  const auto& ps_delays = taximeter_polling_power_policy::GetSetting(
      "/driver/polling/state", config.GetSnapshot());
  ASSERT_EQ(300, ps_delays.full);
  ASSERT_EQ(1200, ps_delays.extra.at("powersaving"));
  ASSERT_EQ(1200, ps_delays.extra.at("background"));
  ASSERT_EQ(1800, ps_delays.extra.at("idle"));

  const auto& po_delays = taximeter_polling_power_policy::GetSetting(
      "/driver/polling/order", config.GetSnapshot());
  ASSERT_EQ(10, po_delays.full);
  ASSERT_EQ(30, po_delays.extra.at("powersaving"));
  ASSERT_EQ(30, po_delays.extra.at("background"));
  ASSERT_EQ(30, po_delays.extra.at("idle"));

  const auto& sh_delays = taximeter_polling_power_policy::GetSetting(
      "/driver/polling/shmorder", config.GetSnapshot());
  ASSERT_EQ(600, sh_delays.full);
  ASSERT_EQ(1200, sh_delays.extra.at("powersaving"));
  ASSERT_EQ(1200, sh_delays.extra.at("background"));
  ASSERT_EQ(1800, sh_delays.extra.at("idle"));

  const auto& co_delays = taximeter_polling_power_policy::GetSetting(
      "common_old", config.GetSnapshot());
  ASSERT_EQ(300, co_delays.full);

  const auto& cn_delays = taximeter_polling_power_policy::GetSetting(
      "common_new", config.GetSnapshot());
  ASSERT_EQ(300, cn_delays.full);
}

TEST(TaximeterPollingPowerPolicyDelays, BuildHeader) {
  const auto config = GetConfig();

  const auto& ps_header = taximeter_polling_power_policy::GetHeader(
      "/driver/polling/state", config.GetSnapshot());
  ASSERT_NE(ps_header.find("full=300s"), std::string::npos);
  ASSERT_NE(ps_header.find("background=1200s"), std::string::npos);
  ASSERT_NE(ps_header.find("powersaving=1200s"), std::string::npos);
  ASSERT_NE(ps_header.find("idle=1800s"), std::string::npos);

  const auto& po_header = taximeter_polling_power_policy::GetHeader(
      "/driver/polling/order", config.GetSnapshot());
  ASSERT_NE(po_header.find("full=10s"), std::string::npos);
  ASSERT_NE(po_header.find("background=30s"), std::string::npos);
  ASSERT_NE(po_header.find("powersaving=30s"), std::string::npos);
  ASSERT_NE(po_header.find("idle=30s"), std::string::npos);

  const auto& sh_header = taximeter_polling_power_policy::GetHeader(
      "/driver/polling/shmorder", config.GetSnapshot());
  ASSERT_NE(sh_header.find("full=600s"), std::string::npos);
  ASSERT_NE(sh_header.find("background=1200s"), std::string::npos);
  ASSERT_NE(sh_header.find("powersaving=1200s"), std::string::npos);
  ASSERT_NE(sh_header.find("idle=1800s"), std::string::npos);
}

TEST(TaximeterPollingPowerPolicyDelays, Disabled) {
  const auto config = GetConfig();

  const auto& ps_header = taximeter_polling_power_policy::GetHeader(
      "/driver/polling/disabled", config.GetSnapshot());
  ASSERT_NE(ps_header.find("full=30s"), std::string::npos);
  ASSERT_NE(ps_header.find("background=disabled"), std::string::npos);
  ASSERT_NE(ps_header.find("powersaving=1200s"), std::string::npos);
  ASSERT_NE(ps_header.find("idle=1800s"), std::string::npos);
}

TEST(TaximeterPollingPowerPolicyDelays, BuildHeaderFromValues) {
  ASSERT_EQ(taximeter_polling_power_policy::GetHeaderFromValues(10, {}),
            "full=10s");
  auto header = taximeter_polling_power_policy::GetHeaderFromValues(
      10, {{"background", 30}, {"idle", 90}});
  ASSERT_NE(header.find("full=10s"), std::string::npos);
  ASSERT_NE(header.find("background=30s"), std::string::npos);
  ASSERT_NE(header.find("idle=90s"), std::string::npos);
}

struct MockJitterImpl {
  MOCK_METHOD(double, Get, (double), (const, noexcept));
};

TEST(TaximeterManager, ParseAndCheckValues) {
  const auto config = GetConfig();

  const auto& uu_setting = taximeter_polling_power_policy::GetSettingNew(
      "/driver/polling/usual_usage", config.GetSnapshot());
  const auto& uu_custom_behavior =
      taximeter_polling_power_policy::GetPolicyGroupValues(uu_setting,
                                                           "custom");
  const auto& uu_default_behavior =
      taximeter_polling_power_policy::GetPolicyGroupValues(uu_setting);

  ASSERT_EQ(300, uu_default_behavior.full);
  ASSERT_EQ(30, uu_default_behavior.extra.at("powersaving"));
  ASSERT_EQ(500, uu_custom_behavior.full);
  ASSERT_EQ(1000, uu_custom_behavior.extra.at("background"));
  ASSERT_EQ(25, uu_setting.jitter_in_percent);

  const auto& od_setting = taximeter_polling_power_policy::GetSettingNew(
      "/driver/polling/only_default", config.GetSnapshot());
  const auto& od_default_behavior =
      taximeter_polling_power_policy::GetPolicyGroupValues(od_setting);

  ASSERT_EQ(300, od_default_behavior.full);
  ASSERT_EQ(30, od_default_behavior.extra.at("idle"));
  ASSERT_EQ(std::nullopt, od_setting.jitter_in_percent);

  const auto& bj_setting = taximeter_polling_power_policy::GetSettingNew(
      "/driver/polling/big_jitter", config.GetSnapshot());
  const auto& bj_default_behavior =
      taximeter_polling_power_policy::GetPolicyGroupValues(bj_setting);

  ASSERT_EQ(300, bj_default_behavior.full);
  ASSERT_EQ(30, bj_default_behavior.extra.at("idle"));
  ASSERT_EQ(50, bj_setting.jitter_in_percent);

  const auto& nij_setting = taximeter_polling_power_policy::GetSettingNew(
      "/driver/polling/not_integer_jitter", config.GetSnapshot());
  const auto& nij_default_behavior =
      taximeter_polling_power_policy::GetPolicyGroupValues(nij_setting);

  ASSERT_EQ(300, nij_default_behavior.full);
  ASSERT_EQ(30, nij_default_behavior.extra.at("idle"));
  ASSERT_EQ(1.25, nij_setting.jitter_in_percent);

  const auto& niv_setting = taximeter_polling_power_policy::GetSettingNew(
      "/driver/polling/not_integer_values", config.GetSnapshot());
  const auto& niv_default_behavior =
      taximeter_polling_power_policy::GetPolicyGroupValues(niv_setting);

  ASSERT_EQ(1.54, niv_default_behavior.full);
  ASSERT_EQ(2.99, niv_default_behavior.extra.at("idle"));
  ASSERT_EQ(std::nullopt, niv_setting.jitter_in_percent);

  const auto& ani_setting = taximeter_polling_power_policy::GetSettingNew(
      "/driver/polling/all_not_integer", config.GetSnapshot());
  const auto& ani_custom_behavior =
      taximeter_polling_power_policy::GetPolicyGroupValues(ani_setting,
                                                           "custom");
  const auto& ani_default_behavior =
      taximeter_polling_power_policy::GetPolicyGroupValues(ani_setting);

  ASSERT_EQ(1.54, ani_default_behavior.full);
  ASSERT_EQ(2.99, ani_default_behavior.extra.at("idle"));
  ASSERT_EQ(0.98, ani_custom_behavior.full);
  ASSERT_EQ(10.5, ani_custom_behavior.extra.at("powersaving"));
  ASSERT_EQ(1.25, ani_setting.jitter_in_percent);

  const auto& wd_setting = taximeter_polling_power_policy::GetSettingNew(
      "/driver/polling/with_disabled", config.GetSnapshot());
  const auto& wd_custom_behavior =
      taximeter_polling_power_policy::GetPolicyGroupValues(wd_setting,
                                                           "custom");
  const auto& wd_default_behavior =
      taximeter_polling_power_policy::GetPolicyGroupValues(wd_setting);

  ASSERT_EQ(1.54, wd_default_behavior.full);
  ASSERT_EQ(0, wd_default_behavior.extra.at("idle"));
  ASSERT_EQ(0.98, wd_custom_behavior.full);
  ASSERT_EQ(0, wd_custom_behavior.extra.at("powersaving"));
  ASSERT_EQ(1.25, wd_setting.jitter_in_percent);

  const auto& e_setting = taximeter_polling_power_policy::GetSettingNew(
      "/driver/polling/error", config.GetSnapshot());
  const auto& e_custom_behavior =
      taximeter_polling_power_policy::GetPolicyGroupValues(e_setting, "custom");
  const auto& e_default_behavior =
      taximeter_polling_power_policy::GetPolicyGroupValues(e_setting);

  ASSERT_EQ(600, e_default_behavior.full);
  ASSERT_EQ(600, e_custom_behavior.full);
  ASSERT_EQ(std::nullopt, e_setting.jitter_in_percent);

  const auto& d_setting = taximeter_polling_power_policy::GetSettingNew(
      "/driver/polling/__default__", config.GetSnapshot());
  const auto& d_default_behavior =
      taximeter_polling_power_policy::GetPolicyGroupValues(d_setting);

  ASSERT_EQ(600, d_default_behavior.full);
  ASSERT_EQ(std::nullopt, d_setting.jitter_in_percent);

  const auto& co_setting = taximeter_polling_power_policy::GetSettingNew(
      "common_old", config.GetSnapshot());
  const auto& co_default_behavior =
      taximeter_polling_power_policy::GetPolicyGroupValues(co_setting);

  ASSERT_EQ(1200, co_default_behavior.full);
  ASSERT_EQ(std::nullopt, co_setting.jitter_in_percent);

  const auto& cn_setting = taximeter_polling_power_policy::GetSettingNew(
      "common_new", config.GetSnapshot());
  const auto& cn_default_behavior =
      taximeter_polling_power_policy::GetPolicyGroupValues(cn_setting);

  ASSERT_EQ(1200, cn_default_behavior.full);
  ASSERT_EQ(std::nullopt, cn_setting.jitter_in_percent);
}

TEST(TaximeterManager, BuildHeaderWithZeroJitter) {
  const auto config = GetConfig();

  MockJitterImpl jitter;
  EXPECT_CALL(jitter, Get).WillRepeatedly(testing::Return(double{0}));

  const auto& uu_default_header = taximeter_polling_power_policy::GetHeaderNew(
      "/driver/polling/usual_usage", config.GetSnapshot(), jitter);
  ASSERT_NE(uu_default_header.find("full=300s"), std::string::npos);
  ASSERT_NE(uu_default_header.find("powersaving=30s"), std::string::npos);

  const auto& uu_custom_header = taximeter_polling_power_policy::GetHeaderNew(
      "/driver/polling/usual_usage", config.GetSnapshot(), jitter, "custom");
  ASSERT_NE(uu_custom_header.find("full=500s"), std::string::npos);
  ASSERT_NE(uu_custom_header.find("background=1000s"), std::string::npos);

  const auto& od_default_header = taximeter_polling_power_policy::GetHeaderNew(
      "/driver/polling/only_default", config.GetSnapshot(), jitter);
  ASSERT_NE(od_default_header.find("full=300s"), std::string::npos);
  ASSERT_NE(od_default_header.find("idle=30s"), std::string::npos);

  const auto& niv_default_header = taximeter_polling_power_policy::GetHeaderNew(
      "/driver/polling/not_integer_values", config.GetSnapshot(), jitter);
  ASSERT_NE(niv_default_header.find("full=1.54s"), std::string::npos);
  ASSERT_NE(niv_default_header.find("idle=2.99s"), std::string::npos);

  const auto& nij_default_header = taximeter_polling_power_policy::GetHeaderNew(
      "/driver/polling/not_integer_jitter", config.GetSnapshot(), jitter);
  ASSERT_NE(nij_default_header.find("full=300s"), std::string::npos);
  ASSERT_NE(nij_default_header.find("idle=30s"), std::string::npos);

  const auto& bj_default_header = taximeter_polling_power_policy::GetHeaderNew(
      "/driver/polling/big_jitter", config.GetSnapshot(), jitter);
  ASSERT_NE(bj_default_header.find("full=300s"), std::string::npos);
  ASSERT_NE(bj_default_header.find("idle=30s"), std::string::npos);

  const auto& ali_default_header = taximeter_polling_power_policy::GetHeaderNew(
      "/driver/polling/all_not_integer", config.GetSnapshot(), jitter);
  ASSERT_NE(ali_default_header.find("full=1.54s"), std::string::npos);
  ASSERT_NE(ali_default_header.find("idle=2.99s"), std::string::npos);

  const auto& ali_custom_header = taximeter_polling_power_policy::GetHeaderNew(
      "/driver/polling/all_not_integer", config.GetSnapshot(), jitter,
      "custom");
  ASSERT_NE(ali_custom_header.find("full=0.98s"), std::string::npos);
  ASSERT_NE(ali_custom_header.find("powersaving=10.5s"), std::string::npos);

  const auto& d_default_header = taximeter_polling_power_policy::GetHeaderNew(
      "/driver/polling/__default__", config.GetSnapshot(), jitter);
  ASSERT_NE(d_default_header.find("full=600s"), std::string::npos);

  const auto& d_custom_header = taximeter_polling_power_policy::GetHeaderNew(
      "/driver/polling/__default__", config.GetSnapshot(), jitter, "custom");
  ASSERT_NE(d_custom_header.find("full=600s"), std::string::npos);

  const auto& co_default_header = taximeter_polling_power_policy::GetHeaderNew(
      "common_old", config.GetSnapshot(), jitter);
  ASSERT_NE(co_default_header.find("full=1200s"), std::string::npos);

  const auto& co_custom_header = taximeter_polling_power_policy::GetHeaderNew(
      "common_old", config.GetSnapshot(), jitter, "custom");
  ASSERT_NE(co_custom_header.find("full=1000s"), std::string::npos);

  const auto& cn_default_header = taximeter_polling_power_policy::GetHeaderNew(
      "common_new", config.GetSnapshot(), jitter);
  ASSERT_NE(cn_default_header.find("full=1200s"), std::string::npos);

  const auto& cn_custom_header = taximeter_polling_power_policy::GetHeaderNew(
      "common_new", config.GetSnapshot(), jitter, "custom");
  ASSERT_NE(cn_custom_header.find("full=1000s"), std::string::npos);
}

TEST(TaximeterManager, BuildHeaderWithNonZeroJitter) {
  const auto config = GetConfig();

  MockJitterImpl jitter;
  EXPECT_CALL(jitter, Get).WillRepeatedly(testing::Return(double{-0.02}));

  const auto& uu_default_header = taximeter_polling_power_policy::GetHeaderNew(
      "/driver/polling/usual_usage", config.GetSnapshot(), jitter);
  ASSERT_NE(uu_default_header.find("full=294s"), std::string::npos);
  ASSERT_NE(uu_default_header.find("powersaving=29.4s"), std::string::npos);

  const auto& uu_custom_header = taximeter_polling_power_policy::GetHeaderNew(
      "/driver/polling/usual_usage", config.GetSnapshot(), jitter, "custom");
  ASSERT_NE(uu_custom_header.find("full=490s"), std::string::npos);
  ASSERT_NE(uu_custom_header.find("background=980s"), std::string::npos);

  const auto& od_default_header = taximeter_polling_power_policy::GetHeaderNew(
      "/driver/polling/only_default", config.GetSnapshot(), jitter);
  ASSERT_NE(od_default_header.find("full=294s"), std::string::npos);
  ASSERT_NE(od_default_header.find("idle=29.4s"), std::string::npos);

  const auto& niv_default_header = taximeter_polling_power_policy::GetHeaderNew(
      "/driver/polling/not_integer_values", config.GetSnapshot(), jitter);
  ASSERT_NE(niv_default_header.find("full=1.509s"),
            std::string::npos);  // 1.5092
  ASSERT_NE(niv_default_header.find("idle=2.93s"),
            std::string::npos);  // 2.9302

  const auto& nij_default_header = taximeter_polling_power_policy::GetHeaderNew(
      "/driver/polling/not_integer_jitter", config.GetSnapshot(), jitter);
  ASSERT_NE(nij_default_header.find("full=294s"), std::string::npos);
  ASSERT_NE(nij_default_header.find("idle=29.4s"), std::string::npos);

  const auto& bj_default_header = taximeter_polling_power_policy::GetHeaderNew(
      "/driver/polling/big_jitter", config.GetSnapshot(), jitter);
  ASSERT_NE(bj_default_header.find("full=294s"), std::string::npos);
  ASSERT_NE(bj_default_header.find("idle=29.4s"), std::string::npos);

  const auto& ali_default_header = taximeter_polling_power_policy::GetHeaderNew(
      "/driver/polling/all_not_integer", config.GetSnapshot(), jitter);
  ASSERT_NE(ali_default_header.find("full=1.509s"), std::string::npos);
  ASSERT_NE(ali_default_header.find("idle=2.93s"), std::string::npos);

  const auto& ali_custom_header = taximeter_polling_power_policy::GetHeaderNew(
      "/driver/polling/all_not_integer", config.GetSnapshot(), jitter,
      "custom");
  ASSERT_NE(ali_custom_header.find("full=0.96s"), std::string::npos);  // 0.9604
  ASSERT_NE(ali_custom_header.find("powersaving=10.29s"),
            std::string::npos);  // 10.29
}

TEST(TaximeterManager, BuildHeaderDisabledWithZeroJitter) {
  const auto config = GetConfig();

  MockJitterImpl jitter;
  EXPECT_CALL(jitter, Get).WillRepeatedly(testing::Return(double{0}));

  const auto& wd_default_header = taximeter_polling_power_policy::GetHeaderNew(
      "/driver/polling/with_disabled", config.GetSnapshot(), jitter);
  ASSERT_NE(wd_default_header.find("full=1.54s"), std::string::npos);
  ASSERT_NE(wd_default_header.find("idle=disabled"), std::string::npos);

  const auto& wd_custom_header = taximeter_polling_power_policy::GetHeaderNew(
      "/driver/polling/with_disabled", config.GetSnapshot(), jitter, "custom");
  ASSERT_NE(wd_custom_header.find("full=0.98s"), std::string::npos);
  ASSERT_NE(wd_custom_header.find("powersaving=disabled"), std::string::npos);
}

TEST(TaximeterManager, BuildHeaderDisabledWithNonZeroJitter) {
  const auto config = GetConfig();

  MockJitterImpl jitter;
  EXPECT_CALL(jitter, Get).WillRepeatedly(testing::Return(double{0.23}));

  const auto& wd_default_header = taximeter_polling_power_policy::GetHeaderNew(
      "/driver/polling/with_disabled", config.GetSnapshot(), jitter);
  ASSERT_NE(wd_default_header.find("full=1.894s"),
            std::string::npos);  // 1.23*1.54=1.8942
  ASSERT_NE(wd_default_header.find("idle=disabled"), std::string::npos);

  const auto& wd_custom_header = taximeter_polling_power_policy::GetHeaderNew(
      "/driver/polling/with_disabled", config.GetSnapshot(), jitter, "custom");
  ASSERT_NE(wd_custom_header.find("full=1.205s"),
            std::string::npos);  // 0.98*1.23=1.2054
  ASSERT_NE(wd_custom_header.find("powersaving=disabled"), std::string::npos);
}

TEST(TaximeterSwitcher, BuildOldHeader) {
  const auto config = GetConfig();

  const auto& co_default_header = taximeter_polling_power_policy::GetHeader(
      "common_old", config.GetSnapshot());
  ASSERT_NE(co_default_header.find("full=300s"), std::string::npos);

  const auto& st_default_header = taximeter_polling_power_policy::GetHeader(
      "/driver/polling/state", config.GetSnapshot());
  ASSERT_NE(st_default_header.find("full=300s"), std::string::npos);

  const auto& sh_default_header = taximeter_polling_power_policy::GetHeader(
      "/driver/polling/shate", config.GetSnapshot());
  ASSERT_NE(sh_default_header.find("full=600s"), std::string::npos);
  ASSERT_NE(sh_default_header.find("background=1200s"), std::string::npos);
  ASSERT_NE(sh_default_header.find("powersaving=1200s"), std::string::npos);
  ASSERT_NE(sh_default_header.find("idle=1800s"), std::string::npos);

  const auto& sh_custom_header = taximeter_polling_power_policy::GetHeader(
      "/driver/polling/shate", config.GetSnapshot(), "custom");
  ASSERT_NE(sh_custom_header.find("full=600s"), std::string::npos);
  ASSERT_NE(sh_custom_header.find("background=1200s"), std::string::npos);
  ASSERT_NE(sh_custom_header.find("powersaving=1200s"), std::string::npos);
  ASSERT_NE(sh_custom_header.find("idle=1800s"), std::string::npos);
}

TEST(TaximeterSwitcher, BuildNewHeader) {
  const auto config = GetConfig();

  const auto& cn_default_header = taximeter_polling_power_policy::GetHeader(
      "common_new", config.GetSnapshot());
  ASSERT_NE(cn_default_header.find("full=1200s"), std::string::npos);

  const auto& cn_custom_header = taximeter_polling_power_policy::GetHeader(
      "common_new", config.GetSnapshot(), "custom");
  ASSERT_NE(cn_custom_header.find("full=1000s"), std::string::npos);
}

}  // namespace
