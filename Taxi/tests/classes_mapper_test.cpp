#include <limits>

#include <gtest/gtest.h>

#include <tariff-classes/class_type.hpp>
#include <tariff-classes/classes.hpp>
#include <tariff-classes/classes_mapper.hpp>

namespace {

const char* const kBusiness = "business";
const char* const kBusiness2 = "business2";
const char* const kCargo = "cargo";
const char* const kCargoCorp = "cargocorp";
const char* const kChildTariff = "child_tariff";
const char* const kComfortPlus = "comfortplus";
const char* const kDemoStand = "demostand";
const char* const kDrive = "drive";
const char* const kEconom = "econom";
const char* const kEda = "eda";
const char* const kExpress = "express";
const char* const kKids = "kids";
const char* const kMaybach = "maybach";
const char* const kMinivan = "minivan";
const char* const kMkk = "mkk";
const char* const kMkkAntifraud = "mkk_antifraud";
const char* const kNdd = "ndd";
const char* const kNight = "night";
const char* const kPersonalDriver = "personal_driver";
const char* const kPool = "pool";
const char* const kPoputkaPromo = "poputka";
const char* const kPremiumSuv = "premium_suv";
const char* const kPremiumVan = "premium_van";
const char* const kPromo = "promo";
const char* const kSdd = "sdd";
const char* const kSelfDriving = "selfdriving";
const char* const kShuttle = "shuttle";
const char* const kStandart = "standart";
const char* const kStart = "start";
const char* const kSuv = "suv";
const char* const kUberBlack = "uberblack";
const char* const kUberKids = "uberkids";
const char* const kUberLux = "uberlux";
const char* const kUberSelect = "uberselect";
const char* const kUberSelectPlus = "uberselectplus";
const char* const kUberStart = "uberstart";
const char* const kUberVan = "ubervan";
const char* const kUberX = "uberx";
const char* const kUbernight = "ubernight";
const char* const kUltimate = "ultimate";
const char* const kUniversal = "universal";
const char* const kScooters = "scooters";
const char* const kUnknown = "";
const char* const kVip = "vip";

const char* const kRandomNonExisting = "random_non_existing";

}  // namespace

TEST(ClassesMapper, Validate) {
  using tariff_classes::Classes;
  using tariff_classes::ClassType;
  using tariff_classes::ClassesMapper::Validate;

  ClassType ct = ClassType::Business;
  ASSERT_EQ(ct, Validate(ct));

  ct = ClassType::Vip;
  ASSERT_EQ(ct, Validate(ct));

  ct = static_cast<ClassType>(Classes::kCount);
  ASSERT_EQ(ClassType::Unknown, Validate(ct));

  ct = std::numeric_limits<ClassType>::max();
  ASSERT_EQ(ClassType::Unknown, Validate(ct));
}

