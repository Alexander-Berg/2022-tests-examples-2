#include <models/priorities/to_max_value.hpp>

#include <variant>

#include <gtest/gtest.h>

TEST(MaxPriorityValue, Rules) {
  using namespace models::priorities;
  using namespace handlers;

  const TagRule kTagRule{"aurora", PriorityValue{1, 2}, std::nullopt};
  const RatingRule kRatingRule{RatingMatchBetween{1, 2}, PriorityValue{0, 4},
                               "tanker_key", std::nullopt};
  const CarYearRule kCarYearRule{CarYearHigherThan{2010}, PriorityValue{3, 4},
                                 "tanker_key", std::nullopt};

  const PriorityRule kSingleRule{SingleRule{kTagRule}};
  const PriorityRule kRankedRule{
      RankedRule{{kRatingRule, kTagRule, kCarYearRule}}};
  const PriorityRule kExcludingRule{ExcludingRule{{kRatingRule, kTagRule}}};
  const PriorityRule kEmptyRule{RankedRule{{}}};
  const PriorityRule kActivityRule{ActivityRule{{}, "tanker_key"}};

  {
    const ToMaxValue visitor{ValueDestination::kDisplay};

    ASSERT_EQ(2, std::visit(visitor, kSingleRule));
    ASSERT_EQ(4, std::visit(visitor, kRankedRule));
    ASSERT_EQ(4, std::visit(visitor, kExcludingRule));
    ASSERT_EQ(0, std::visit(visitor, kEmptyRule));
    ASSERT_EQ(5, std::visit(visitor, kActivityRule));
  }

  {
    const ToMaxValue visitor{ValueDestination::kBackend};

    ASSERT_EQ(1, std::visit(visitor, kSingleRule));
    ASSERT_EQ(3, std::visit(visitor, kRankedRule));
    ASSERT_EQ(1, std::visit(visitor, kExcludingRule));
  }
}
