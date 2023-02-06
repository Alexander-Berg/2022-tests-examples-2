using System;
using FluentAssertions;
using Newtonsoft.Json;
using Xunit;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Models.Orders;
using System.Linq;

namespace Yandex.Taximeter.Common.Tests.Helpers
{
    public class OrderHelperTests
    {
        [Fact]
        public void OrderDictionary_Convert()
        {
            var values = new OrderDictionary
            {
                {"enum", (int) OrderStatus.driving},
                {"datetime", JsonConvert.SerializeObject(DateTime.UtcNow.Date, StaticHelper.JsonSerializerSettings)},
                {"double", "1.0"},
                {"int", "1"}
            };

            values.Convert<OrderStatus>("enum")
                .Should()
                .Be(OrderStatus.driving);

            values.Convert<DateTime>("datetime")
                .Should()
                .Be(DateTime.UtcNow.Date);

            values.Convert<double>("double")
                .Should()
                .Be(1d);

            values.Convert<int>("int")
                .Should()
                .Be(1);
        }

        [Fact]
        public void OrderDictionary_Convert_Nullable()
        {
            var values = new OrderDictionary
            {
                {"enum1", 10 },
                {"enum2", 10 },
                {"enum3", null},
            };

            values.Convert<OrderStatus>("enum1")
                .Should()
                .Be(OrderStatus.driving);

            values.Convert<OrderStatus?>("enum2")
                .Should()
                .Be(OrderStatus.driving);

            values.Convert<OrderStatus?>("enum3")
                .Should()
                .BeNull();
        }

        [Fact]
        public void OrderDictionary_Convert_DateTime()
        {
            var values = new OrderDictionary
            {
                {"date_booking", DateTime.Today }
            };

            var obj = values.ToObject<Order>();
            obj.DateBooking
                .Should()
                .Be(DateTime.Today);
        }

        [Fact]
        public void OrderHelper_RequestConfirm_Status()
        {
            Enum.GetValues(typeof(OrderStatus))
                .Cast<OrderStatus>()
                .Where(p => p < OrderStatus.transporting)
                .OrderByDescending(p => p)
                .First()
                .Should()
                .Be(OrderStatus.calling);
        }
    }
}
