using System;
using System.Collections.Generic;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Car;
using Yandex.Taximeter.Core.Repositories.Sql.Order;

namespace Yandex.Taximeter.Common.Tests.Services.Order.SQL
{
    public class OrderFilterTests
    {
        [Fact]
        public void TestEquals()
        {
            var filter1 = OrderFilter
                .DateBetween("date_booking", new DateTime(2017, 01, 01), null)
                .Equal("driver_id", "test_driver")
                .NotEqual("car_id", "test_car")
                .In("status", 50, 60, 70)
                .NotIn("provider", 1, 2)
                .OrderIdOrOldUuid("order1", "order2", "order3")
                .Category(CategoryFlags.Comfort)
                .PassengerPhone("79260000000");

            var filter2 = OrderFilter
                .DateBetween("date_booking", new DateTime(2017, 01, 01), null)
                .Equal("driver_id", "test_driver")
                .NotEqual("car_id", "test_car")
                .In("status", 50, 60, 70)
                .NotIn("provider", 1, 2)
                .OrderIdOrOldUuid("order1", "order2", "order3")
                .Category(CategoryFlags.Comfort)
                .PassengerPhone("79260000000");

            filter1.Should().Be(filter2);

            var filter3 = OrderFilter.DateBetween("date_booking", new DateTime(2017, 01, 01), null);
            filter3.Should().NotBe(filter1);
            filter3.Should().NotBe(filter2);
        }

        [Fact]
        public void TestDateFilter_From()
        {
            var filter = OrderFilter
                .DateBetween("date_booking", new DateTime(2017, 01, 01), null);
            var whereItem = filter.ToSql();
            whereItem.Sql.Should().Be("date_booking >= @date_booking_from");
            whereItem.Values.Should().BeEquivalentTo(
                new Dictionary<string, object>
                {
                    ["date_booking_from"] = new DateTime(2017,01,01)
                }
            );
        }

        [Fact]
        public void TestDateFilter_To()
        {
            var filter = OrderFilter
                .DateBetween("date_booking", null, new DateTime(2017, 01, 01));
            var whereItem = filter.ToSql();
            whereItem.Sql.Should().Be("date_booking <= @date_booking_to");
            whereItem.Values.Should().BeEquivalentTo(
                new Dictionary<string, object>
                {
                    ["date_booking_to"] = new DateTime(2017, 01, 01)
                }
            );
        }

        [Fact]
        public void TestDateFilter_Between()
        {
            var filter = OrderFilter
                .DateBetween("date_booking", new DateTime(2017, 01, 01), new DateTime(2017, 02, 01));
            var whereItem = filter.ToSql();
            whereItem.Sql.Should().Be("date_booking BETWEEN @date_booking_from AND @date_booking_to");
            whereItem.Values.Should().BeEquivalentTo(
                new Dictionary<string, object>
                {
                    ["date_booking_from"] = new DateTime(2017, 01, 01),
                    ["date_booking_to"] = new DateTime(2017, 02, 01)
                }
            );
        }


        [Fact]
        public void TestEqualsFilter()
        {
            var filter = OrderFilter
                .Equal("driver_id", "test_driver");
            var whereItem = filter.ToSql();
            whereItem.Sql.Should().Be("driver_id = @driver_id");
            whereItem.Values.Should().BeEquivalentTo(
                new Dictionary<string, object>
                {
                    ["driver_id"] = "test_driver"
                }
            );
        }

        [Fact]
        public void TestNotEqualsFilter()
        {
            var filter = OrderFilter
                .NotEqual("driver_id", "test_driver");
            var whereItem = filter.ToSql();
            whereItem.Sql.Should().Be("driver_id != @driver_id");
            whereItem.Values.Should().BeEquivalentTo(
                new Dictionary<string, object>
                {
                    ["driver_id"] = "test_driver"
                }
            );
        }

        [Fact]
        public void TestLessThanFilter()
        {
            var filter = OrderFilter
                .LessThan("status", 50);
            var whereItem = filter.ToSql();
            whereItem.Sql.Should().Be("status < @status");
            whereItem.Values.Should().BeEquivalentTo(
                new Dictionary<string, object>
                {
                    ["status"] = 50
                }
            );
        }
        
