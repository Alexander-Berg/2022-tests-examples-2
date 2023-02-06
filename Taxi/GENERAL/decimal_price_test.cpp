#include <userver/utest/utest.hpp>

#include <utils/decimal_price.hpp>

namespace fleet_orders_manager::utils {

TEST(EtimatePriceParcer, EtimatePriceParcer) {
  ASSERT_EQ(FormatPrice(DecimalPrice::FromStringPermissive("0")), "0");
  ASSERT_EQ(FormatPrice(DecimalPrice::FromStringPermissive("1")), "1");
  ASSERT_EQ(FormatPrice(DecimalPrice::FromStringPermissive("10")), "10");
  ASSERT_EQ(FormatPrice(DecimalPrice::FromStringPermissive("0.1")), "0.1");
  ASSERT_EQ(FormatPrice(DecimalPrice::FromStringPermissive("0.001")), "0");
  ASSERT_EQ(FormatPrice(DecimalPrice::FromStringPermissive("10.001")), "10");
  ASSERT_EQ(FormatPrice(DecimalPrice::FromStringPermissive("0.123")), "0.12");
  ASSERT_EQ(FormatPrice(DecimalPrice::FromStringPermissive("0.127")), "0.13");
  ASSERT_EQ(FormatPrice(DecimalPrice::FromStringPermissive("100000000000.127")),
            "100000000000.13");
}

}  // namespace fleet_orders_manager::utils
