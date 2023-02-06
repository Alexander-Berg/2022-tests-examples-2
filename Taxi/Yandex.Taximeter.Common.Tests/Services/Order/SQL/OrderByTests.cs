using System;
using System.Linq;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Models.Orders;
using Yandex.Taximeter.Core.Repositories.Sql.Order;

namespace Yandex.Taximeter.Common.Tests.Services.Order.SQL
{
    public class OrderByTests
    {
        private static readonly OrderDictionary[] Orders = new[]
        {
            new OrderDictionary
            {
                ["id"] = "order1",
                ["date_booking"] = new DateTime(2017, 01, 01),
                ["status"] = 50,
                ["driver_id"] = "driver1"
            },
            new OrderDictionary
            {
                ["id"] = "order2",
                ["date_booking"] = new DateTime(2017, 01, 02),
                ["status"] = 50,
                ["driver_id"] = "driver2"
            },
            new OrderDictionary
            {
                ["id"] = "order3",
                ["date_booking"] = new DateTime(2017, 01, 03),
                ["status"] = 60,
                ["driver_id"] = "driver1"
            },
            new OrderDictionary
            {
                ["id"] = "order4",
                ["date_booking"] = new DateTime(2017, 01, 04),
                ["status"] = 70,
                ["driver_id"] = "driver2"
            },
            new OrderDictionary
            {
                ["id"] = "order5",
                ["date_booking"] = new DateTime(2017, 01, 05),
                ["status"] = 60,
                ["driver_id"] = "driver3"
            },

        };

        [Fact]
        public void TestEquals()
        {
            var item1 = OrderBy.Asc("status").Desc("date_booking");
            var item2 = OrderBy.Asc("status").Desc("date_booking");
            var item3 = OrderBy.Desc("status").Desc("date_booking");

            item1.Should().Be(item2);
            item3.Should().NotBe(item1);
            item3.Should().NotBe(item2);
        }

        [Fact]
        public void TestOrderBy_Ascending()
        {
            var result = Orders.OrderBy(x=>x, OrderBy.Asc("date_booking")).Select(x => x.Convert<string>("id")).ToArray();
            result.Should().BeEquivalentTo(new[] { "order1", "order2", "order3", "order4", "order5"});
        }

        [Fact]
        public void TestOrderBy_Descending()
        {
            var result = Orders.OrderBy(x => x, OrderBy.Desc("date_booking")).Select(x => x.Convert<string>("id")).ToArray();
            result.Should().BeEquivalentTo(new[] { "order5", "order4", "order3", "order2", "order1" });
        }


        [Fact]
        public void TestOrderBy_Multiple()
        {
            var result = Orders.OrderBy(x => x, OrderBy.Asc("driver_id").Desc("date_booking")).Select(x => x.Convert<string>("id")).ToArray();
            result.Should().BeEquivalentTo(new[] { "order3", "order1", "order4", "order2", "order5" });
        }

        [Fact]
        public void TestOrderBy_CreateFilter_Preceding()
        {
            var orderBy = OrderBy.Asc("driver_id").Desc("date_booking");
            var preceding = orderBy.Preceding(new OrderDictionary
            {
                ["driver_id"] = "driver1",
                ["date_booking"] = new DateTime(2017, 01, 01)
            });

            preceding.ToString().Should()
                .Be("driver_id < @driver_id OR (driver_id = @driver_id AND (date_booking > @date_booking))");
        }

        [Fact]
        public void TestOrderBy_CreateFilter_Following()
        {
            var orderBy = OrderBy.Asc("driver_id").Desc("date_booking");
            var following = orderBy.Following(new OrderDictionary
            {
                ["driver_id"] = "driver1",
                ["date_booking"] = new DateTime(2017, 01, 01)
            });

            following.ToString().Should()
                .Be("driver_id > @driver_id OR (driver_id = @driver_id AND (date_booking < @date_booking))");
            
        }
    }
}