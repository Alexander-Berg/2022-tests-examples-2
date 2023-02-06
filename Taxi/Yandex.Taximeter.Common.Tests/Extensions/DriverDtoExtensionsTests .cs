using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Repositories.MongoDB.Dtos.Driver;

namespace Yandex.Taximeter.Common.Tests.Extensions
{
    public class DriverDtoExtensionsTests
    {
        [Theory]
        [InlineData(null, null, "")]
        [InlineData(null, "A", "A")]
        [InlineData("0", null, "0")]
        [InlineData("", "", "")]
        [InlineData("", "АВСЕНКМОРТХУ", "ABCEHKMOPTXY")]
        [InlineData("01ОВ", "123123", "01OB123123")]
        [InlineData("01-ОВ", "123/123", "01OB123123")] // remove all non alpha-numberic
        [InlineData("ВОRЩ", "", "BORЩ")] // keep untranslatable chars (like Щ)
        public void Test_NormalizeLicense(string licenseSeries, string licenseNumber, string expected)
        {
            var result = DriverDtoExtensions.NormalizeLicense(licenseSeries, licenseNumber);
            
            result.Should().Be(expected);
        }
    }
}
