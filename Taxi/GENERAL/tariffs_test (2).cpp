#include <string>

#include <discounts/models/error.hpp>
#include <userver/utest/utest.hpp>

#include <models/tariffs.hpp>

const auto tariffs = models::Tariffs({
    models::Tariffs::Tariff{"moscow", "ru", "Europe/Moscow", "rus", "RUB"},
    models::Tariffs::Tariff{"tomsk", "ru", "Asia/Tomsk", "rus", "RUB"},
    models::Tariffs::Tariff{"almaty", "kz", "Asia/Almaty", "kz", "KZT"},
    models::Tariffs::Tariff{"city_without_currency", "ru", "Asia/Tomsk", "rus",
                            std::nullopt},
});

TEST(Tariffs, GetCurrency_Ok) {
  ASSERT_EQ(tariffs.GetCurrency({"moscow", "tomsk"}), "RUB");
  ASSERT_EQ(tariffs.GetCurrency({"almaty"}), "KZT");
  ASSERT_EQ(tariffs.GetCurrency({"moscow", "city_without_currency"}), "RUB");
  ASSERT_EQ(tariffs.GetCurrency({"city_without_currency", "moscow"}), "RUB");
}

TEST(Tariffs, GetCurrency_TwoCurrencies) {
  ASSERT_THROW(tariffs.GetCurrency({"moscow", "almaty"}),
               discounts::models::Error);
}

TEST(Tariffs, GetCurrency_Invalid) {
  ASSERT_THROW(tariffs.GetCurrency({"invalid"}), discounts::models::Error);
}

TEST(Tariffs, GetCurrency_NotFoundCurrency) {
  ASSERT_THROW(tariffs.GetCurrency({"city_without_currency"}),
               discounts::models::Error);
}

TEST(Tariffs, GetCurrency_Empty) {
  ASSERT_THROW(tariffs.GetCurrency({}), discounts::models::Error);
}

TEST(Tariffs, GetEarliestTimezone_Ok) {
  cctz::time_zone tz;
  cctz::load_time_zone("Asia/Tomsk", &tz);
  ASSERT_EQ(tariffs.GetEarliestTimezone({"moscow", "tomsk", "almaty"}), tz);
}

TEST(Tariffs, GetEarliestTimezone_Invalid) {
  ASSERT_THROW(tariffs.GetEarliestTimezone({"invalid"}),
               discounts::models::Error);
}

TEST(Tariffs, GetEarliestTimezone_Empty) {
  ASSERT_THROW(tariffs.GetEarliestTimezone({}), discounts::models::Error);
}
