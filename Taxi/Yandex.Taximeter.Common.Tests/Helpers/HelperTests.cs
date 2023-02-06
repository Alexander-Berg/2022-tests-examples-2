using System;
using System.Collections.Generic;
using System.Globalization;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Code;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Car;

namespace Yandex.Taximeter.Common.Tests.Helpers
{
    public class HelperTests
    {
        [Fact]
        public void DateTimeToHuman_AnyTimeSpan_ReturnsHumanReadableString()
        {
            var data = new List<Tuple<TimeSpan, string>>
            {
                Tuple.Create(new TimeSpan(4,5,6,7), "4 д 5 ч"),
                Tuple.Create(new TimeSpan(0,5,6,7), "5 ч 6 мин"),
                Tuple.Create(new TimeSpan(0,0,6,7), "6 мин"),
                Tuple.Create(new TimeSpan(0,0,-5,35), "-4 мин"), //-5 + 0.52 мин
                Tuple.Create(new TimeSpan(0,0,0,7), "7 сек"),
                Tuple.Create(new TimeSpan(0,0,0,0,0), "Сейчас")
            };

            foreach (var tuple in data)
            {
                var actual = Helper.DateTimeToHuman(tuple.Item1, new CultureInfo("ru"));
                var expected = tuple.Item2;
                actual.Should().Be(expected);
            }
        }

        [Theory]
        [InlineData(4, 5, 6, 7, "4д 5ч", "-4д 5ч")]
        [InlineData(0, 10, 6, 7, "10ч", "-10ч")]
        [InlineData(0, 1, 6, 7, "1ч 6м", "-1ч 6м")]
        [InlineData(0, 0, 12, 7, "13м", "-12м")]

        public void DateTimeToHumanShort_AnyTimeSpan_ReturnsHumanReadableString(int days, int hours, int minutes,
            int seconds, string expected, string expectedNegative)
        {
            var timeStamp = new TimeSpan(days, hours, minutes, seconds);
            var actual = Helper.DateTimeToHumanShort(timeStamp, new CultureInfo("ru"));
            actual.Should().Be(expected);
            var actualNegative = Helper.DateTimeToHumanShort(timeStamp.Negate(), new CultureInfo("ru"));
            actualNegative.Should().Be(expectedNegative);

        }

        [Fact]
        public void Transliteration_CheckAndCleanRussianNumberTest()
        {
            var number = "0123456789-ABCEHKMOPTXY;abcehkmoptxy_АВСЕНКМОРТХУ,авсенкмортху";
            var cleaned = number.CheckAndCleanRussianNumber();
            cleaned.Should().BeEquivalentTo("0123456789ABCEHKMOPTXYABCEHKMOPTXYABCEHKMOPTXYABCEHKMOPTXY");

            var number2 = "Ю111ЫЭ77";
            number2.CheckAndCleanRussianNumber().Should().BeNull();
        }

        [Fact]
        public void ClassCategory_TxtCategoryFullNameTest()
        {
            var str = Helper.TxtCategoryFullName((CategoryFlags)0b1111111111, false);
            str.Should().Be("ЭКОНОМ;КОМФОРТ;БИЗНЕС;МИНИВЭН;ЛИМУЗИН;VIP;ГРУЗ;УНИВЕРСАЛ;АВТОБУС;КОМФОРТ+");
        }
        
         
    }
}
