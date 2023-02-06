using System;
using System.Linq;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Extensions;
using Yandex.Taximeter.Core.Utils;

namespace Yandex.Taximeter.Common.Tests.UtilsTests
{
    public class DateTimeExtensionsTests
    {
        [Theory]
        [InlineData("2018-12-10", DayOfWeek.Monday, "2018-12-10")]
        [InlineData("2018-12-12", DayOfWeek.Monday, "2018-12-10")]
        [InlineData("2018-12-16", DayOfWeek.Monday, "2018-12-10")]
        [InlineData("2018-12-17", DayOfWeek.Monday, "2018-12-17")]
        [InlineData("2018-12-10", DayOfWeek.Wednesday, "2018-12-5")]
        [InlineData("2018-12-12", DayOfWeek.Wednesday, "2018-12-12")]
        public void TestDateTimeExtensions_StartOfWeek(string date, DayOfWeek day, string expectedStart)
        {
            var dt = DateTime.Parse(date);
            dt.StartOfWeek(day).Should().Be(DateTime.Parse(expectedStart));
        }
        
        [Theory]
        [InlineData("2018-12-10", DayOfWeek.Monday, "2018-12-16")]
        [InlineData("2018-12-12", DayOfWeek.Monday, "2018-12-16")]
        [InlineData("2018-12-16", DayOfWeek.Monday, "2018-12-16")]
        [InlineData("2018-12-17", DayOfWeek.Monday, "2018-12-23")]
        [InlineData("2018-12-10", DayOfWeek.Wednesday, "2018-12-11")]
        [InlineData("2018-12-12", DayOfWeek.Wednesday, "2018-12-18")]
        public void TestDateTimeExtensions_EndOfWeek(string date, DayOfWeek day, string expectedEnd)
        {
            var dt = DateTime.Parse(date);
            dt.EndOfWeek(day).Date.Should().Be(DateTime.Parse(expectedEnd));
        }
        
        [Theory]
        [InlineData("2018-12-01", "2018-12-14", DayOfWeek.Monday, "2018-12-01", "2018-12-03", "2018-12-10", "2018-12-14")]
        [InlineData("2018-12-03", "2018-12-10", DayOfWeek.Monday, "2018-12-03", "2018-12-10")]
        public void TestDateTimeInterval_SplitWeeks(string from, string to, DayOfWeek day, params string[] intervalBorders)
        {
            var interval = new DateTimeInterval(DateTime.Parse(from), DateTime.Parse(to));
            var fromDates = intervalBorders.Take(intervalBorders.Length - 1);
            var toDates = intervalBorders.Skip(1);
            var intervals =interval.SplitWeeks(day); 
            intervals.Select(x=>x.From).Should().BeEquivalentTo(fromDates.Select(DateTime.Parse));
            intervals.Select(x=>x.To).Should().BeEquivalentTo(toDates.Select(DateTime.Parse));
        }
    }
}
