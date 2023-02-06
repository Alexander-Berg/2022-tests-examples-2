using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Code;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Car;

namespace Yandex.Taximeter.Common.Tests.Helpers
{
    public class CardHelperTests
    {
        [Theory]
        [InlineData("043601607#40817810254409357320#А331#ЛАЗАРЕВ",false)]
        [InlineData("6390 0240 9027 5989 66",true)]
        [InlineData("Карта, в которой 19 знаков: 6390 0240 9027 5989 657",true)]
        [InlineData("6390 0240 9027 5989", false)]
        [InlineData("5336а6900а6144а4321  Алексей Сергеевич" , true)]
        [InlineData("5469700013493448 сбер" , true)]
        [InlineData("5469700013493448" , true)]
        [InlineData("1234 5469-7000-1349-3448 сбер" , true)]
        [InlineData("1234 5469    -   7000-1349-3448 сбер" , true)]
        [InlineData("1234 5469 а вот 7000-1349-3448 сбер" , false)]
        [InlineData("1234 5469-7000-1349-3449 Некорректный сбер" , false)]
        [InlineData("Разбивка долга 6000 с 22.11/ разбивка долга 4000 16 дней по 250/Разбивка долга 6250/ 250 на 25 дней " , false)]

        public void HasCardNumberTest(string InputString, bool expectedResult)
        {
         
            var isCard = CardHelper.HasCardNumber(InputString);
            isCard.Should().Be(expectedResult);

        }
        
        [Fact]
        public void HasCardNumberLongStringTest()
        {
           
            var InputString = new StringBuilder();
            for (var i = 0; i < 1000; i++)
                InputString.Append("1м");
            var isCard = CardHelper.HasCardNumber(InputString.ToString());
            isCard.Should().Be(false);

        }
    }
}
