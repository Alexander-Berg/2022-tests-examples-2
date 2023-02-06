using FluentAssertions;
using Newtonsoft.Json;
using Xunit;
using Xunit.Sdk;
using Yandex.Taximeter.Core.Services.Driver;
using Yandex.Taximeter.Core.Services.JsonConverters;

namespace Yandex.Taximeter.Common.Tests.Services.JsonConverters
{
    public class DbUuidJsonConverterTest
    {
        [Fact]
        public void TestDriverIdJsonConverter_Null_ReturnsNull()
        {
            var driverId = JsonConvert.DeserializeObject<DriverId>("null", new DbUuidJsonConverter());
            driverId.Should().BeNull();
        }
        
        [Fact]
        public void TestDriverIdJsonConverter_String_ReturnsDriverId()
        {
            //TODO: implement json converter
            var driverId = JsonConvert.DeserializeObject<DriverId>("'db_driver'", new DbUuidJsonConverter());
            driverId.Should().Be(new DriverId("db", "driver"));
        }
        
        [Fact]
        public void TestDriverIdJsonConverter_String_ThrowsException()
        {
            Assert.Throws<JsonSerializationException>(() => JsonConvert.DeserializeObject<DriverId>("'db_'", new DbUuidJsonConverter()));
            Assert.Throws<JsonSerializationException>(() => JsonConvert.DeserializeObject<DriverId>("'_driver'", new DbUuidJsonConverter()));
            Assert.Throws<JsonSerializationException>(() => JsonConvert.DeserializeObject<DriverId>("'INVALID'", new DbUuidJsonConverter()));
        }
        
        [Fact]
        public void TestDriverIdJsonConverter_Object_ReturnsDriverId()
        {
            var driverId = JsonConvert.DeserializeObject<DriverId>("{'db':'db', 'driver':'driver'}", new DbUuidJsonConverter());
            driverId.Should().Be(new DriverId("db", "driver"));
        }
        
        [Fact]
        public void TestDriverIdJsonConverter_Object_ThrowsException()
        {
            Assert.Throws<JsonSerializationException>(() => JsonConvert.DeserializeObject<DriverId>("{'db':'db'}", new DbUuidJsonConverter()));
            Assert.Throws<JsonSerializationException>(() => JsonConvert.DeserializeObject<DriverId>("{'driver':'driver'}", new DbUuidJsonConverter()));
            Assert.Throws<JsonSerializationException>(() => JsonConvert.DeserializeObject<DriverId>("{'field':'value'}", new DbUuidJsonConverter()));
        }

        [Fact]
        public void TestDriverIdJsonConverter_InvalidToken()
        {
            Assert.Throws<JsonSerializationException>(() => JsonConvert.DeserializeObject<DriverId>("true", new DbUuidJsonConverter()));
            Assert.Throws<JsonSerializationException>(() => JsonConvert.DeserializeObject<DriverId>("0", new DbUuidJsonConverter()));
            Assert.Throws<JsonSerializationException>(() => JsonConvert.DeserializeObject<DriverId>("0.0", new DbUuidJsonConverter()));
        }
    }
}