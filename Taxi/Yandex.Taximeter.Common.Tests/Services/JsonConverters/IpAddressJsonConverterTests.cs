using System.Collections.Generic;
using System.Net;
using FluentAssertions;
using Newtonsoft.Json;
using Xunit;
using Yandex.Taximeter.Core.Models.User;

namespace Yandex.Taximeter.Common.Tests.Models.User
{
    public class IpAddressJsonConverterTests
    {
        private static readonly JsonSerializerSettings SerializerSettings = new JsonSerializerSettings
        {
            Converters = new List<JsonConverter> {new IpAddressJsonConverter()}
        };

        [Fact]
        public void Serialization_NullAddress()
        {
            var deserialized = SerializeAndDeserialize(null);
            deserialized.Should().Be(null);
        }

        [Theory]
        [InlineData("127.0.0.1")]
        [InlineData("2a02:6b8:b010:6f::40")]
        [InlineData("::1")]
        public void Serialization_ValidAddress(string ipAddress)
        {
            var address = IPAddress.Parse(ipAddress);
            var deserialized = SerializeAndDeserialize(address);
            deserialized.Should().Be(address);
        }

        [Theory]
        [InlineData(-1298478848, "178.154.201.0")]
        [InlineData(-2101269760, "130.193.43.0")]
        public void Deserialization_IntValue(int ipNumber, string expectedAddr)
        {
            var deserialized = JsonConvert.DeserializeObject<IPAddress>(ipNumber.ToString(), SerializerSettings);
            deserialized.Should().Be(IPAddress.Parse(expectedAddr));
        }

        [Fact]
        public void Deserialization_InvalidStringValue()
        {
            var deserialized = JsonConvert.DeserializeObject<IPAddress>("\"-fdsfsfsfdsfds-fsdf-fds\"", SerializerSettings);
            deserialized.Should().Be(null);
        }

        private static IPAddress SerializeAndDeserialize(IPAddress address)
        {
            var serialized = JsonConvert.SerializeObject(address, SerializerSettings);
            return JsonConvert.DeserializeObject<IPAddress>(serialized, SerializerSettings);
        }
    }
}
