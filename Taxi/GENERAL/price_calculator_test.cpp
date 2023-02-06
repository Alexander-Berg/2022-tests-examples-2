#include <userver/utest/utest.hpp>

#include "price_calculator.hpp"

#include <userver/formats/json/serialize_container.hpp>

namespace cargo_pricing {

namespace {

// -- Пример1 определения Калькулятора цены --

// Структура с раcсчитываемой ценой
// в качестве данных стоимости - строка - для наглядности тестов
struct Price {
  std::string data;
};

// Структура со всеми входными параметрами расчета
struct InputParams {
  int int_data;
  std::string data;
};

// Функция для дампа части структуры цены на каждом этапе
formats::json::Value DumpCalcPriceStage(const Price& p) {
  auto builder = formats::json::ValueBuilder{};
  builder["price"] = p.data;
  return builder.ExtractValue();
}

// Много функций преобразований цены (некоторые имеют несколько версий)
Price TransformA_V1(Price price, const InputParams& input) {
  return {price.data + "TrA1" + input.data};
}

Price TransformB_V0(Price price, const InputParams& input) {
  return {price.data + "TrB0" + input.data};
}

Price TransformB_V1(Price price, const InputParams& input) {
  return {price.data + "TrB1" + input.data};
}

Price TransformB_V2(Price price, const InputParams& input) {
  return {price.data + "TrB2" + input.data};
}

Price TransformB_V3(Price price, const InputParams& input) {
  return {price.data + "TrB3" + input.data};
}

Price TransformC_V1(Price price, const InputParams& input) {
  return {price.data + "TrC1" + input.data};
}

Price TransformD_V1(Price price, const InputParams& input) {
  return {price.data + "TrD1" + input.data};
}

Price TransformD_V2(Price price, const InputParams& input) {
  return {price.data + "TrD2" + input.data};
}

Price TransformOld_V1(Price price, const InputParams& input) {
  return {price.data + "TrOld1" + input.data};
}

// целевой класс калькулятора
class Calc : public price_calc::PriceCalculator<InputParams, Price> {
 protected:
  std::vector<TransformVariants> MakeTransformList() const final {
    // задаем список преобразований цены
    // каждая группа - это одно преобразование
    // и внутри нее мы можем задавать версии
    // Состав преобразований, порядок и версии
    // при расчете будут определяться планом
    return {{"TransformA", {{TransformA_V1, 1}}},
            {"TransformB",
             {{TransformB_V1, 1},
              {TransformB_V0, 0},
              {TransformB_V2, 2},
              {TransformB_V3, 3}}},
            {"TransformC", {{TransformC_V1, 1}}},
            {"TransformOld", {{TransformOld_V1, 1}}},
            {"TransformD", {{TransformD_V1, 1}, {TransformD_V2, 2}}}};
  }
};

// -- Пример2 определения Калькулятора цены с выделенным начальным расчетом --

// Функции расчет начальной цены (две версии)
Price InitCalc_V1(const InputParams&) { return {"InitV1 "}; }

Price InitCalc_V2(const InputParams& input) {
  return {"InitV2_" + std::to_string(input.int_data) + " "};
}

// целевой класс калькулятора
class Calc_WithInitCalc
    : public price_calc::PriceCalculator_WithInitCalc<InputParams, Price> {
 protected:
  InitCalcVariants MakeInitCalc() const final {
    // задаем версии базового расчета
    return {{{InitCalc_V2, 2}, {InitCalc_V1, 1}}};
  }
  std::vector<TransformVariants> MakeTransformList() const final {
    return {{"TransformA", {{TransformA_V1, 1}}},
            {"TransformB",
             {{TransformB_V1, 1},
              {TransformB_V2, 2},
              {TransformB_V0, 0},
              {TransformB_V3, 3}}},
            {"TransformC", {{TransformC_V1, 1}}},
            {"TransformD", {{TransformD_V1, 1}, {TransformD_V2, 2}}}};
  }
};

// -- Конец примера --

using ExpectedStagesDump = std::vector<std::pair<std::string, std::string>>;
bool IsEqual(price_calc::CalculationStagesDump const& e1,
             ExpectedStagesDump const& e2) {
  if (e1.size() != e2.size()) {
    return false;
  }
  for (std::size_t i = 0; i < e1.size(); ++i) {
    if (e1[i].stage_name != e2[i].first) {
      return false;
    }
    if (e1[i].dump.extra["price"].As<std::string>() != e2[i].second) {
      return false;
    }
  }
  return true;
}

TEST(CargoPriceCalculator, BaseUsageCase) {
  const auto in_plan = price_calc::CalculationPlan{
      {"TransformA", 1},
      {"TransformB", 3},
      {"TransformC", 1},
      {"TransformD", 2},
  };
  const auto calc = Calc{};
  const auto [price, dump] = calc.CalcPrice(in_plan, {12, "+"});
  ASSERT_EQ(price.data, "TrA1+TrB3+TrC1+TrD2+");
  const auto expected_dump = ExpectedStagesDump{
      {"TransformA", "TrA1+"},
      {"TransformB", "TrA1+TrB3+"},
      {"TransformC", "TrA1+TrB3+TrC1+"},
      {"TransformD", "TrA1+TrB3+TrC1+TrD2+"},
  };
  ASSERT_TRUE(IsEqual(dump, expected_dump));
}

TEST(CargoPriceCalculator, EmptyPlan) {
  const auto in_plan = price_calc::CalculationPlan{};
  const auto calc = Calc{};
  const auto [price, dump] = calc.CalcPrice(in_plan, {12, "+"});
  ASSERT_EQ(price.data, "");
  const auto expected_dump = ExpectedStagesDump{};
  ASSERT_TRUE(IsEqual(dump, expected_dump));
}

TEST(CargoPriceCalculator, UseOldVersionsOfTransforms) {
  const auto in_plan = price_calc::CalculationPlan{
      {"TransformA", 1},
      {"TransformB", 2},  // !
      {"TransformC", 1},
      {"TransformD", 2},
  };
  const auto calc = Calc{};
  const auto [price, _] = calc.CalcPrice(in_plan, {13, "|"});
  ASSERT_EQ(price.data, "TrA1|TrB2|TrC1|TrD2|");
}

TEST(CargoPriceCalculator, StrangeTransformationOrder) {
  const auto in_plan = price_calc::CalculationPlan{
      {"TransformB", 3}, {"TransformD", 2}, {"TransformA", 1}};
  const auto calc = Calc{};
  const auto [price, _] = calc.CalcPrice(in_plan, {1, "-"});
  ASSERT_EQ(price.data, "TrB3-TrD2-TrA1-");
}

TEST(CargoPriceCalculator, WrongTransformVersion_Exception) {
  const auto in_plan = price_calc::CalculationPlan{{"TransformA", 1},
                                                   {"TransformB", 5},  //!
                                                   {"TransformC", 1}};
  const auto calc = Calc{};
  try {
    const auto _ = calc.CalcPrice(in_plan, {1, "-"});
  } catch (const price_calc::CalcPriceError& e) {
    ASSERT_STREQ(e.what(), "no price calculator 'TransformB' with version=5");
    return;
  }
  ADD_FAILURE();
}

TEST(CargoPriceCalculator, WrongTransformName_Exception) {
  const auto in_plan = price_calc::CalculationPlan{
      {"TransformA", 1}, {"TransformWrong", 1}, {"TransformC", 1}};
  const auto calc = Calc{};
  try {
    const auto _ = calc.CalcPrice(in_plan, {1, "-"});
  } catch (const price_calc::CalcPriceError& e) {
    ASSERT_STREQ(e.what(),
                 "no price transformation with name 'TransformWrong'");
    return;
  }
  ADD_FAILURE();
}

TEST(CargoPriceCalculator_WithInitCalc, BaseUsageCase) {
  const auto in_plan = price_calc::CalculationPlan{
      {"BasePrice", 2},  {"TransformA", 1}, {"TransformB", 3},
      {"TransformC", 1}, {"TransformD", 2},
  };
  const auto calc = Calc_WithInitCalc{};
  const auto [price, dump] = calc.CalcPrice(in_plan, {12, "+"});
  ASSERT_EQ(price.data, "InitV2_12 TrA1+TrB3+TrC1+TrD2+");
  const auto expected_dump = ExpectedStagesDump{
      {"BasePrice", "InitV2_12 "},
      {"TransformA", "InitV2_12 TrA1+"},
      {"TransformB", "InitV2_12 TrA1+TrB3+"},
      {"TransformC", "InitV2_12 TrA1+TrB3+TrC1+"},
      {"TransformD", "InitV2_12 TrA1+TrB3+TrC1+TrD2+"},
  };
  ASSERT_TRUE(IsEqual(dump, expected_dump));
}

TEST(CargoPriceCalculator_WithInitCalc, InitCalcOnly) {
  const auto in_plan = price_calc::CalculationPlan{
      {"BasePrice", 1},
  };
  const auto calc = Calc_WithInitCalc{};
  const auto [price, dump] = calc.CalcPrice(in_plan, {12, "+"});
  ASSERT_EQ(price.data, "InitV1 ");
  const auto expected_dump = ExpectedStagesDump{{"BasePrice", "InitV1 "}};
  ASSERT_TRUE(IsEqual(dump, expected_dump));
}

TEST(CargoPriceCalculator_WithInitCalc, WrongInitCalcStageName_Exception) {
  const auto in_plan = price_calc::CalculationPlan{
      {"TransformA", 1}, {"TransformB", 1}, {"TransformC", 1}};
  const auto calc = Calc_WithInitCalc{};
  try {
    const auto _ = calc.CalcPrice(in_plan, {1, "-"});
  } catch (const price_calc::CalcPriceError& e) {
    ASSERT_STREQ(e.what(),
                 "first stage in plan has to be BasePrice not 'TransformA'");
    return;
  }
  ADD_FAILURE();
}

TEST(CargoPriceCalculator_WithInitCalc, EmptyPlan_Exception) {
  const auto in_plan = price_calc::CalculationPlan{};
  const auto calc = Calc_WithInitCalc{};
  try {
    const auto _ = calc.CalcPrice(in_plan, {1, "-"});
  } catch (const price_calc::CalcPriceError& e) {
    ASSERT_STREQ(
        e.what(),
        "calculation plan can't be empty. Initial price calculation has to "
        "be exists");
    return;
  }
  ADD_FAILURE();
}

}  // namespace

}  // namespace cargo_pricing
