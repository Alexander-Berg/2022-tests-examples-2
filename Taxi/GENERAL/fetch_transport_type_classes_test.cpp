#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_transport_type/fetch_transport_type.hpp>
#include <userver/utest/utest.hpp>
#include "fetch_transport_type_classes.hpp"

const candidates::filters::FilterInfo kEmptyInfo;

namespace cf = candidates::filters;
namespace cfi = candidates::filters::infrastructure;

UTEST(FetchTransportTypeClasses, Sample) {
  cf::Context context;

  candidates::models::TransportTypeClasses excluded_classes{
      {models::TransportType::kPedestrian, models::Classes({"econom"})}};

  cfi::FetchTransportTypeClasses filter(kEmptyInfo,
                                        models::Classes({"econom", "comfort"}),
                                        {}, std::move(excluded_classes));

  cfi::FetchTransportType::Set(context, models::TransportType::kCar);
  EXPECT_EQ(filter.Process({}, context), cf::Result::kAllow);
  EXPECT_EQ(cfi::FetchTransportTypeClasses::Get(context),
            models::Classes({"econom", "comfort"}));

  cfi::FetchTransportType::Set(context, models::TransportType::kPedestrian);
  EXPECT_EQ(filter.Process({}, context), cf::Result::kAllow);
  EXPECT_EQ(cfi::FetchTransportTypeClasses::Get(context),
            models::Classes({"comfort"}));
}
