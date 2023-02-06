using System.Net;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Models.User;

namespace Yandex.Taximeter.Common.Tests.Models.User
{
    public class IpRangeTests
    {
        [Fact]
        public void IsValid_BordersNull_ReturnsTrue()
        {
            var ipRange = new IpRange();
            var address = IPAddress.Parse("127.0.0.1");
            ipRange.IsValid(address).Should().BeTrue();
        }

        [Fact]
        public void IsValid_AddressNull_ReturnsFalse()
        {
            var ipRange = new IpRange
            {
                Start = IPAddress.Parse("127.0.0.1"),
                End = IPAddress.Parse("127.0.0.255")
            };
            ipRange.IsValid(null).Should().BeFalse();
        }

        [Fact]
        public void IsValid_FallsOutOfBorders_ReturnsFalse()
        {
            var ipRange = new IpRange
            {
                Start = IPAddress.Parse("127.1.1.1")
            };
            var address = IPAddress.Parse("127.1.0.25");
            ipRange.IsValid(address).Should().BeFalse();
        }

        [Fact]
        public void IsValid_WithinBounds_ReturnsTrue()
        {
            var ipRange = new IpRange
            {
                Start = IPAddress.Parse("127.1.1.0"),
                End = IPAddress.Parse("127.1.1.255"),
            };
            var address = IPAddress.Parse("127.1.1.25");
            ipRange.IsValid(address).Should().BeTrue();
        }
    }
}