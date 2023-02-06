using System;
using System.Text;
using System.Threading.Tasks;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Integration.Tests.Fixtures;

namespace Yandex.Taximeter.Integration.Tests.Helper
{
    public class DriverHelperTests : IClassFixture<FatFixture>
    {
        private readonly FatFixture _fixture;

        public DriverHelperTests(FatFixture fixture)
        {
            _fixture = fixture;
        }

        [Fact]
        public void AuthTokenDecodingTest()
        {
            var token = "Ri6mVvj1YK7wbCWKziecwrnGBqBwNESFphc0S1XOnCYVDSs9v4EGoWlsFp2SiOfxc2mZRJCriwLw4LRZYFS31lgYH0YqNZB483j/9qr5VeaqTiogG2vNWmzynw90r4bJZ+gzHd1P7jRJvzWRRCcywL8Cvj29e5KkZlq5BiEWg/E=";
            var expectedBytes = "462EA656F8F560AEF06C258ACE279CC2B9C606A070344485A617344B55CE9C26150D2B3DBF8106A1696C169D9288E7F17369994490AB8B02F0E0B4596054B7D658181F462A359078F378FFF6AAF955E6AA4E2A201B6BCD5A6CF29F0F74AF86C967E8331DDD4FEE3449BF3591442732C0BF02BE3DBD7B92A4665AB906211683F1";

            var bytes = Convert.FromBase64String(token);
            var actualBytes = ByteArrayToString(bytes).ToUpperInvariant();

            actualBytes.Should().Be(expectedBytes);
        }

        public static string ByteArrayToString(byte[] ba)
        {
            var hex = new StringBuilder(ba.Length * 2);
            foreach (byte b in ba)
                hex.Append($"{b:x2}");
            return hex.ToString();
        }
    }
}
