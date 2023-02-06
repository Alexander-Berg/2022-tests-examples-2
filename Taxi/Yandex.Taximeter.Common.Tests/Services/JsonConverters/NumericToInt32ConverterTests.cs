using FluentAssertions;
using Newtonsoft.Json;
using Xunit;
using Yandex.Taximeter.Core.Services.JsonConverters;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Services.JsonConverters
{
    public class NumericToInt32ConverterTests
    {
        private readonly NumericToInt32Converter _converter = new NumericToInt32Converter();

        [Theory]
        [InlineData("null", null)]
        [InlineData("0", 0)]
        [InlineData("123", 123)]
        [InlineData("43234.56", 43235)]
        public void ReadJson_Tests(string json, object expectedParsed)
        {
            var result = _converter.ReadJson(json);
            result.Should().Be(expectedParsed);
        }

        [Fact]
        public void ReadJson_InvalidInput()
        {
            Assert.Throws<JsonSerializationException>(() => _converter.ReadJson("\"ffds\""));
        }

        [Theory]
        [InlineData(0, "0")]
        [InlineData(123, "123")]
        [InlineData(43.23, "43")]
        public void WriteJsonTests(object input, string expectedJson)
        {
            var result = _converter.WriteJson(input);
            result.Should().Be(expectedJson);
        }
    }
}
