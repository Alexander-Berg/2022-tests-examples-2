#include <gtest/gtest.h>
#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>

#include <filters/efficiency/active_reposition/active_reposition.hpp>
#include <filters/efficiency/fetch_reposition_status/fetch_reposition_status.hpp>

namespace {
namespace Cf = candidates::filters;
using Filter = candidates::filters::efficiency::ActiveReposition;
using Factory = candidates::filters::efficiency::ActiveRepositionFactory;
using candidates::GeoMember;
using candidates::filters::Context;
using candidates::filters::Result;
using candidates::filters::efficiency::FetchRepositionStatus;

const candidates::filters::FilterInfo kEmptyInfo;
}  // namespace

UTEST(ActiveReposition, InactiveReposition) {
  Filter filter(kEmptyInfo);
  clients::reposition::IndexEntry status{true, false, false};

  Context context;
  GeoMember member;

  FetchRepositionStatus::Set(context, status);
  EXPECT_EQ(filter.Process(member, context), Result::kIgnore);
}

UTEST(ActiveReposition, ActiveReposition) {
  Filter filter(kEmptyInfo);
  clients::reposition::IndexEntry status{false, false, true};

  Context context;
  GeoMember member;

  FetchRepositionStatus::Set(context, status);
  EXPECT_EQ(filter.Process(member, context), Result::kDisallow);
}
