#include "jump_injection_filter.hpp"

#include <driver-id/hash.hpp>
#include <driver-id/types.hpp>
#include <userver/utils/mock_now.hpp>
#include "userver/utest/utest.hpp"

namespace {
using JumpInjectionFilter =
    driver_route_responder::filters::JumpInjectionFilter;

using Timelefts = driver_route_responder::models::Timelefts;
using Position = driver_route_responder::internal::Position;
using InternalTimelefts = driver_route_responder::models::InternalTimelefts;

constexpr std::chrono::system_clock::time_point ToTimepoint(int seconds) {
  return std::chrono::system_clock::time_point{std::chrono::seconds{seconds}};
}

}  // namespace

TEST(JumpInjectionFilter, BaseTest) {
  auto timelefts_ptr = std::make_shared<Timelefts>();
  utils::datetime::MockNowSet(ToTimepoint(300));
  auto now = utils::datetime::Now();
  timelefts_ptr->timestamp = now;
  int server_delta = 60;
  timelefts_ptr->update_timestamp = now - std::chrono::seconds{server_delta};

  // See the next test for instructions on how to find good tag values
  const std::string tag = "j";

  InternalTimelefts timelefts;
  timelefts.timeleft_data.resize(2);
  timelefts.timeleft_data[0].time_distance_left = {std::chrono::seconds(0),
                                                   0 * ::geometry::meter};
  timelefts.timeleft_data[0].order_id = tag;
  timelefts.timeleft_data[0].raw_time_distance_left =
      timelefts.timeleft_data[0].time_distance_left;
  timelefts.timeleft_data[1].time_distance_left = {std::chrono::seconds(70),
                                                   1500 * ::geometry::meter};
  timelefts.timeleft_data[1].raw_time_distance_left =
      timelefts.timeleft_data[1].time_distance_left;
  timelefts.timeleft_data[1].order_id = tag;

  JumpInjectionFilter filter{
      5,                        /* every 5 minute */
      std::chrono::seconds{60}, /* 60 seconds duration */
      std::chrono::seconds{120} /* 120 seconds range */
  };

  // There is no way to calc this other than by looking into debug
  // output. If you've changed something, then change this constant as well
  static const std::chrono::seconds ref_jump_val{51};

  auto copy = timelefts;
  filter.ApplyFilter(copy);

  // check that jump was applied
  EXPECT_NE(copy.timeleft_data[0].time_distance_left->time.count(), 0);
  EXPECT_NE(copy.timeleft_data[1].time_distance_left->time.count(), 70);
  EXPECT_EQ(copy.timeleft_data[0].time_distance_left->time.count(),
            0 + ref_jump_val.count());
  EXPECT_EQ(copy.timeleft_data[1].time_distance_left->time.count(),
            70 + ref_jump_val.count());

  const auto ref_first_res =
      copy.timeleft_data[0].time_distance_left->time.count();
  const auto ref_second_res =
      copy.timeleft_data[1].time_distance_left->time.count();

  // check that within one minute, jump values will not change
  utils::datetime::MockNowSet(ToTimepoint(331));
  copy = timelefts;
  filter.ApplyFilter(copy);
  EXPECT_EQ(copy.timeleft_data[0].time_distance_left->time.count(),
            ref_first_res);
  EXPECT_EQ(copy.timeleft_data[1].time_distance_left->time.count(),
            ref_second_res);

  // check that jump won't be applied after specified duration
  utils::datetime::MockNowSet(ToTimepoint(361));
  copy = timelefts;
  filter.ApplyFilter(copy);

  EXPECT_EQ(copy.timeleft_data[0].time_distance_left->time.count(), 0);
  EXPECT_EQ(copy.timeleft_data[1].time_distance_left->time.count(), 70);
}

TEST(JumpInjectionFilter, NegativeTest) {
  auto timelefts_ptr = std::make_shared<Timelefts>();
  utils::datetime::MockNowSet(ToTimepoint(300));
  auto now = utils::datetime::Now();
  timelefts_ptr->timestamp = now;
  int server_delta = 60;
  timelefts_ptr->update_timestamp = now - std::chrono::seconds{server_delta};

  // We experimentally found tag where hash % 200 is equal to -82
  // we need significantly large negative number so that jump was negative.
  // If anything changes, uncomment the following code and find new value
  // that produces negative jump val.
  /*
  const auto now_in_minutes =
  std::chrono::duration_cast<std::chrono::minutes>(now.time_since_epoch());
  for(char a = 'A'; a != 'z'; ++a) {
    std::string tag_;
    tag_.resize(1);
    tag_[0] = a;
    // This code is taken from within JumpInjectionFilter. If implementation
    // changed there, change it here as well
    const size_t tag_hash = Fnv0_64(driver_id::DriverDbidView{tag_},
  driver_id::DriverUuidView{tag_}); const int val = (tag_hash % 200 +
  now_in_minutes.count() % 200 ) % 200 - 100;

  // We substract jump, so look for value greater than 0
    EXPECT_LE(val, 0) << "Good tag is " << tag_;
  }
  */
  const std::string good_tag{"s"};

  InternalTimelefts timelefts;
  timelefts.timeleft_data.resize(2);
  timelefts.timeleft_data[0].time_distance_left = {std::chrono::seconds(10),
                                                   0 * ::geometry::meter};
  timelefts.timeleft_data[0].order_id = good_tag;
  timelefts.timeleft_data[0].raw_time_distance_left =
      timelefts.timeleft_data[0].time_distance_left;
  timelefts.timeleft_data[1].time_distance_left = {std::chrono::seconds(120),
                                                   1500 * ::geometry::meter};
  timelefts.timeleft_data[1].raw_time_distance_left =
      timelefts.timeleft_data[1].time_distance_left;
  timelefts.timeleft_data[1].order_id = good_tag;

  JumpInjectionFilter filter{
      5,                        /* every 5 minute */
      std::chrono::seconds{60}, /* 60 seconds duration */
      std::chrono::seconds{120} /* 120 seconds range */
  };

  // There is no way to calc this other than by looking into debug
  // output. If you've changed something, then change this constant as well
  [[maybe_unused]] static const std::chrono::seconds ref_jump_val{-109};

  auto copy = timelefts;
  filter.ApplyFilter(copy);

  // check that jump was applied, but as it was negative, value is zero
  EXPECT_EQ(copy.timeleft_data[0].time_distance_left->time.count(), 0);
  // here it should have been applied without problem
  EXPECT_EQ(copy.timeleft_data[1].time_distance_left->time.count(),
            120 + ref_jump_val.count());
}
