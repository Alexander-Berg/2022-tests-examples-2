#include "requirements.hpp"

#include <gtest/gtest.h>
#include <common/test_config.hpp>
#include <config/config.hpp>
#include <models/payment_types.hpp>

const std::string kDefaultZoneName = "crimea";

class CommonRequirements : public testing::Test {
 public:
  CommonRequirements()
      : requirements_(GenerateRequirements()),
        tariff_settings_dict_(GenerateTariffes()) {
    config::DocsMap docs_map = config::DocsMapForTest();
    config_.reset(new config::Config(docs_map));
    manager_.reset(new requirements::Manager(requirements_,
                                             tariff_settings_dict_, *config_));
  }

  // void SetUp() override {}
  // void TearDown() override {}
 protected:
  requirements::Descriptions requirements_;
  models::tariff_settings_dict tariff_settings_dict_;
  std::unique_ptr<config::Config> config_;
  std::unique_ptr<requirements::Manager> manager_;

 private:
  static requirements::Descriptions GenerateRequirements() {
    models::requirements::Description a;
    a.name = "a";
    a.type = models::requirements::types::Boolean;
    a.default_value = false;

    models::requirements::Description b;
    b.name = "b";
    b.type = models::requirements::types::Number;
    b.default_value = models::requirements::number_t(0);

    models::requirements::Description c;
    c.name = "c";
    c.type = models::requirements::types::String;
    c.default_value = "";

    return {a, b, c};
  }
  static models::tariff_settings_dict GenerateTariffes() {
    models::TariffSettings::Category econom;
    econom.class_type = models::Classes::Econom;
    econom.client_requirements = {"a"};
    econom.persistent_requirements = {};

    models::TariffSettings::Category comfort;
    comfort.class_type = models::Classes::Business;
    comfort.client_requirements = {"a", "b"};
    comfort.persistent_requirements = {"a"};

    models::TariffSettings::Category vip;
    vip.class_type = models::Classes::Vip;
    vip.client_requirements = {"a", "b", "c"};
    vip.persistent_requirements = {"a", "b"};

    models::TariffSettings crimea;
    crimea.zone_name = kDefaultZoneName;
    crimea.payment_options.set(models::payment_types::Cash, true);
    crimea.payment_options.set(models::payment_types::Coupon, true);

    crimea.categories = {econom, comfort, vip};

    models::tariff_settings_dict tariffs;
    tariffs[kDefaultZoneName] = crimea;
    return tariffs;
  }
};

TEST_F(CommonRequirements, GetSupported) {
  EXPECT_ANY_THROW(
      manager_->GetSupported("ukraine", {models::Classes::Econom}));

  const std::set<std::string>& reqs_econom =
      manager_->GetSupported(kDefaultZoneName, {models::Classes::Econom});
  EXPECT_TRUE(reqs_econom.count("a"));
  EXPECT_FALSE(reqs_econom.count("b"));
  EXPECT_FALSE(reqs_econom.count("c"));

  const std::set<std::string>& reqs_vip =
      manager_->GetSupported(kDefaultZoneName, {models::Classes::Vip});
  EXPECT_TRUE(reqs_vip.count("a"));
  EXPECT_TRUE(reqs_vip.count("b"));
  EXPECT_TRUE(reqs_vip.count("c"));
}
