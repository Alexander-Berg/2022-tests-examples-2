#include <vector>

#include <gtest/gtest.h>

#include <tariff-classes/class_type.hpp>
#include <tariff-classes/classes.hpp>
#include <tariff-classes/classes_mapper.hpp>

/**
 * @details String construction tested in ClassesMapper.
 */
TEST(Classes, Constructors) {
  using tariff_classes::Classes;
  using tariff_classes::ClassType;

  auto cs = Classes();
  ASSERT_EQ(cs.Count(), 0);
  ASSERT_FALSE(cs.IsMultiClass());
  ASSERT_TRUE(cs.Empty());

  cs = {ClassType::Business};
  ASSERT_EQ(cs.Count(), 1);
  ASSERT_FALSE(cs.Empty());
  ASSERT_FALSE(cs.IsMultiClass());
  ASSERT_TRUE(cs.Provides(ClassType::Business));

  std::vector<ClassType> ctv{ClassType::Business, ClassType::Vip};
  cs = Classes(ctv);
  ASSERT_EQ(cs.Count(), 2);
  ASSERT_EQ(cs.GetFirstActive(), ClassType::Business);
  ASSERT_FALSE(cs.Empty());
  ASSERT_TRUE(cs.IsMultiClass());
  ASSERT_TRUE(cs.Provides(ClassType::Business) && cs.Provides(ClassType::Vip));
}

TEST(Classes, Operators) {
  using tariff_classes::Classes;
  using tariff_classes::ClassType;

  auto cs_alpha = Classes({ClassType::Business});
  auto cs_beta = cs_alpha;
  ASSERT_TRUE(cs_alpha == cs_beta);

  cs_beta = {ClassType::Vip};
  ASSERT_TRUE(cs_alpha != cs_beta);

  ASSERT_FALSE((~cs_alpha).Provides(ClassType::Business));
  ASSERT_FALSE(
      (cs_alpha & cs_beta).Provides({ClassType::Business, ClassType::Vip}));
  ASSERT_TRUE(
      (cs_alpha | cs_beta).Provides({ClassType::Business, ClassType::Vip}));
  ASSERT_FALSE(
      (cs_alpha - Classes{ClassType::Business}).Provides(ClassType::Business));

  cs_alpha |= cs_beta;
  ASSERT_TRUE(cs_alpha.Count() == 2 &&
              cs_alpha.Provides({ClassType::Business, ClassType::Vip}));

  cs_alpha &= cs_beta;
  ASSERT_TRUE(cs_alpha.Count() == 1 && cs_alpha.Provides(ClassType::Vip));

  ASSERT_TRUE(bool(cs_alpha));
  ASSERT_FALSE(bool(cs_alpha - cs_beta));
}

TEST(Classes, Add) {
  using tariff_classes::Classes;
  using tariff_classes::ClassType;

  static const char* const kCargo = "cargo";

  auto cs = Classes({ClassType::Business});
  cs.Add(ClassType::Business2);
  ASSERT_TRUE(cs.Provides(ClassType::Business2));

  cs.Add(kCargo);
  ASSERT_TRUE(cs.Provides(ClassType::Cargo));

  cs.Add(Classes({ClassType::ChildTariff, ClassType::DemoStand}));
  ASSERT_TRUE(cs.Provides({ClassType::ChildTariff, ClassType::DemoStand}));
}

TEST(Classes, Remove) {
  using tariff_classes::Classes;
  using tariff_classes::ClassType;

  static const char* const kEconom = "econom";

  auto cs = Classes({ClassType::Business, ClassType::Business2,
                     ClassType::Econom, ClassType::Express});
  ASSERT_TRUE(cs.Provides(
      Classes({ClassType::Business, ClassType::Business2, ClassType::Econom})));

  cs.Remove(ClassType::Business2);
  ASSERT_TRUE(cs.Provides(
      {ClassType::Business, ClassType::Econom, ClassType::Express}));
  ASSERT_FALSE(cs.Provides(ClassType::Business2));

  cs.Remove(kEconom);
  ASSERT_FALSE(cs.Provides(ClassType::Econom));

  cs.Remove(Classes{ClassType::Business, ClassType::Express});
  ASSERT_TRUE(cs.Empty());
}

TEST(Classes, Provides) {
  using tariff_classes::Classes;
  using tariff_classes::ClassType;

  auto cs = Classes{};
  ASSERT_FALSE(cs.Provides(ClassType::Business));

  cs.Add(ClassType::Business);
  ASSERT_TRUE(cs.Provides(ClassType::Business));

  ASSERT_TRUE(cs.Provides({ClassType::Business, ClassType::Business2}));
  cs.Add(ClassType::Business2);
  ASSERT_TRUE(cs.Provides({ClassType::Business, ClassType::Business2}));
}

TEST(Classes, Empty) {
  using tariff_classes::Classes;
  using tariff_classes::ClassType;

  auto cs = Classes{};
  ASSERT_TRUE(cs.Empty());

  cs.Add(ClassType::Business);
  ASSERT_FALSE(cs.Empty());
}

TEST(Classes, IsMultiClass) {
  using tariff_classes::Classes;
  using tariff_classes::ClassType;

  auto cs = Classes{ClassType::Business};
  ASSERT_FALSE(cs.IsMultiClass());
  cs.Add(ClassType::Business2);
  ASSERT_TRUE(cs.IsMultiClass());
}

TEST(Classes, Count) {
  using tariff_classes::Classes;
  using tariff_classes::ClassType;

  auto cs = Classes{};
  ASSERT_EQ(cs.Count(), 0);

  cs.Add(ClassType::Business);
  ASSERT_EQ(cs.Count(), 1);

  cs.Remove(ClassType::Business);
  ASSERT_EQ(cs.Count(), 0);
}

TEST(Classes, GetFirstActive) {
  using tariff_classes::Classes;
  using tariff_classes::ClassType;

  auto cs = Classes{};
  ASSERT_EQ(cs.GetFirstActive(), ClassType::Unknown);

  cs.Add(ClassType::Business);
  ASSERT_EQ(cs.GetFirstActive(), ClassType::Business);
}

TEST(Classes, GetTypes) {
  using tariff_classes::Classes;
  using tariff_classes::ClassType;

  auto cs = Classes{};
  auto csv = cs.GetTypes();
  ASSERT_TRUE(csv.empty());

  cs.Add(ClassType::Business);
  csv = cs.GetTypes();
  ASSERT_EQ(csv.size(), 1);
  ASSERT_EQ(csv.front(), ClassType::Business);

  cs.Add(ClassType::Vip);
  csv = cs.GetTypes();
  ASSERT_EQ(csv.size(), 2);
  ASSERT_EQ(csv.back(), ClassType::Vip);
}

TEST(Classes, GetNames) {
  using tariff_classes::Classes;
  using tariff_classes::ClassType;

  static const char* const kBusiness = "business";
  static const char* const kVip = "vip";

  auto cs = Classes{};
  auto csv = cs.GetNames();
  ASSERT_TRUE(csv.empty());

  cs.Add(ClassType::Business);
  csv = cs.GetNames();
  ASSERT_EQ(csv.size(), 1);
  ASSERT_EQ(csv.front(), std::string(kBusiness));

  cs.Add(ClassType::Vip);
  csv = cs.GetNames();
  ASSERT_EQ(csv.size(), 2);
  ASSERT_EQ(csv.back(), std::string(kVip));
}
