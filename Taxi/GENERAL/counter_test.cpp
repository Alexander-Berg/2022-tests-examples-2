#include <gtest/gtest.h>

#include <discounts/models/counter.hpp>
#include <discounts/models/error.hpp>

namespace {

discounts::models::TwoKeyCounter<
    discounts::models::OnDuplicateCounterThrowStrategy>
MakeTwoKeyCounter() {
  return discounts::models::TwoKeyCounter<
      discounts::models::OnDuplicateCounterThrowStrategy>{};
}

discounts::models::ThreeKeyCounter<
    discounts::models::OnDuplicateCounterThrowStrategy>
MakeThreeKeyCounter() {
  return discounts::models::ThreeKeyCounter<
      discounts::models::OnDuplicateCounterThrowStrategy>{};
}
}  // namespace

TEST(TwoKeyCounter, EmptyCounter) {
  auto counter = MakeTwoKeyCounter();

  ASSERT_EQ(counter.Count("key1", "key2"), 0);
  ASSERT_EQ(counter.Count(std::nullopt, "key2"), 0);
  ASSERT_EQ(counter.Count("key1", std::nullopt), 0);
  ASSERT_EQ(counter.Count(std::nullopt, std::nullopt), 0);
}

TEST(ThreeKeyCounter, EmptyThreeKeyCounter) {
  auto counter = MakeThreeKeyCounter();

  ASSERT_EQ(counter.Count("key1", "key2", "key3"), 0);
  ASSERT_EQ(counter.Count(std::nullopt, "key2", "key3"), 0);
  ASSERT_EQ(counter.Count("key1", std::nullopt, "key2"), 0);
  ASSERT_EQ(counter.Count("key1", "key2", std::nullopt), 0);
  ASSERT_EQ(counter.Count("key1", std::nullopt, std::nullopt), 0);
  ASSERT_EQ(counter.Count(std::nullopt, "key2", std::nullopt), 0);
  ASSERT_EQ(counter.Count(std::nullopt, std::nullopt, "key3"), 0);
  ASSERT_EQ(counter.Count(std::nullopt, std::nullopt, std::nullopt), 0);
}

TEST(ThreeKeyCounter, AddSingle) {
  auto counter = MakeThreeKeyCounter();
  counter.Add("key1", "key2", "key3", 10);

  ASSERT_EQ(counter.Count("key1", "key2", "key3"), 10);
  ASSERT_EQ(counter.Count(std::nullopt, "key2", "key3"), 10);
  ASSERT_EQ(counter.Count("key1", std::nullopt, "key3"), 10);
  ASSERT_EQ(counter.Count("key1", "key2", std::nullopt), 10);
  ASSERT_EQ(counter.Count("key1", std::nullopt, std::nullopt), 10);
  ASSERT_EQ(counter.Count(std::nullopt, "key2", std::nullopt), 10);
  ASSERT_EQ(counter.Count(std::nullopt, std::nullopt, "key3"), 10);
  ASSERT_EQ(counter.Count(std::nullopt, std::nullopt, std::nullopt), 10);
}

TEST(ThreeKeyCounter, AddTwoDifferent) {
  auto counter = MakeThreeKeyCounter();
  counter.Add("key1_1", "key2_1", "key3_1", 10);
  counter.Add("key1_2", "key2_2", "key3_2", 10);
  counter.Add("key1_3", "key2_3", "key3_3", 10);

  ASSERT_EQ(counter.Count("key1_1", "key2_1", "key3_1"), 10);
  ASSERT_EQ(counter.Count(std::nullopt, "key2_2", "key3_2"), 10);
  ASSERT_EQ(counter.Count("key1_3", std::nullopt, "key3_3"), 10);
  ASSERT_EQ(counter.Count("key1_1", "key2_2", std::nullopt), 0);
  ASSERT_EQ(counter.Count("key1_1", std::nullopt, std::nullopt), 10);
  ASSERT_EQ(counter.Count(std::nullopt, "key2_2", std::nullopt), 10);
  ASSERT_EQ(counter.Count(std::nullopt, std::nullopt, "key3_3"), 10);
  ASSERT_EQ(counter.Count(std::nullopt, std::nullopt, std::nullopt), 30);
}

