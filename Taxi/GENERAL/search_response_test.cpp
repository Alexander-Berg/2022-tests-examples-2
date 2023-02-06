#include <gtest/gtest.h>

#include "search_response.hpp"

using eats_full_text_search::models::JsonFromString;
using eats_full_text_search::models::UnEscapeStringInJson;

TEST(SearchResponseCondition, UnescapeStringInJson) {
  std::string escaped_json_str = "\\b \\f \\n \\r \\t \\/ \\' \\\" \\\\";
  std::string unescaped_json_str = "\b \f \n \r \t / \' \" \\";
  ASSERT_EQ(UnEscapeStringInJson(escaped_json_str), unescaped_json_str);

  escaped_json_str = "\\ \\u0001 \\\\u0001 \\ \x01 0x01 \\";
  unescaped_json_str = " u0001 \\u0001  \x01 0x01 ";
  ASSERT_EQ(UnEscapeStringInJson(escaped_json_str), unescaped_json_str);

  escaped_json_str = "\\";
  unescaped_json_str = "";
  ASSERT_EQ(UnEscapeStringInJson(escaped_json_str), unescaped_json_str);

  escaped_json_str = "";
  unescaped_json_str = "";
  ASSERT_EQ(UnEscapeStringInJson(escaped_json_str), unescaped_json_str);
}

/* Example SaaS response
{
  "Key": "s_parent_categories_v2",
  "Value": "[
{\\\"id\\\":21731,\\\"parent_id\\\":21607,\\\"title\\\":\\\"Газировка\\\"},
{\\\"id\\\":21607,\\\"parent_id\\\":12881,\\\"title\\\":\\\"Газировка\\\"},
{\\\"id\\\":12881,\\\"parent_id\\\":null,\\\"title\\\":\\\"Вода и напитки\\\"},
{\\\"id\\\":23756,\\\"parent_id\\\":null,\\\"title\\\":\\\"День
рождения \\\\\\\"Верного\\\\\\\"!\\\"}]"
},
{
  "Key": "s_description",
  "Value": "Хрустим багет со вкусом пикантного ростбифа\\r\\n\\r\\nНа создание
этих сухариков компанию вдохновил восхитительный французский багет в сочетании с
изысканными вкусами.\\r\\n\\r\\n●Когда хочешь сделать перерыв, открывай
Хрустим!\\r\\n●Воздушные и хрустящие\\r\\n●Тают во рту\\r\\n●Деликатный вкус
оставляет приятное послевкусие\\r\\n\\r\\nХрустим – это молодежный бренд,
который изменил представление о традиционных соленых снеках, предложив
современные сухарики различной формы с яркими вкусами."
},
*/

TEST(SearchResponseCondition, UnescapeStringInJsonRealData) {
  std::string escaped_json_str =
      "Хрустим багет со вкусом пикантного ростбифа\\r\\n\\r\\nНа создание этих "
      "сухариков компанию вдохновил восхитительный французский багет в "
      "сочетании с изысканными вкусами.\\r\\n\\r\\n●Когда хочешь сделать "
      "перерыв, открывай Хрустим!\\r\\n●Воздушные и хрустящие\\r\\n●Тают во "
      "рту\\r\\n●Деликатный вкус оставляет приятное "
      "послевкусие\\r\\n\\r\\nХрустим – это молодежный бренд, который изменил "
      "представление о традиционных соленых снеках, предложив современные "
      "сухарики различной формы с яркими вкусами.";
  std::string unescaped_json_str =
      "Хрустим багет со вкусом пикантного ростбифа\r\n\r\nНа создание этих "
      "сухариков компанию вдохновил восхитительный французский багет в "
      "сочетании с изысканными вкусами.\r\n\r\n●Когда хочешь сделать перерыв, "
      "открывай Хрустим!\r\n●Воздушные и хрустящие\r\n●Тают во "
      "рту\r\n●Деликатный вкус оставляет приятное послевкусие\r\n\r\nХрустим – "
      "это молодежный бренд, который изменил представление о традиционных "
      "соленых снеках, предложив современные сухарики различной формы с яркими "
      "вкусами.";
  ASSERT_EQ(UnEscapeStringInJson(escaped_json_str), unescaped_json_str);

  escaped_json_str = "Peg\\\\ppg-18\\\\18 Dimethicone";
  unescaped_json_str = "Peg\\ppg-18\\18 Dimethicone";
  ASSERT_EQ(UnEscapeStringInJson(escaped_json_str), unescaped_json_str);
}

TEST(SearchResponseCondition, JsonFromStringRealData) {
  std::string escaped_json_str =
      "["
      "{\\\"id\\\":21731,"
      "\\\"parent_id\\\":21607,"
      "\\\"title\\\":\\\"Газировка\\\"},"
      "{\\\"id\\\":21607,"
      "\\\"parent_id\\\":12881,"
      "\\\"title\\\":\\\"Газировка\\\"},"
      "{\\\"id\\\":12881,"
      "\\\"parent_id\\\":null,"
      "\\\"title\\\":\\\"Вода и напитки\\\"},"
      "{\\\"id\\\":23756,"
      "\\\"parent_id\\\":null,"
      "\\\"title\\\":\\\"День рождения \\\\\\\"Верного\\\\\\\"!\\\"}"
      "]";
  std::string unescaped_json_str =
      "["
      "{\"id\":21731,"
      "\"parent_id\":21607,"
      "\"title\":\"Газировка\"},"
      "{\"id\":21607,"
      "\"parent_id\":12881,"
      "\"title\":\"Газировка\"},"
      "{\"id\":12881,"
      "\"parent_id\":null,"
      "\"title\":\"Вода и напитки\"},"
      "{\"id\":23756,"
      "\"parent_id\":null,"
      "\"title\":\"День рождения \\\"Верного\\\"!\"}"
      "]";
  ASSERT_EQ(UnEscapeStringInJson(escaped_json_str), unescaped_json_str);
  ASSERT_EQ(ToString(JsonFromString(escaped_json_str)), unescaped_json_str);

  escaped_json_str = "[{\\\"title\\\":\\\"Lay\\'s\\\"}]";
  unescaped_json_str = "[{\"title\":\"Lay's\"}]";
  ASSERT_EQ(UnEscapeStringInJson(escaped_json_str), unescaped_json_str);
  ASSERT_EQ(ToString(JsonFromString(escaped_json_str)), unescaped_json_str);
}
