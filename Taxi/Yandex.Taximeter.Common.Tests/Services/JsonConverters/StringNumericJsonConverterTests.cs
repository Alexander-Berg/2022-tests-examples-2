using FluentAssertions;
using Newtonsoft.Json;
using Xunit;
using Xunit.Sdk;
using Yandex.Taximeter.Core.Services.JsonConverters;

namespace Yandex.Taximeter.Common.Tests.Services.JsonConverters
{
    public class StringNumericJsonConverterTests
    {
        [Fact]
        public void ReadJson_Null_ReturnsZero()
        {
            var obj = JsonConvert.DeserializeObject<TestDecimal>(@"{""val"":null}");
            obj.Val.Should().Be(0m);
        }

        [Fact]
        public void ReadJson_EmptyStr_ReturnsZero()
        {
            var obj = JsonConvert.DeserializeObject<TestDecimal>(@"{""val"":""""}");
            obj.Val.Should().Be(0m);
        }

        [Fact]
        public void ReadJson_NumericStr_ParsesStr()
        {
            var obj = JsonConvert.DeserializeObject<TestDecimal>(@"{""val"":""-100.0025""}");
            obj.Val.Should().Be(-100.0025m);
        }

        [Fact]
        public void ReadJson_ExpStr_ParsesStr()
        {
            var obj = JsonConvert.DeserializeObject<TestDecimal>(@"{""val"":""2E3""}");
            obj.Val.Should().Be(2000);
        }
        
        [Fact]
        public void ReadJson_Float_Parses()
        {
            var obj = JsonConvert.DeserializeObject<TestDecimal>(@"{""val"":123.45}");
            obj.Val.Should().Be(123.45m);
        }
        
        [Fact]
        public void ReadJson_Integer_Parses()
        {
            var obj = JsonConvert.DeserializeObject<TestDecimal>(@"{""val"":123}");
            obj.Val.Should().Be(123);
        }

        [Fact]
        public void ReadJson_FloatAsInteger_ThrowsException()
        {
            Assert.Throws<JsonSerializationException>(() =>
                JsonConvert.DeserializeObject<TestInteger>(@"{""val"":123.45}"));
        }

        [Theory]
        [InlineData(0)]
        [InlineData(10)]
        [InlineData(-10)]
        public void WriteJson_AnyValue_WritesStr(int val)
        {
            var obj = JsonConvert.DeserializeObject<TestDecimal>(
                JsonConvert.SerializeObject(new TestDecimal {Val = val}));

            obj.Val.Should().Be(val);
        }

        private class TestDecimal
        {
            [JsonConverter(typeof(StringNumericJsonConverter))]
            [JsonProperty("val")]
            public decimal Val { get; set; }
        }
        
        private class TestInteger
        {
            [JsonConverter(typeof(StringNumericJsonConverter))]
            [JsonProperty("val")]
            public int Val { get; set; }
        }
    }
}
