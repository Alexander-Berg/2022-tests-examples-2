#include <userver/utest/utest.hpp>

#include <payment-method-id-parser/payment_method_id_parser.hpp>

TEST(PaymentMethodIdParser, ParseCorpCard) {
  const std::string payment_method_id = "cargocorp:123:card:456:789";

  const auto parsed_id = payment_method_id_parser::ParseId(payment_method_id);
  EXPECT_TRUE(std::holds_alternative<payment_method_id_parser::CargoCorpCard>(
      parsed_id));

  const auto& corp_card =
      std::get<payment_method_id_parser::CargoCorpCard>(parsed_id);
  EXPECT_EQ("123", corp_card.corp_client_id);
  EXPECT_EQ("456", corp_card.owner_yandex_uid);
  EXPECT_EQ("789", corp_card.cardstorage_id);
}

TEST(PaymentMethodIdParser, ParseCorpCardNoCardstorage) {
  const std::string payment_method_id = "cargocorp:123:card:456";

  const auto parsed_id = payment_method_id_parser::ParseId(payment_method_id);
  EXPECT_TRUE(std::holds_alternative<std::monostate>(parsed_id));
}

TEST(PaymentMethodIdParser, ParseUnknownMethod) {
  const std::string payment_method_id = "nal:123";

  const auto parsed_id = payment_method_id_parser::ParseId(payment_method_id);
  EXPECT_TRUE(std::holds_alternative<std::monostate>(parsed_id));
}

TEST(PaymentMethodIdParser, ParseContract) {
  const std::string payment_method_id =
      "cargocorp:123:balance:456:contract:789";

  const auto parsed_id = payment_method_id_parser::ParseId(payment_method_id);
  EXPECT_TRUE(
      std::holds_alternative<payment_method_id_parser::Contract>(parsed_id));

  const auto& contract =
      std::get<payment_method_id_parser::Contract>(parsed_id);
  EXPECT_EQ("123", contract.corp_client_id);
  EXPECT_EQ("456", contract.billing_id);
  EXPECT_EQ("789", contract.contract_id);
}