        [Fact]
        public void TestLessThanOrEqualFilter()
        {
            var filter = OrderFilter
                .LessThanOrEqual("status", 50);
            var whereItem = filter.ToSql();
            whereItem.Sql.Should().Be("status <= @status");
            whereItem.Values.Should().BeEquivalentTo(
                new Dictionary<string, object>
                {
                    ["status"] = 50
                }
            );
        }


        [Fact]
        public void TestGreaterThanFilter()
        {
            var filter = OrderFilter
                .GreaterThan("status", 50);
            var whereItem = filter.ToSql();
            whereItem.Sql.Should().Be("status > @status");
            whereItem.Values.Should().BeEquivalentTo(
                new Dictionary<string, object>
                {
                    ["status"] = 50
                }
            );
        }

        [Fact]
        public void TestGreaterThanOrEqualFilter()
        {
            var filter = OrderFilter
                .GreaterThanOrEqual("status", 50);
            var whereItem = filter.ToSql();
            whereItem.Sql.Should().Be("status >= @status");
            whereItem.Values.Should().BeEquivalentTo(
                new Dictionary<string, object>
                {
                    ["status"] = 50
                }
            );
        }

        [Fact]
        public void TestLikeFilter()
        {
            var filter = OrderFilter
                .Like("driver_id", "test_driver");
            var whereItem = filter.ToSql();
            whereItem.Sql.Should().Be("driver_id ILIKE '%'||@driver_id||'%'");
            whereItem.Values.Should().BeEquivalentTo(
                new Dictionary<string, object>
                {
                    ["driver_id"] = "test_driver"
                }
            );
        }

        [Fact]
        public void TestInFilter()
        {
            var filter = OrderFilter
                .In("status", 50, 60, 70);
            var whereItem = filter.ToSql();
            whereItem.Sql.Should().Be("status = ANY(@status)");
            whereItem.Values.Should().BeEquivalentTo(
                new Dictionary<string, object>
                {
                    ["status"] = new object[] { 50, 60, 70}
                }
            );
        }

        [Fact]
        public void TestNotInFilter()
        {
            var filter = OrderFilter
                .NotIn("status", 50, 60, 70);
            var whereItem = filter.ToSql();
            whereItem.Sql.Should().Be("status != ANY(@status)");
            whereItem.Values.Should().BeEquivalentTo(
                new Dictionary<string, object>
                {
                    ["status"] = new object[] { 50, 60, 70 }
                }
            );
        }

        [Fact]
        public void TestIsNullFilter()
        {
            var filter = OrderFilter.IsNull("address_from");
            var whereItem = filter.ToSql();
            whereItem.Sql.Should().Be("address_from IS NULL");
            whereItem.Values.Should().BeNull();
        }

        [Fact]
        public void TestIsNotNullFilter()
        {
            var filter = OrderFilter.IsNotNull("address_from");
            var whereItem = filter.ToSql();
            whereItem.Sql.Should().Be("address_from IS NOT NULL");
            whereItem.Values.Should().BeNull();
        }

        [Fact]
        public void TestIsNullOrEmptyFilter()
        {
            var filter = OrderFilter.IsNullOrEmpty("address_from");
            var whereItem = filter.ToSql();
            whereItem.Sql.Should().Be("address_from IS NULL OR address_from = ''");
            whereItem.Values.Should().BeNull();
        }

        [Fact]
        public void TestIsNotNullOrEmptyFilter()
        {
            var filter = OrderFilter
                .IsNotNullOrEmpty("address_from");
            var whereItem = filter.ToSql();
            whereItem.Sql.Should().Be("address_from IS NOT NULL AND address_from != ''");
            whereItem.Values.Should().BeNull();
        }

        [Fact]
        public void TestOrderIdFilter_Single()
        {
            var filter = OrderFilter
                .OrderIdOrOldUuid("order1");
            var whereItem = filter.ToSql();
            whereItem.Sql.Should().Be("id=@id OR (old_uuid=@id AND old_uuid IS NOT NULL)");
            whereItem.Values.Should().BeEquivalentTo(
                new Dictionary<string, object>
                {
                    ["id"] = "order1"
                }
            );
        }

