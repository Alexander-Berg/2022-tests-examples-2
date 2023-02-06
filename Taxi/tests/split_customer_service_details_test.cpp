#include <gtest/gtest.h>

#include "helpers/uniform_discount.hpp"

TEST(ApplyV2, ErrorBYN) {
  //баг https://st.yandex-team.ru/EDAORDERS-6889
  //ждем изменения продуктовых требований
  models::Decimal q{1};

  std::vector<helpers::uniform_discount::Item> items_to_split{
      {"item-tvistery_tvister_ostryj-0", models::Decimal{"6.35"}, q,
       models::CustomerServiceType::kCompositionProducts, false},
      {"item-tvistery_tvister_ostryj-1", models::Decimal{"6.35"}, q,
       models::CustomerServiceType::kCompositionProducts, false},
      {"item-kurica_bajtsy_bolshie-0", models::Decimal{"7.72"}, q,
       models::CustomerServiceType::kCompositionProducts, false},
      {"item-garniry_basket_fri-0", models::Decimal{"4.45"}, q,
       models::CustomerServiceType::kCompositionProducts, false},
      {"item-sous_sous_chesnochnyj-0", models::Decimal{"0.74"}, q,
       models::CustomerServiceType::kCompositionProducts, false},
      {"item-goryachie_napitki_kapuchino_bolshoj-0", models::Decimal{"4"}, q,
       models::CustomerServiceType::kCompositionProducts, false}};

  models::Decimal amount_to_split{"26.6"};
  helpers::uniform_discount::Options uniform_discount_options{
      helpers::uniform_discount::Country::kRussia, false};
  helpers::uniform_discount::UniformDiscountRules rules{models::Decimal{1},
                                                        models::Decimal{1}, 0};

  auto items = helpers::uniform_discount::ApplyV2(
      items_to_split, amount_to_split, uniform_discount_options, rules);

  ASSERT_TRUE(!items);
}
