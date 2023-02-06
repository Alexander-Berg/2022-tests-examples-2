#include <gtest/gtest.h>

#include <userver/formats/json.hpp>
#include <userver/formats/json/serialize_container.hpp>
#include <userver/formats/json/serialize_variant.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/formats/parse/common_containers.hpp>
#include <userver/formats/parse/variant.hpp>

namespace promotions_cache::tests::utils {

template <typename TLhs, typename TRhs>
void AssertEqAsJson(const TLhs& lhs, const TRhs& rhs) {
  const auto& lhs_json =
      formats::json::ToString(formats::json::ValueBuilder{lhs}.ExtractValue());
  const auto& rhs_json =
      formats::json::ToString(formats::json::ValueBuilder{rhs}.ExtractValue());

  ASSERT_EQ(lhs_json, rhs_json);
}

}  // namespace promotions_cache::tests::utils
