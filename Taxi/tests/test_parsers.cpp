#include <gtest/gtest.h>
#include <utils/parsers.hpp>

using namespace localizations_replica::parsers;

TEST(TesParsers, TestParseNonStrictPercentPlaceholders) {
  EXPECT_NO_THROW(ParseNonStrictPercentPlaceholders("hello %(map)d"));

  EXPECT_NO_THROW(ParseNonStrictPercentPlaceholders("hello%(1)d"));
  EXPECT_NO_THROW(ParseNonStrictPercentPlaceholders("%(abc)s"));
  EXPECT_NO_THROW(ParseNonStrictPercentPlaceholders("(abc)s"));
  EXPECT_NO_THROW(ParseNonStrictPercentPlaceholders(
      "two placeholders %(abc1)s : %(abc2)s"));
  EXPECT_NO_THROW(ParseNonStrictPercentPlaceholders(
      "three placeholders %(abc1)s : %(abc2)s%(abc3)s"));
  EXPECT_NO_THROW(ParseNonStrictPercentPlaceholders("placeholder %(abc1)s."));
  EXPECT_NO_THROW(
      ParseNonStrictPercentPlaceholders("placeholder .%(abc1).12s."));
  EXPECT_NO_THROW(
      ParseNonStrictPercentPlaceholders("placeholder .%(abc1)12.12s."));
  EXPECT_NO_THROW(
      ParseNonStrictPercentPlaceholders("placeholder %(abc1)0E end"));
  EXPECT_NO_THROW(
      ParseNonStrictPercentPlaceholders("%(a)d%(a)i%(a)o%(a)u%(a)x"));
  EXPECT_NO_THROW(ParseNonStrictPercentPlaceholders("placeholder %(abc1)s."));
  EXPECT_NO_THROW(ParseNonStrictPercentPlaceholders("%abc1"));
  EXPECT_NO_THROW(ParseNonStrictPercentPlaceholders("%(rating).1f"));
  EXPECT_NO_THROW(ParseNonStrictPercentPlaceholders(
      "თქვენს გარშემო ეხლა მზარდი კოეფიციენტია %(value).1f. იმისათვის, რომ "
      "სარფიანი შეკვეთა არ გამოტოვოთ, დააყენეთ სტატუსი „ხაზზე ვარ“!"));
  EXPECT_NO_THROW(ParseNonStrictPercentPlaceholders(
      "%(value).0f კმ\n%(value).0f կմ\n%(value).0f km\n%(value).0f "
      "км\n%(value).0f km\n%(value).0f km\n%(value).0f km\n%(value).0f "
      "км\n%(value).0f km\n%(value).0f km\n"));
  EXPECT_NO_THROW(ParseNonStrictPercentPlaceholders(
      "%(value).0f კმ\n%(value).0f կմ\n%(value).0f km\n%(value).0f "
      "км\n%(value).0f km\n%(value).0f km\n%(value).0f km\n%(value).0f "
      "км\n%(value).0f km\n%(value).0f km\n"));
  EXPECT_NO_THROW(ParseNonStrictPercentPlaceholders(
      "Olet viettänyt liian kauan aikaa ratissa. Meidän on lopetettava "
      "tilausten lähettäminen sinulle %(time)n kuluttua."));
  EXPECT_NO_THROW(ParseNonStrictPercentPlaceholders("%(value).3f"));

  EXPECT_THROW(ParseNonStrictPercentPlaceholders("%(mapd"),
               BadPlaceholderError);
  EXPECT_THROW(ParseNonStrictPercentPlaceholders("%(mapd)"),
               BadPlaceholderError);
  EXPECT_THROW(ParseNonStrictPercentPlaceholders("%(mapd)."),
               BadPlaceholderError);
  EXPECT_THROW(ParseNonStrictPercentPlaceholders("%(mapd).."),
               BadPlaceholderError);
  EXPECT_THROW(ParseNonStrictPercentPlaceholders("%(mapd)..."),
               BadPlaceholderError);
  EXPECT_THROW(ParseNonStrictPercentPlaceholders("parrent missed %(mapd"),
               BadPlaceholderError);
  EXPECT_THROW(ParseNonStrictPercentPlaceholders("empty %()"),
               BadPlaceholderError);
  EXPECT_THROW(ParseNonStrictPercentPlaceholders("dots .%(abc1)..s."),
               BadPlaceholderError);
  EXPECT_THROW(
      ParseNonStrictPercentPlaceholders("Москва - %(capital) %(country)s"),
      BadPlaceholderError);
  EXPECT_THROW(
      ParseNonStrictPercentPlaceholders("Москва - %(capitals %(country)s"),
      BadPlaceholderError);
  EXPECT_THROW(
      ParseNonStrictPercentPlaceholders("Москва - %(capitals)s %(country)."),
      BadPlaceholderError);
}