        [Fact]
        public void TestOrderIdFilter_Multiple()
        {
            var filter = OrderFilter
                .OrderIdOrOldUuid("order1", "order2", "order3");
            var whereItem = filter.ToSql();
            whereItem.Sql.Should().Be("id=ANY(@id) OR (old_uuid=ANY(@id) AND old_uuid IS NOT NULL)");
            whereItem.Values.Should().BeEquivalentTo(
                new Dictionary<string, object>
                {
                    ["id"] = new[] { "order1", "order2", "order3" }
                }
            );
        }

        [Fact]
        public void TestQueryFilter()
        {
            var filter = OrderFilter
                .Query("100500");
            var whereItem = filter.ToSql();
            whereItem.Sql.Should().Be("id=@id OR (old_uuid=@id AND old_uuid IS NOT NULL) OR number = @number");
            whereItem.Values.Should().BeEquivalentTo(
                new Dictionary<string, object>
                {
                    ["id"] = "100500",
                    ["number"] = 100500
                }
            );
        }

        [Fact]
        public void TestCompanyFilter()
        {
            var filter = OrderFilter
                .Company("test_company");
            var whereItem = filter.ToSql();
            whereItem.Sql.Should().Be("company_id = @company OR company_name ILIKE '%'||@company||'%'");
            whereItem.Values.Should().BeEquivalentTo(
                new Dictionary<string, object>
                {
                    ["company"] = "test_company"
                }
            );
        }

        [Fact]
        public void TestCategoryFilter()
        {
            var filter = OrderFilter
                .Category(CategoryFlags.Comfort);
            var whereItem = filter.ToSql();
            whereItem.Sql.Should().Be("categorys & @categorys != 0");
            whereItem.Values.Should().BeEquivalentTo(
                new Dictionary<string, object>
                {
                    ["categorys"] = (int)CategoryFlags.Comfort
                }
            );
        }

        [Fact]
        public void TestIsDelayedFilter()
        {
            var filter = OrderFilter
                .IsDelayed();
            var whereItem = filter.ToSql();
            whereItem.Sql.Should().Be("date_waiting IS NOT NULL AND date_booking < date_waiting");
            whereItem.Values.Should().BeNull();
        }

        [Fact]
        public void TestIsNotDelayedFilter()
        {
            var filter = OrderFilter
                .IsNotDelayed();
            var whereItem = filter.ToSql();
            whereItem.Sql.Should().Be("date_waiting IS NULL OR date_booking >= date_waiting");
            whereItem.Values.Should().BeNull();
        }

        [Fact]
        public void TestPassengerPhoneFilter_Single()
        {
            var filter = OrderFilter
                .PassengerPhone("79260000000");
            var whereItem = filter.ToSql();
            whereItem.Sql.Should().Be("phone1 = @phone1 OR phone1 = @phone1_normalized OR phone2 = @phone1 OR phone2 = @phone1_normalized OR phone3 = @phone1 OR phone3 = @phone1_normalized");
            whereItem.Values.Should().BeEquivalentTo(
                new Dictionary<string, object>
                {
                    ["phone1"] = "79260000000",
                    ["phone1_normalized"] = "+79260000000"
                }
            );
        }

        [Fact]
        public void TestPassengerPhoneFilter_Multiple()
        {
            var filter = OrderFilter
                .PassengerPhone("79260000000", "79261111111");
            var whereItem = filter.ToSql();
            whereItem.Sql.Should().Be("phone1 = ANY(@phone1) OR phone1 = ANY(@phone1_normalized) OR phone2 = ANY(@phone1) OR phone2 = ANY(@phone1_normalized) OR phone3 = ANY(@phone1) OR phone3 = ANY(@phone1_normalized)");
        }

        [Fact]
        public void TestCompositeFilter()
        {
            var filter = OrderFilter
                .DateBetween("date_booking", new DateTime(2017, 01, 01), new DateTime(2017, 02, 01))
                .In("status", 50, 60, 70)
                .Equal("provider", 2);
            var whereItem = filter.ToSql();
            whereItem.Sql.Should().Be("(date_booking BETWEEN @date_booking0_from AND @date_booking0_to) AND (status = ANY(@status1)) AND (provider = @provider2)");
            whereItem.Values.Should().BeEquivalentTo(
                new Dictionary<string, object>
                {
                    ["date_booking0_from"] = new DateTime(2017, 01, 01),
                    ["date_booking0_to"] = new DateTime(2017, 02, 01),
                    ["status1"] = new object[] { 50, 60, 70},
                    ["provider2"] = 2
                }
            );
        }
    }
}
