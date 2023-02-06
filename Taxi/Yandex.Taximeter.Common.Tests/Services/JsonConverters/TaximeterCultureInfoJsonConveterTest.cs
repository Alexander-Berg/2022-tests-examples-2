using FluentAssertions;
using Newtonsoft.Json;
using Xunit;
using Yandex.Taximeter.Core.Services.Culture;
using Yandex.Taximeter.Core.Services.JsonConverters;

namespace Yandex.Taximeter.Common.Tests.Services.JsonConverters
{
    public class TaximeterCultureInfoJsonConveterTest
    {
        [Fact]
        public void TestDeserialize_Null_ReturnsNull()
        {
            var tci = JsonConvert.DeserializeObject<TaximeterCultureInfo>("null", new TaximeterCultureInfoJsonConverter());
            tci.Should().BeNull();
        }
        
        [Fact]
        public void TestDeserialize_NameOnly_ReturnsDefaultCountry()
        {
            var tci = JsonConvert.DeserializeObject<TaximeterCultureInfo>("\"ru-RU\"", new TaximeterCultureInfoJsonConverter());
            tci.Name.Should().Be("ru-RU");
            tci.Country.Should().Be(CultureCountry.Default);
        }
        
        [Fact]
        public void TestDeserialize_NameAndCountry_ReturnsCountry()
        {
            var tci = JsonConvert.DeserializeObject<TaximeterCultureInfo>("\"ru-RU:Azerbaijan\"", new TaximeterCultureInfoJsonConverter());
            tci.Name.Should().Be("ru-RU");
            tci.Country.Should().Be(CultureCountry.Azerbaijan);
        }
        
        [Fact]
        public void TestSerialize_Null_ReturnsNull()
        {
            var json = JsonConvert.SerializeObject(null, new TaximeterCultureInfoJsonConverter());
            json.Should().Be("null");
        }
        
        [Fact]
        public void TestSerialize_NameOnly_ReturnsDefaultCountry()
        {
            var json = JsonConvert.SerializeObject(new TaximeterCultureInfo("ru-RU"), new TaximeterCultureInfoJsonConverter());
            json.Should().Be("\"ru-RU\"");
        }
        
        [Fact]
        public void TestSerialize_NameAndCountry_ReturnsCountry()
        {
            var json = JsonConvert.SerializeObject(new TaximeterCultureInfo("ru-RU", CultureCountry.Azerbaijan), new TaximeterCultureInfoJsonConverter());
            json.Should().Be("\"ru-RU:Azerbaijan\"");
        }
    }
}
