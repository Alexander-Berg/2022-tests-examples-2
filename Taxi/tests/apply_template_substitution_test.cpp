#include <utils/apply_template_substitution.hpp>

#include <stdexcept>

#include <userver/utest/parameter_names.hpp>
#include <userver/utest/utest.hpp>

namespace grocery_l10n {

UTEST(ApplyTemplateSubstitutionTest, AsIs) {
  const std::string translation = "translation";
  auto substitution = utils::TryApplyTemplateSubstitution(
      translation, models::template_type::AsIs{});
  ASSERT_TRUE(substitution.has_value());
  EXPECT_EQ(translation, substitution.value());
}

UTEST(ApplyTemplateSubstitutionTest, SimpleTemplate) {
  const std::string string_template = "Delivery from {from} till {till}.";
  const simple_template::ArgsList args{{"from", "7:00"}, {"till", "23:00"}};
  const std::string expected = "Delivery from 7:00 till 23:00.";
  auto substitution = utils::TryApplyTemplateSubstitution(
      string_template, models::template_type::SimpleTemplate{args});
  ASSERT_TRUE(substitution.has_value());
  EXPECT_EQ(substitution.value(), expected);
}

}  // namespace grocery_l10n
