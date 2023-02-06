#include <gtest/gtest.h>

#include <optional>

#include <filters/infrastructure/fetch_afs_driver_client_info/fetch_afs_driver_client_info.hpp>
#include "afs_bad_signature.hpp"

namespace cf = candidates::filters;

const cf::FilterInfo kEmptyInfo;
const candidates::GeoMember kMember;

TEST(AfsBadSignatureTest, Base) {
  const auto test = [](const std::optional<std::string>& reason,
                       cf::Result result) {
    cf::Context context;

    if (reason) {
      cf::infrastructure::FetchAfsDriverClientInfo::Set(context,
                                                        {reason.value()});
    }

    cf::infrastructure::AfsBadSignature filter(kEmptyInfo);

    EXPECT_EQ(filter.Process(kMember, context), result);
  };

  test(std::nullopt, cf::Result::kAllow);
  test("", cf::Result::kAllow);
  test("fake_gps", cf::Result::kDisallow);
}