TEST(TestParsers, TestParseStrictPercentPlaceholders) {
  EXPECT_NO_THROW(ParseStrictPercentPlaceholders(""));
  EXPECT_NO_THROW(ParseStrictPercentPlaceholders("a b c"));
  EXPECT_NO_THROW(ParseStrictPercentPlaceholders("hello%(map)d"));
  EXPECT_NO_THROW(ParseStrictPercentPlaceholders("hello%(1)d"));
  EXPECT_NO_THROW(ParseStrictPercentPlaceholders("hello%(abc)#d"));
  EXPECT_NO_THROW(ParseStrictPercentPlaceholders("%(abc)s"));
  EXPECT_NO_THROW(ParseStrictPercentPlaceholders("(abc)s"));
  EXPECT_NO_THROW(
      ParseStrictPercentPlaceholders("two placeholders %(abc1)s : %(abc2)s"));
  EXPECT_NO_THROW(ParseStrictPercentPlaceholders(
      "three placeholders %(abc1)s : %(abc2)s%(abc3)s"));
  EXPECT_NO_THROW(ParseStrictPercentPlaceholders("placeholder %(abc1)s."));
  EXPECT_NO_THROW(ParseStrictPercentPlaceholders("placeholder .%(abc1).12s."));
  EXPECT_NO_THROW(
      ParseStrictPercentPlaceholders("placeholder .%(abc1)12.12s."));
  EXPECT_NO_THROW(
      ParseStrictPercentPlaceholders("placeholder .%(abc1) 56.12F."));
  EXPECT_NO_THROW(ParseStrictPercentPlaceholders("placeholder %(abc1)0E end"));
  EXPECT_NO_THROW(ParseStrictPercentPlaceholders(
      "%(a)d%(a)i%(a)o%(a)u%(a)x%(a)X%(a)e%(a)E%(a)f%("
      "a)F%(a)g%(a)G%(a)c%(a)r%(a)s%(a)a"));
  EXPECT_NO_THROW(
      ParseStrictPercentPlaceholders("minus - %(abc)-s plus - %(abc)+s"));
  EXPECT_NO_THROW(ParseStrictPercentPlaceholders("%abc1)"));
  EXPECT_NO_THROW(ParseStrictPercentPlaceholders("%(rating).1f"));
  EXPECT_NO_THROW(ParseStrictPercentPlaceholders(
      "თქვენს გარშემო ეხლა მზარდი კოეფიციენტია %(value).1f. იმისათვის, რომ "
      "სარფიანი შეკვეთა არ გამოტოვოთ, დააყენეთ სტატუსი „ხაზზე ვარ“!"));
  EXPECT_NO_THROW(ParseStrictPercentPlaceholders(
      "%(value).0f კმ\n%(value).0f կմ\n%(value).0f km\n%(value).0f "
      "км\n%(value).0f km\n%(value).0f km\n%(value).0f km\n%(value).0f "
      "км\n%(value).0f km\n%(value).0f km\n"));
  EXPECT_NO_THROW(ParseStrictPercentPlaceholders(
      "Olet viettänyt liian kauan aikaa ratissa. Meidän on lopetettava "
      "tilausten lähettäminen sinulle %(time)n kuluttua."));
  EXPECT_NO_THROW(ParseStrictPercentPlaceholders("%(value).3f"));
  EXPECT_NO_THROW(ParseStrictPercentPlaceholders("%(discount)s endirim"));
  EXPECT_NO_THROW(ParseStrictPercentPlaceholders(
      "Folosesc Yango. Faceți clic pe link pentru a obține o reducere de "
      "%(percent)s pentru utilizatorii noi (până la un total de %(value)s din "
      "primele dvs. %(ride_count)s călătorii, dacă plătiți cu card %(link)s"));

  EXPECT_THROW(ParseStrictPercentPlaceholders("type missed .%(abc1) 5 6.12F."),
               BadPlaceholderError);
  EXPECT_THROW(ParseStrictPercentPlaceholders("dots .%(abc1).1.2s."),
               BadPlaceholderError);
  EXPECT_THROW(ParseStrictPercentPlaceholders("parrent missed %(mapd"),
               BadPlaceholderError);
  EXPECT_THROW(ParseStrictPercentPlaceholders("empty %()"),
               BadPlaceholderError);
  EXPECT_THROW(ParseStrictPercentPlaceholders("unknown type %()z"),
               BadPlaceholderError);
  EXPECT_THROW(ParseStrictPercentPlaceholders("unknown type %()Z"),
               BadPlaceholderError);
  EXPECT_THROW(ParseStrictPercentPlaceholders("unknown precission %(a).zd"),
               BadPlaceholderError);
  EXPECT_THROW(ParseStrictPercentPlaceholders("unknown type %(a)1.1]"),
               BadPlaceholderError);
  EXPECT_THROW(ParseStrictPercentPlaceholders("unknown type %(a)1.1"),
               BadPlaceholderError);
  EXPECT_THROW(
      ParseStrictPercentPlaceholders("Москва - %(capital) %(country)s"),
      BadPlaceholderError);
  EXPECT_THROW(
      ParseStrictPercentPlaceholders("Москва - %(capitals %(country)s"),
      BadPlaceholderError);
  EXPECT_THROW(
      ParseStrictPercentPlaceholders("Москва - %(capitals)s %(country)."),
      BadPlaceholderError);
}