TEST(TwoKeyCounter, AddSingle) {
  auto counter = MakeTwoKeyCounter();
  counter.Add("key1", "key2", 10);

  ASSERT_EQ(counter.Count("key1", "key2"), 10);
  ASSERT_EQ(counter.Count(std::nullopt, "key2"), 10);
  ASSERT_EQ(counter.Count("key1", std::nullopt), 10);
  ASSERT_EQ(counter.Count(std::nullopt, std::nullopt), 10);
  ASSERT_EQ(counter.Count("key", "key2"), 0);
  ASSERT_EQ(counter.Count("key1", "key"), 0);
  ASSERT_EQ(counter.Count("key", "key"), 0);
}

TEST(TwoKeyCounter, AddTwoDifferent) {
  auto counter = MakeTwoKeyCounter();
  counter.Add("key1_1", "key2_1", 10);
  counter.Add("key1_2", "key2_2", 10);

  ASSERT_EQ(counter.Count("key1_1", "key2_1"), 10);
  ASSERT_EQ(counter.Count("key1_2", "key2_2"), 10);
  ASSERT_EQ(counter.Count(std::nullopt, "key2_1"), 10);
  ASSERT_EQ(counter.Count(std::nullopt, "key2_2"), 10);
  ASSERT_EQ(counter.Count("key1_1", std::nullopt), 10);
  ASSERT_EQ(counter.Count("key1_2", std::nullopt), 10);
  ASSERT_EQ(counter.Count(std::nullopt, std::nullopt), 20);
}

TEST(TwoKeyCounter, AddTwoSameKey1DifferentKey2) {
  auto counter = MakeTwoKeyCounter();
  counter.Add("key1", "key2_1", 10);
  counter.Add("key1", "key2_2", 10);

  ASSERT_EQ(counter.Count("key1", "key2_1"), 10);
  ASSERT_EQ(counter.Count("key1", "key2_2"), 10);
  ASSERT_EQ(counter.Count(std::nullopt, "key2_1"), 10);
  ASSERT_EQ(counter.Count(std::nullopt, "key2_2"), 10);
  ASSERT_EQ(counter.Count("key1", std::nullopt), 20);
  ASSERT_EQ(counter.Count(std::nullopt, std::nullopt), 20);
}

TEST(TwoKeyCounter, AddTwoDifferentKey1SameKey2) {
  auto counter = MakeTwoKeyCounter();
  counter.Add("key1_1", "key2", 10);
  counter.Add("key1_2", "key2", 10);

  ASSERT_EQ(counter.Count("key1_1", "key2"), 10);
  ASSERT_EQ(counter.Count("key1_2", "key2"), 10);
  ASSERT_EQ(counter.Count("key1_1", std::nullopt), 10);
  ASSERT_EQ(counter.Count("key1_2", std::nullopt), 10);
  ASSERT_EQ(counter.Count(std::nullopt, "key2"), 20);
  ASSERT_EQ(counter.Count(std::nullopt, std::nullopt), 20);
}

TEST(TwoKeyCounter, AddTwoSame) {
  auto counter = MakeTwoKeyCounter();
  counter.Add("key1", "key2", 10);

  EXPECT_THROW(counter.Add("key1", "key2", 10), discounts::models::Error);
  ASSERT_EQ(counter.Count("key1", "key2"), 10);
}

TEST(CounterValidator, AddDifferent) {
  discounts::models::CounterValidator validator;
  validator.Add("key1", "key2");
  validator.Add("key1", std::nullopt);
  validator.Add(std::nullopt, "key2");
  validator.Add(std::nullopt, std::nullopt);
}

TEST(CounterValidator, AddTwoSame) {
  discounts::models::CounterValidator validator;
  validator.Add("key1", "key2");

  EXPECT_THROW(validator.Add("key1", "key2"), discounts::models::Error);
}

TEST(CounterValidator, AddTwoSameKey1NoKey2) {
  discounts::models::CounterValidator validator;
  validator.Add("key1", std::nullopt);

  EXPECT_THROW(validator.Add("key1", std::nullopt), discounts::models::Error);
}

TEST(CounterValidator, AddTwoNoKey1SameKey2) {
  discounts::models::CounterValidator validator;
  validator.Add(std::nullopt, "key2");

  EXPECT_THROW(validator.Add(std::nullopt, "key2"), discounts::models::Error);
}

TEST(CounterValidator, AddTwoNoKey1NoKey2) {
  discounts::models::CounterValidator validator;
  validator.Add(std::nullopt, std::nullopt);

  EXPECT_THROW(validator.Add(std::nullopt, std::nullopt),
               discounts::models::Error);
}