TEST(ClassesMapper, GetClassType) {
  using tariff_classes::Classes;
  using tariff_classes::ClassType;
  using tariff_classes::ClassesMapper::GetClassType;

  auto ct = GetClassType(kBusiness);
  ASSERT_EQ(ct, ClassType::Business);

  ct = GetClassType(kBusiness2);
  ASSERT_EQ(ct, ClassType::Business2);

  ct = GetClassType(kCargo);
  ASSERT_EQ(ct, ClassType::Cargo);

  ct = GetClassType(kCargoCorp);
  ASSERT_EQ(ct, ClassType::CargoCorp);

  ct = GetClassType(kChildTariff);
  ASSERT_EQ(ct, ClassType::ChildTariff);

  ct = GetClassType(kComfortPlus);
  ASSERT_EQ(ct, ClassType::ComfortPlus);

  ct = GetClassType(kDemoStand);
  ASSERT_EQ(ct, ClassType::DemoStand);

  ct = GetClassType(kDrive);
  ASSERT_EQ(ct, ClassType::Drive);

  ct = GetClassType(kEconom);
  ASSERT_EQ(ct, ClassType::Econom);

  ct = GetClassType(kEda);
  ASSERT_EQ(ct, ClassType::Eda);

  ct = GetClassType(kExpress);
  ASSERT_EQ(ct, ClassType::Express);

  ct = GetClassType(kKids);
  ASSERT_EQ(ct, ClassType::Kids);

  ct = GetClassType(kMaybach);
  ASSERT_EQ(ct, ClassType::Maybach);

  ct = GetClassType(kMinivan);
  ASSERT_EQ(ct, ClassType::Minivan);

  ct = GetClassType(kMkk);
  ASSERT_EQ(ct, ClassType::Mkk);

  ct = GetClassType(kMkkAntifraud);
  ASSERT_EQ(ct, ClassType::MkkAntifraud);

  ct = GetClassType(kNdd);
  ASSERT_EQ(ct, ClassType::Ndd);

  ct = GetClassType(kNight);
  ASSERT_EQ(ct, ClassType::Night);

  ct = GetClassType(kPersonalDriver);
  ASSERT_EQ(ct, ClassType::PersonalDriver);

  ct = GetClassType(kPool);
  ASSERT_EQ(ct, ClassType::Pool);

  ct = GetClassType(kPoputkaPromo);
  ASSERT_EQ(ct, ClassType::PoputkaPromo);

  ct = GetClassType(kPremiumSuv);
  ASSERT_EQ(ct, ClassType::PremiumSuv);

  ct = GetClassType(kPremiumVan);
  ASSERT_EQ(ct, ClassType::PremiumVan);

  ct = GetClassType(kPromo);
  ASSERT_EQ(ct, ClassType::Promo);

  ct = GetClassType(kScooters);
  ASSERT_EQ(ct, ClassType::Scooters);

  ct = GetClassType(kSdd);
  ASSERT_EQ(ct, ClassType::Sdd);

  ct = GetClassType(kSelfDriving);
  ASSERT_EQ(ct, ClassType::SelfDriving);

  ct = GetClassType(kShuttle);
  ASSERT_EQ(ct, ClassType::Shuttle);

  ct = GetClassType(kStandart);
  ASSERT_EQ(ct, ClassType::Standart);

  ct = GetClassType(kStart);
  ASSERT_EQ(ct, ClassType::Start);

  ct = GetClassType(kSuv);
  ASSERT_EQ(ct, ClassType::Suv);

  ct = GetClassType(kUberBlack);
  ASSERT_EQ(ct, ClassType::UberBlack);

  ct = GetClassType(kUberKids);
  ASSERT_EQ(ct, ClassType::UberKids);

  ct = GetClassType(kUberLux);
  ASSERT_EQ(ct, ClassType::UberLux);

  ct = GetClassType(kUberSelect);
  ASSERT_EQ(ct, ClassType::UberSelect);

  ct = GetClassType(kUberSelectPlus);
  ASSERT_EQ(ct, ClassType::UberSelectPlus);

  ct = GetClassType(kUberStart);
  ASSERT_EQ(ct, ClassType::UberStart);

  ct = GetClassType(kUberVan);
  ASSERT_EQ(ct, ClassType::UberVan);

  ct = GetClassType(kUberX);
  ASSERT_EQ(ct, ClassType::UberX);

  ct = GetClassType(kUbernight);
  ASSERT_EQ(ct, ClassType::Ubernight);

  ct = GetClassType(kUltimate);
  ASSERT_EQ(ct, ClassType::Ultimate);

  ct = GetClassType(kUniversal);
  ASSERT_EQ(ct, ClassType::Universal);

  ct = GetClassType(kUnknown);
  ASSERT_EQ(ct, ClassType::Unknown);

  ct = GetClassType(kVip);
  ASSERT_EQ(ct, ClassType::Vip);

  ct = GetClassType(kRandomNonExisting);
  ASSERT_EQ(ct, ClassType::Unknown);
}

TEST(ClassesMapper, GetClassName) {
  using tariff_classes::Classes;
  using tariff_classes::ClassType;
  using tariff_classes::ClassesMapper::GetClassName;

  auto cn = GetClassName(ClassType::Business);
  ASSERT_EQ(cn, std::string(kBusiness));

  cn = GetClassName(ClassType::Vip);
  ASSERT_EQ(cn, std::string(kVip));

  cn = GetClassName(static_cast<ClassType>(Classes::kCount));
  ASSERT_EQ(cn, std::string(kUnknown));

  cn = GetClassName(std::numeric_limits<ClassType>::max());
  ASSERT_EQ(cn, std::string(kUnknown));
}
