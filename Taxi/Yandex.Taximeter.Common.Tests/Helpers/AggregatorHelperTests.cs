using System;
using System.Globalization;
using FluentAssertions;
using Xunit;
using System.Linq;

namespace Yandex.Taximeter.Common.Tests.Helpers
{
    public class AggregatorHelperTests
    {
        [Theory]
        [InlineData("Agg:Act:d1bf2d6baf30419f8addad3bb0ed1d7b:")]
        public void Act_Search(string key)
        {
            var keys = new[]
            {
                "Agg:Act:d1bf2d6baf30419f8addad3bb0ed1d7b:201601",
                "Agg:Act:d1bf2d6baf30419f8addad3bb0ed1d7b:201611",
                "Agg:Act:d1bf2d6baf30419f8addad3bb0ed1d7b:201512",
                "Agg:Act:d1bf2d6baf30419f8addad3bb0ed1d7b:201609",
                "Agg:Act:d1bf2d6baf30419f8addad3bb0ed1d7b:201606",
            };

            var result = keys
                .Select(p => DateTime.ParseExact(p.Substring(key.Length), "yyyyMM", CultureInfo.CurrentUICulture))
                .ToArray();

            result.First().Should().Be(new DateTime(2016, 1, 1));
        }
    }
}