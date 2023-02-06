using System.Collections.Generic;
using System.Diagnostics.CodeAnalysis;
using System.Linq;
using FluentAssertions;
using Moq;
using Xunit;
using Yandex.Taximeter.Core.Repositories;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.City;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Country;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Driver;
using Yandex.Taximeter.Core.Repositories.MongoDB.Dtos.Driver;
using Yandex.Taximeter.Core.Repositories.MongoDB.Dtos.Park;
using Yandex.Taximeter.Core.Services.Culture;
using Yandex.Taximeter.Core.Services.Driver;
using Yandex.Taximeter.Core.Services.Geography;
using Yandex.Taximeter.Core.Services.Settings;
using Yandex.Taximeter.Test.Utils.Fakes;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Services.Culture
{
    [SuppressMessage("ReSharper", "ExplicitCallerInfoArgument")]
    public class CultureServiceTests
    {
        private readonly FakeGlobalSettingsService _fakeGlobalSettingsService = new FakeGlobalSettingsService();
        private readonly Mock<ICountryRepository> _countryRepository = new Mock<ICountryRepository>();
        private readonly Mock<IParkRepository> _parkRepository = new Mock<IParkRepository>();
        private readonly Mock<ICityRepository> _cityRepository = new Mock<ICityRepository>();
        private readonly Mock<IDriverRepository> _driverRepository = new Mock<IDriverRepository>();
        private readonly CultureService _cultureService;

        public CultureServiceTests()
        {
            _fakeGlobalSettingsService.GlobalSettings = new GlobalSettings
            {
                DefaultSupportedLocales = new List<string> {"ru", "en", "et", "az"}
            };
            _countryRepository
                .Setup(x => x.GetAsync(Country.RUSSIA_NAME))
                .ReturnsAsync(new Country());
            _countryRepository
                .Setup(x => x.GetAsync(Country.RUSSIA_ID))
                .ReturnsAsync(new Country());
            _countryRepository
                .Setup(x => x.GetAsync(It.IsAny<string>()))
                .ReturnsAsync((string id) =>
                {
                    switch (id)
                    {
                        case Country.RUSSIA_NAME:
                        case Country.RUSSIA_ID:
                            return new Country
                            {
                                SupportedLocales = new List<string>()
                            }; //country without overriden settings
                        case Country.AZERBAIJAN_NAME:
                        case Country.AZERBAIJAN_ID:
                            return new Country //country with overriden settings
                            {
                                Id = "aze",
                                DefaultLocale = "az",
                                SupportedLocales = new List<string> {"ru", "en", "az", "ro"}
                            };
                        default:
                            return null;
                    }
                });
            _cityRepository
                .Setup(x => x.GetCountryAsync(CityDoc.ID_YEREVAN))
                .ReturnsAsync(Country.AZERBAIJAN_NAME);

            _cultureService = new CultureService(
                _fakeGlobalSettingsService, 
                _countryRepository.Object,
                _parkRepository.Object,
                _driverRepository.Object,
                _cityRepository.Object,
                new FakeLogger<CultureService>());
        }

        [Fact]
        public async void GetGlobalAsync_Tests()
        {
            var culture = await _cultureService.GetGlobalAsync("ro");
            culture.Name.Should().Be(DriverDoc.DEFAULT_LOCALE, "config does not contain ro");
            
            culture = await _cultureService.GetGlobalAsync("en");
            culture.Name.Should().Be("en", "config contains en");
        }

        [Fact]
        public async void GetAsync_LocaleSupported_ReturnsRequestedLocale()
        {
            var culture = await _cultureService.GetAsync("en", Country.RUSSIA_ID);
            culture.Name.Should().Be("en");

            culture = await _cultureService.GetAsync("en", Country.AZERBAIJAN_ID);
            culture.Name.Should().Be("en");
        }

        [Fact]
        public async void GetAsync_LocaleNotSupported_ReturnsCountryDefaultLocale()
        {
            var culture = await _cultureService.GetAsync("ro", Country.RUSSIA_ID);
            culture.Name.Should().Be(DriverDoc.DEFAULT_LOCALE, "fallback to global default locale");

            culture = await _cultureService.GetAsync("ro", Country.AZERBAIJAN_ID);
            culture.Name.Should().Be("az", "ro is not in global supported list, thus fallback");

            culture = await _cultureService.GetAsync("et", Country.AZERBAIJAN_ID);
            culture.Name.Should().Be("az", "et is not in country supported list, thus fallback");

            culture = await _cultureService.GetAsync("ky", Country.AZERBAIJAN_ID);
            culture.Name.Should().Be("az",
                "ky is not present in both global and country supported list, thus fallback");
        }

        [Fact]
        public async void GetCountryDefaultAsync_DefaultNotOverriden_ReturnsGlobalDefault()
        {
            var culture = await _cultureService.GetCountryDefaultAsync(Country.RUSSIA_ID);
            culture.Should().Be(new TaximeterCultureInfo(DriverDoc.DEFAULT_LOCALE, CultureCountry.Default));
        }

        [Fact]
        public async void GetCountryDefaultAsync_DefaultOverriden_ReturnsOverriden()
        {
            var culture = await _cultureService.GetCountryDefaultAsync(Country.AZERBAIJAN_ID);
            culture.Should().Be(new TaximeterCultureInfo("az", CultureCountry.Azerbaijan));
        }

        [Fact]
        public async void IsSupportedAsync_Tests()
        {
            var isSupported = await _cultureService.IsSupportedAsync("ro", Country.AZERBAIJAN_ID);
            isSupported.Should().BeFalse("not supported globally");

            isSupported = await _cultureService.IsSupportedAsync("et", Country.AZERBAIJAN_ID);
            isSupported.Should().BeFalse("not supported for azerbaijan");

            isSupported = await _cultureService.IsSupportedAsync("az", Country.AZERBAIJAN_ID);
            isSupported.Should().BeTrue();
        }

        [Fact]
        public async void ListAsync_LocalesNotOverriden_ReturnsFromConfig()
        {
            var cultures = await _cultureService.ListAsync(Country.RUSSIA_ID);
            cultures.Select(x => x.Name).Should().BeEquivalentTo(
                _fakeGlobalSettingsService.GlobalSettings.DefaultSupportedLocales);
            cultures.All(x => x.Country == CultureCountry.Default).Should().BeTrue();
        }

        [Fact]
        public async void ListAsync_LocalesOverriden_ReturnsIntersectionOfLocales()
        {
            var cultures = await _cultureService.ListAsync(Country.AZERBAIJAN_ID);
            cultures.Select(x => x.Name).Should().BeEquivalentTo("ru", "en", "az");
            cultures.All(x => x.Country == CultureCountry.Azerbaijan).Should().BeTrue();
        }

        [Fact]
        public async void GetParkCultureAsync_ParkNotFound_ReturnsDefaultCulture()
        {
            var culture = await _cultureService.GetParkCultureAsync(TestUtils.NewId());
            culture.Should().Be(new TaximeterCultureInfo(DriverDoc.DEFAULT_LOCALE, CultureCountry.Default));
        }

        [Theory]
        [InlineData("", "az", CultureCountry.Azerbaijan)]
        [InlineData("et", "az", CultureCountry.Azerbaijan)]
        [InlineData("ru", "ru", CultureCountry.Azerbaijan)]
        public async void GetParkCultureAsync_ParkFound_ReturnsParkOrCountryDefaultCulture(
            string parkLocale, string resultLocale, CultureCountry resultCountry)
        {
            var parkId = TestUtils.NewId();
            SetupPark(id: parkId, city: CityDoc.ID_YEREVAN, locale: parkLocale);

            var culture = await _cultureService.GetParkCultureAsync(parkId);

            culture.Should().Be(new TaximeterCultureInfo(resultLocale, resultCountry));
        }

        [Fact]
        public async void GetDriverCultureAsync_ParkNotFound_ReturnsDefaultCulture()
        {
            var driverId = TestUtils.NewDriverId();
            SetupDriver(id: driverId, locale: "en");
            
            var culture = await _cultureService.GetDriverCultureAsync(driverId);

            culture.Should().Be(new TaximeterCultureInfo(DriverDoc.DEFAULT_LOCALE, CultureCountry.Default));
        }

        [Theory]
        [InlineData(null, null, "az", CultureCountry.Azerbaijan)] // fallback to country default locale
        [InlineData("ru", null, "ru", CultureCountry.Azerbaijan)] // fallback to park locale
        [InlineData("ru", "en", "en", CultureCountry.Azerbaijan)] // use driver locale
        public async void GetDriverCulureAsync_ParkAndDriverFound_ReturnsDriverOrParkOrCountryLocale(
            string parkLocale, string driverLocale, string resultLocale, CultureCountry resultCultureCountry)
        {
            var driverId = TestUtils.NewDriverId();
            SetupPark(id: driverId.Db, city: CityDoc.ID_YEREVAN, locale: parkLocale);
            SetupDriver(id: driverId, locale: driverLocale);

            var culture = await _cultureService.GetDriverCultureAsync(driverId);

            culture.Should().Be(new TaximeterCultureInfo(resultLocale, resultCultureCountry));
        }

        private void SetupDriver(DriverId id, string locale)
        {
            _driverRepository
                .Setup(x => x.GetAsync<DriverLocaleDto>(id.Db, id.Driver, It.IsAny<QueryMode>(),
                    It.IsAny<string>(), It.IsAny<string>(), It.IsAny<int>()))
                .ReturnsAsync(new DriverLocaleDto
                {
                    DriverId = id.Driver,
                    ParkId = id.Db,
                    Locale = locale
                });
        }

        private void SetupPark(string id, string city, string locale)
        {
            _parkRepository
                .Setup(x => x.GetDtoAsync<ParkLocaleDto>(id, It.IsAny<QueryMode>()))
                .ReturnsAsync(new ParkLocaleDto
                {
                    City = city,
                    Locale = locale
                });
        }
    }
}