using System.Collections.Generic;
using FluentAssertions;
using Newtonsoft.Json;
using Xunit;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Services.JsonConverters;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Services.JsonConverters
{
    public enum TestEnum
    {
        [DbValue("fired")]
        Fired = 1,

        [DbValue("not_working")]
        NotWorking = 2,

        NoDbValue = 3
    }

    public class EnumWithDbValueConverterTest
    {
        private readonly EnumWithDbValueConverter<TestEnum> _converter = new EnumWithDbValueConverter<TestEnum>();

        [Fact]
        public void ReadJson_Tests()
        {
            _converter.ReadJson("\"fired\"").Should().Be(TestEnum.Fired);
        }

        [Theory]
        [InlineData("")]
        [InlineData("null")]
        [InlineData("1")]
        [InlineData("\"asd\"")]
        [InlineData("\"NoDbValue\"")]
        public void ReadJson_InvalidInput(string json)
        {
            Assert.Throws<JsonSerializationException>(() => _converter.ReadJson(json));
        }

        [Fact]
        public void WriteJsonTests()
        {
            _converter.WriteJson(TestEnum.NotWorking).Should().Be("\"not_working\"");
        }

        [Theory]
        [InlineData(null)]
        [InlineData(1)]
        [InlineData(TestEnum.NoDbValue)]
        public void WriteJson_InvalidInput(object obj)
        {
            Assert.Throws<JsonSerializationException>(() => _converter.WriteJson(obj));
        }
    }
}

