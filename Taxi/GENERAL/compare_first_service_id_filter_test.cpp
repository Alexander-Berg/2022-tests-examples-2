#include "compare_first_service_id_filter.hpp"

#include "userver/utest/utest.hpp"

namespace {
using CompareFirstServiceIdFilter =
    driver_route_responder::filters::CompareFirstServiceIdFilter;

using Timelefts = driver_route_responder::models::Timelefts;
using TimeleftData = driver_route_responder::models::TimeleftData;
}  // namespace

TEST(CompareFirstServiceIdFilter, BaseTest) {
  // No driver in cache
  {
    const std::string kServiceId = "any-service-id";
    auto timelefts_ptr = nullptr;

    CompareFirstServiceIdFilter filter{kServiceId};
    ASSERT_NO_THROW(filter.VisitTimelefts(timelefts_ptr));
  }

  // Service ids is equal
  {
    const std::string kServiceId = "reposition-watcher";
    TimeleftData timeleft_data;
    timeleft_data.service_id = kServiceId;

    auto timelefts_ptr = std::make_shared<Timelefts>();
    timelefts_ptr->timeleft_data = {timeleft_data};

    CompareFirstServiceIdFilter filter{kServiceId};
    ASSERT_NO_THROW(filter.VisitTimelefts(timelefts_ptr));
  }

  // Service ids is not equal
  {
    const std::string kServiceId = "transporting";
    const std::string kFilterServiceId = "reposition-watcher";
    TimeleftData timeleft_data;
    timeleft_data.service_id = kServiceId;

    auto timelefts_ptr = std::make_shared<Timelefts>();
    timelefts_ptr->timeleft_data = {timeleft_data};

    CompareFirstServiceIdFilter filter{kFilterServiceId};
    ASSERT_ANY_THROW(filter.VisitTimelefts(timelefts_ptr));
  }
}
