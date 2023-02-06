#include <gmock/gmock.h>
#include <userver/utest/utest.hpp>

#include <userver/utils/datetime.hpp>

#include <models/promo_definition.hpp>

namespace eats_restapp_promo::types {
inline bool operator==(StoredData lhs, StoredData rhs) {
  return std::tie(lhs.place_ids, lhs.promo_type, lhs.status, lhs.task_id,
                  lhs.starts, lhs.ends, lhs.requirements, lhs.bonuses,
                  lhs.schedule) == std::tie(rhs.place_ids, rhs.promo_type,
                                            rhs.status, rhs.task_id, rhs.starts,
                                            rhs.ends, rhs.requirements,
                                            rhs.bonuses, rhs.schedule);
}
}  // namespace eats_restapp_promo::types

namespace eats_restapp_promo::models {

using namespace ::testing;

struct BaseFeatureMock {
  MOCK_METHOD(void, UpdateStoredData, (types::StoredDataRaw&), (const));
  MOCK_METHOD(void, UpdateDiscountData, (types::DiscountDataRaw&), (const));
  MOCK_METHOD(void, UpdateResponse, (models::PromoResponse&), (const));
};

struct TestFeature final : promo_features::Base {
  TestFeature(const BaseFeatureMock& mock) : mock_(mock) {}

  void UpdateStoredData(types::StoredDataRaw& v) const final {
    mock_.UpdateStoredData(v);
  }
  void UpdateDiscountData(types::DiscountDataRaw& v) const final {
    mock_.UpdateDiscountData(v);
  }
  void UpdateResponse(models::PromoResponse& v) const final {
    mock_.UpdateResponse(v);
  }

 private:
  const BaseFeatureMock& mock_;
};

struct PromoDefinitionTest : public Test {
  StrictMock<BaseFeatureMock> feature;
  PromoDefinition promo;

  PromoDefinitionTest() {
    promo.type = PromoType::kGift;
    promo.status = PromoStatus::kApproved;
    promo.title = "title";
    promo.description = "description";
    promo.features.emplace("first", std::make_shared<TestFeature>(feature));
    promo.features.emplace("second", std::make_shared<TestFeature>(feature));
  }

  static std::chrono::system_clock::time_point GetTimeFromString(
      const std::string& time_str) {
    return ::utils::datetime::Stringtime(
        time_str, ::utils::datetime::kDefaultTimezone, "%Y-%m-%d");
  }
};

TEST_F(PromoDefinitionTest, build_discount_data_success) {
  EXPECT_CALL(feature, UpdateDiscountData(_)).Times(2);
  promo.BuildDiscountData();
}

TEST_F(PromoDefinitionTest, build_stored_data_success) {
  const types::StoredData expected{
      {100, 200},
      PromoType::kGift,
      PromoStatus::kApproved,
      TaskId{"task"},
      GetTimeFromString("2022-02-01"),
      GetTimeFromString("2022-02-10"),
      storages::postgres::PlainJson{::formats::json::FromString(R"({
        "requirements": [
          {"key1": "value1", "key2": "value2"},
          {"key3": "value3"}
      ]})")},
      storages::postgres::PlainJson{::formats::json::FromString(R"({
        "bonuses": [{"some": "yeah"}]
      })")},
      std::nullopt};

  EXPECT_CALL(feature, UpdateStoredData(_))
      .WillOnce(Invoke([](types::StoredDataRaw& data) {
        data.place_ids.push_back(100);
        data.place_ids.push_back(200);
        data.starts_at = GetTimeFromString("2022-02-01");
        data.ends_at = GetTimeFromString("2022-02-10");
      }))
      .WillOnce(Invoke([](types::StoredDataRaw& data) {
        data.requirements_builder["requirements"].PushBack(
            ::formats::json::MakeObject("key1", "value1", "key2", "value2"));
        data.requirements_builder["requirements"].PushBack(
            ::formats::json::MakeObject("key3", "value3"));
        data.bonuses_builder["bonuses"].PushBack(
            ::formats::json::MakeObject("some", "yeah"));
      }));
  const auto result = promo.BuildStoredData(TaskId{"task"});
  ASSERT_EQ(expected, result);
}

TEST_F(PromoDefinitionTest, build_make_response_success) {
  PromoRequirement min_order_price;
  min_order_price.min_order_price = 300.0;
  PromoRequirement order_numbers;
  order_numbers.order_numbers = std::vector<int>{1, 3};
  PromoBonus discount;
  discount.discount = 420;
  PromoSchedule schedule{3, 0, 600};

  const PromoResponse expected{42,
                               PromoStatus::kApproved,
                               "title",
                               "description",
                               {100, 200},
                               PromoType::kGift,
                               GetTimeFromString("2022-02-01"),
                               GetTimeFromString("2022-02-10"),
                               {{schedule}},
                               {min_order_price, order_numbers},
                               {discount}};

  EXPECT_CALL(feature, UpdateResponse(_))
      .WillOnce(Invoke([](PromoResponse& data) {
        data.place_ids.push_back(100);
        data.place_ids.push_back(200);
        data.starts_at = GetTimeFromString("2022-02-01");
        data.ends_at = GetTimeFromString("2022-02-10");
      }))
      .WillOnce(Invoke([&](PromoResponse& data) {
        data.requirements.push_back(min_order_price);
        data.requirements.push_back(order_numbers);
        data.bonuses.push_back(discount);
        data.schedule = std::vector<PromoSchedule>{schedule};
      }));
  const auto result = promo.MakeResponse(42);
  ASSERT_EQ(expected, result);
}

}  // namespace eats_restapp_promo::models
