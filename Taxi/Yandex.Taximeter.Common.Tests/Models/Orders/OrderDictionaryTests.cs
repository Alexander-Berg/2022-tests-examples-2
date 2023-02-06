using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Models.Orders;
using Yandex.Taximeter.Core.Services;

namespace Yandex.Taximeter.Common.Tests.Models.Orders
{
    public class OrderDictionaryTests
    {
        [Fact]
        public void Get_Discount_NoCouponColumns_ReturnsNull()
        {
            var order = new OrderDictionary();
            order.Discount.Should().BeNull();
        }

        [Fact]
        public void Get_Discount_ZeroCoupon_ReturnsNull()
        {
            var order = new OrderDictionary
            {
                [OrderSqlColumns.COST_COUPON] = 0,
                [OrderSqlColumns.COST_COUPON_PERCENT] = 0
            };
            order.Discount.Should().BeNull();
        }

        [Fact]
        public void Get_Discount_PositiveCoupon_ReturnsValidDiscount()
        {
            var order = new OrderDictionary
            {
                [OrderSqlColumns.COST_COUPON] = 10.0,
                [OrderSqlColumns.COST_COUPON_PERCENT] = 20.0
            };
            order.Discount.Limit.Should().Be((double) order[OrderSqlColumns.COST_COUPON]);
            order.Discount.Percent.Should().Be((double) order[OrderSqlColumns.COST_COUPON_PERCENT]);
        }
    }
}