TEST(TestParsers, TestParseCurlyBracePlaceholders) {
  EXPECT_NO_THROW(ParseCurlyBracePlaceholders(""));
  EXPECT_NO_THROW(ParseCurlyBracePlaceholders("a b c"));
  EXPECT_NO_THROW(ParseCurlyBracePlaceholders("{0}"));
  EXPECT_NO_THROW(ParseCurlyBracePlaceholders("{0}{1}{2}{3}"));
  EXPECT_NO_THROW(ParseCurlyBracePlaceholders("Москва - {0} {1}"));
  EXPECT_NO_THROW(
      ParseCurlyBracePlaceholders("Moscow is the {0} of Great Britain"));
  EXPECT_NO_THROW(ParseCurlyBracePlaceholders(
      "В рамках данного тикета кто:{login} "
      "((https://tariff-editor.taxi.yandex-team.ru/tariffs/draft/{draft_id} "
      "создал черновик)) создания/изменения тарифа в {time}(MSK)"));
  EXPECT_NO_THROW(ParseCurlyBracePlaceholders(
      "**Категория {category_name} {category_type} {waiting_price_type}**"));
  EXPECT_NO_THROW(ParseCurlyBracePlaceholders(
      "Sürücü: {% if driver_name %}${driver_name} {% end %}{% if driver_phone "
      "%}${driver_phone}{% end %}"));
  EXPECT_NO_THROW(ParseCurlyBracePlaceholders("{% if has_driver_info %}"));
  EXPECT_NO_THROW(
      ParseCurlyBracePlaceholders("Автомобиль: {% if car_color %}${car_color} "
                                  "{% end %}${car_model} ${car_number}"));
  EXPECT_NO_THROW(ParseCurlyBracePlaceholders(
      "К сожалению, автомобиль {0} не прошёл проверку."));
  EXPECT_NO_THROW(ParseCurlyBracePlaceholders(
      "<p>Здравствуйте!<br>\n"
      " Мы нашли для вашего таксопарка нового водителя:<br> \n"
      "  {0}<br>                                            \n"
      "  Водительское удостоверение: {1}{2}.<br>            \n"
      "  Номер телефона: {3}</p>                            \n"
      "<p>{4}</p>                                           \n"
      "<p>С уважением, команда Uber</p>                     \n"
      "<p>Hello,<br>                                        \n"
      "  We found a new driver for your fleet:<br>          \n"
      "  {0}<br>                                            \n"
      "  Driver's license: {1}{2}.<br>                      \n"
      "  Phone number: {3}</p>                              \n"
      "<p>{4}</p>                                           \n"
      "<p>Best regards, Uber team</p>                       \n"));
  EXPECT_NO_THROW(ParseCurlyBracePlaceholders("{0:N1}% du tarif TVA incluse"));
  EXPECT_NO_THROW(ParseCurlyBracePlaceholders(
      "Осы телефон нөміріне {} тапсырыс берілді.Шектеуден асты."));
  EXPECT_NO_THROW(
      ParseCurlyBracePlaceholders("{completed}/{required} sifariş"));
  EXPECT_NO_THROW(
      ParseCurlyBracePlaceholders("Urgent help needed. Call user {phone!s}"));
  EXPECT_NO_THROW(ParseCurlyBracePlaceholders(
      "The taxi will arrive in {minutes:d} minutes "));
  EXPECT_NO_THROW(ParseCurlyBracePlaceholders(
      "Поздравляем, ваша компания {client_name} подключена к Яндекс.Драйву! "
      "Привязать свой аккаунт: "
      "https://business.taxi.yandex.ru/pages/user?code={code}"));

  EXPECT_THROW(ParseCurlyBracePlaceholders("Moscow is the {0 of Great Britain"),
               BadPlaceholderError);
  EXPECT_THROW(
      ParseCurlyBracePlaceholders("Moscow is the {0{1} of Great Britain"),
      BadPlaceholderError);
  EXPECT_THROW(
      ParseCurlyBracePlaceholders("Moscow is the {0}1} of Great Britain"),
      BadPlaceholderError);
  EXPECT_THROW(
      ParseCurlyBracePlaceholders("Moscow is the {0}1} of Great Britain"),
      BadPlaceholderError);
  EXPECT_THROW(ParseCurlyBracePlaceholders("Москва - 0} Великобритании"),
               BadPlaceholderError);
}
