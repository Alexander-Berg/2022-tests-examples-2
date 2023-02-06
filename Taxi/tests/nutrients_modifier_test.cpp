#include <gtest/gtest.h>

#include <modifiers/erms/item/nutrients_modifier.hpp>

namespace eats_restaurant_menu::modifiers::erms::item::tests {

namespace {

namespace tanker_keys = localization::keys::nutrients;

const std::string kDefaultTemplate =
    R"(NUTRIENTS: C {calories}, P {proteins}, F {fats}, C {carbohydrates})";

const std::unordered_map<localization::TankerKey, std::string> kMockLocalization{
    {tanker_keys::kNutrientsProteins, "белк"},
    {tanker_keys::kNutrientsFats, "жир"},
    {tanker_keys::kNutrientsCarbohydrates, "углевод"},
    {tanker_keys::kNutrients, "кбжу"},
    {tanker_keys::kNutrientsCaloriesUnit, "ккал"},
    {tanker_keys::kNutrientsUnit, "г"},
    {tanker_keys::kNutrientsFormatLine,
     R"(NUTRIENTS: C {calories}, P {proteins}, F {fats}, C {carbohydrates})"}};

NutrientsModifier MakeModifier(
    const bool enabled = false,
    const std::string& template_ = kDefaultTemplate) {
  NutrientsModifier::Settings settings{};
  settings.enabled = enabled;
  settings.template_ = template_;
  return NutrientsModifier{settings,
                           localization::MakeTestLocalizer(kMockLocalization)};
}

clients::eats_rest_menu_storage::Item MakeErmsItem() {
  clients::eats_rest_menu_storage::Item item{};
  item.nutrients = clients::eats_rest_menu_storage::ItemNutrients{
      decimal64::Decimal<2>{1},  // calories
      decimal64::Decimal<2>{2},  // proteins
      decimal64::Decimal<2>{3},  // fats
      decimal64::Decimal<2>{4},  // carbohydrates
  };
  return item;
}

struct TestCase {
  std::string name;
  std::optional<std::string> description{std::nullopt};
  bool enabled{false};
  std::string template_ = kDefaultTemplate;
  std::string expected_description;
};

class NutrientsModifierTest : public ::testing::TestWithParam<TestCase> {};

}  // namespace

TEST_P(NutrientsModifierTest, NutrientsModifier) {
  ::handlers::ItemResponse item{};

  auto params = GetParam();
  item.description = params.description;
  const auto erms_item = MakeErmsItem();

  const auto modifier = MakeModifier(params.enabled, params.template_);
  modifier.Modify(item, erms_item);

  ASSERT_EQ(item.description.value(), params.expected_description);
}

INSTANTIATE_TEST_SUITE_P(
    /**/, NutrientsModifierTest,
    ::testing::Values(
        TestCase{
            "generic",                                        // name
            "Description",                                    // description
            true,                                             // enabled
            kDefaultTemplate,                                 // template_
            "Description.<br>NUTRIENTS: C 1, P 2, F 3, C 4",  // expected_description
        },
        TestCase{
            "disabled",        // name
            "Description",     // description
            false,             // enabled
            kDefaultTemplate,  // template_
            "Description",     // expected_description
        },
        TestCase{
            "already_has_nutrients",  // name
            "Description кбжу",       // description
            true,                     // enabled
            kDefaultTemplate,         // template_
            "Description кбжу",       // expected_description
        },
        TestCase{
            "null_description",               // name
            std::nullopt,                     // description
            true,                             // enabled
            kDefaultTemplate,                 // template_
            "NUTRIENTS: C 1, P 2, F 3, C 4",  // expected_description
        },
        TestCase{
            "empty_description",              // name
            "",                               // description
            true,                             // enabled
            kDefaultTemplate,                 // template_
            "NUTRIENTS: C 1, P 2, F 3, C 4",  // expected_description
        },
        // не учитываем то что пришло из template_, так как в коде заведен
        // танкерный ключ
        TestCase{
            "only_callories",                 // name
            "",                               // description
            true,                             // enabled
            "Calories {calories}",            // template_
            "NUTRIENTS: C 1, P 2, F 3, C 4",  // expected_description
        }),
    [](const auto& v) { return v.param.name; });

}  // namespace eats_restaurant_menu::modifiers::erms::item::tests
