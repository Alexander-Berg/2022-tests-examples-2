#include <gtest/gtest.h>

#include <candidates/filters/filter.hpp>

namespace candidates::filters::test {

class DisallowWithReason : public Filter {
 public:
  using Filter::Filter;

  Result Process([[maybe_unused]] const GeoMember& member,
                 Context& context) const override {
    CONTEXT_DETAIL_FMT(context, "nothing {}", "personal");
    return Result::kDisallow;
  }
};

}  // namespace candidates::filters::test

namespace cf = candidates::filters;

TEST(DisallowReason, Sample) {
  cf::FilterInfo info{"f1", {}, {}, false, {}};
  cf::test::DisallowWithReason filter(info);
  cf::Context context;
  EXPECT_EQ(cf::Result::kDisallow, filter.Process({}, context));
  EXPECT_TRUE(context.GetDetails().empty());

  context.need_details = true;
  EXPECT_EQ(cf::Result::kDisallow, filter.Process({}, context));
  ASSERT_FALSE(context.GetDetails().empty());
  EXPECT_EQ(context.GetDetails().front().desc, "nothing personal");
}
