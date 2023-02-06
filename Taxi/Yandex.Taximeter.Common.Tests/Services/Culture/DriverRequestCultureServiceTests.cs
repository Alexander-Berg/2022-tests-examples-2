using System.Collections.Generic;
using System.Threading.Tasks;
using FluentAssertions;
using Moq;
using Xunit;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Country;
using Yandex.Taximeter.Core.Services.Culture;
using Yandex.Taximeter.Core.Services.Driver;
using Yandex.Taximeter.Test.Utils.Fakes;
using Yandex.Taximeter.Test.Utils.Utils;

// ReSharper disable ExplicitCallerInfoArgument

namespace Yandex.Taximeter.Common.Tests.Services.Culture
{
    public class DriverRequestCultureServiсeTests
    {
        private readonly DriverId _driverId = TestUtils.NewDriverId();
        private readonly TaximeterCultureInfo _driverCulture = new TaximeterCultureInfo("sr");
        private readonly TaximeterCultureInfo _globalDefaultCultre = new TaximeterCultureInfo("ru");
        private readonly TaximeterCultureInfo _azDefaultCulture = new TaximeterCultureInfo("az", CultureCountry.Azerbaijan);

        private readonly IList<TaximeterCultureInfo> _globalSupported = new List<TaximeterCultureInfo>
        {
            new TaximeterCultureInfo("en"),
            new TaximeterCultureInfo("ru"),
            new TaximeterCultureInfo("az")
        };

        private readonly IList<TaximeterCultureInfo> _azSupported = new List<TaximeterCultureInfo>
        {
            new TaximeterCultureInfo("az", CultureCountry.Azerbaijan)
        };

        private readonly Mock<IDriverSessionService> _driverSessionService;
        private readonly IDriverRequestCultureService _service;

        public DriverRequestCultureServiсeTests()
        {
            _driverSessionService = new Mock<IDriverSessionService>();

            var cultureService = new Mock<ICultureService>();
            cultureService.Setup(x => x.GetCountryDefaultAsync(Country.AZERBAIJAN_ID))
                .Returns(new ValueTask<TaximeterCultureInfo>(_azDefaultCulture));
            cultureService.Setup(x => x.GetCountryDefaultAsync(null))
                .Returns(new ValueTask<TaximeterCultureInfo>(_globalDefaultCultre));
            cultureService.Setup(x => x.ListGlobalSupportedAsync())
                .Returns(new ValueTask<IList<TaximeterCultureInfo>>(_globalSupported));
            cultureService.Setup(x => x.ListAsync(Country.AZERBAIJAN_ID))
                .Returns(new ValueTask<IList<TaximeterCultureInfo>>(_azSupported));
            cultureService.Setup(x => x.GetGlobalDefault()).Returns(_globalDefaultCultre);
            cultureService.Setup(x => x.GetDriverCultureAsync(It.IsAny<DriverId>()))
                .ReturnsAsync(_driverCulture);

            _service = new DriverRequestCultureService(
                new FakeLogger<DriverRequestCultureService>(),
                _driverSessionService.Object,
                cultureService.Object);
        }

        [Fact]
        public async void SelectBestCultureAsync_NoHeaders_NoSession_ReturnsGlobalDefault()
        {
            var culture = await _service.SelectBestCultureAsync(new FakeHttpContext());

            culture.Should().Be(_globalDefaultCultre);
        }

        [Fact]
        public async void SelectBestCultureAsync_HasUserAgent_NoAcceptLanguage_NoSession_ReturnsCountryDefaultCulture()
        {
            var context = new FakeHttpContext();
            context.Request.Headers["X-Request-Platform"] = "android";
            context.Request.Headers["X-Request-Application-Version"] = "8.53 (543)";
            context.Request.Headers["X-Request-Platform-Version"] = "1.0.0";
            context.Request.Headers["X-Request-Application-Brand"] = "az";

            var culture = await _service.SelectBestCultureAsync(context);

            culture.Should().Be(_azDefaultCulture);
        }

        [Fact]
        public async void SelectBestCultureAsync_NoHeaders_HasSession_ReturnsDriverCulture()
        {
            var context = new FakeHttpContext();
            _driverSessionService.Setup(x => x.GetCurrentDriver(context)).Returns(_driverId);

            var culture = await _service.SelectBestCultureAsync(context);

            culture.Should().Be(_driverCulture);
        }

        [Fact]
        public async void SelectBestCultureAsync_HasHeaders_NoSession_ReturnsCountryCulture()
        {
            var context = new FakeHttpContext();
            context.Request.Headers["Accept-Language"] = "sr;q=0.9, en-us;q=0.8, az;q=0.7";
            context.Request.Headers["X-Request-Platform"] = "android";
            context.Request.Headers["X-Request-Application-Version"] = "8.53 (543)";
            context.Request.Headers["X-Request-Platform-Version"] = "1.0.0";
            context.Request.Headers["X-Request-Application-Brand"] = "az";

            var culture = await _service.SelectBestCultureAsync(context);

            culture.Should().Be(_azSupported[0]);
        }

        [Fact]
        public async void SelectBestCultureAsync_HasHeaders_HasSession_ReturnsHeadersCulture()
        {
            var context = new FakeHttpContext();
            context.Request.Headers["Accept-Language"] = "sr;q=0.9, en-us;q=0.8, az;q=0.7";
            context.Request.Headers["X-Request-Platform"] = "android";
            context.Request.Headers["X-Request-Application-Version"] = "8.53 (543)";
            context.Request.Headers["X-Request-Platform-Version"] = "1.0.0";
            context.Request.Headers["X-Request-Application-Brand"] = "az";
            _driverSessionService.Setup(x => x.GetCurrentDriver(context)).Returns(_driverId);

            var culture = await _service.SelectBestCultureAsync(context);

            culture.Should().Be(_azSupported[0]);
        }
    }
}
