using System.Threading.Tasks;
using System.Collections.Generic;
using FluentAssertions;
using MongoDB.Driver;
using Moq;
using Xunit;
using Yandex.Taximeter.Core.Clients.Personal;
using Yandex.Taximeter.Core.Redis;
using Yandex.Taximeter.Core.Repositories;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Country;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Park;
using Yandex.Taximeter.Core.Repositories.MongoDB.Dtos.Driver;
using Yandex.Taximeter.Core.Repositories.MongoDB.Dtos.Park;
using Yandex.Taximeter.Core.Services.Authorization;
using Yandex.Taximeter.Core.Services.Car;
using Yandex.Taximeter.Core.Services.Culture;
using Yandex.Taximeter.Core.Services.Driver;
using Yandex.Taximeter.Core.Services.Driver.Import;
using Yandex.Taximeter.Core.Services.Geography;
using Yandex.Taximeter.Core.Services.SelfRegistration;
using Yandex.Taximeter.Test.Utils.Fakes;

namespace Yandex.Taximeter.Common.Tests.Services.SelfReg
{
    public class SelfRegistrationServiceTests
    {

        private readonly FakeGlobalSettingsService _fakeGlobalSettingsService = new FakeGlobalSettingsService();
        private readonly Mock<ICountryRepository> _countryRepository = new Mock<ICountryRepository>();
        private readonly Mock<ICityRepository> _cityRepository = new Mock<ICityRepository>();
        private readonly Mock<IParkRepository> _parkRepository = new Mock<IParkRepository>();

        private readonly SelfRegistrationService _selfRegistrationService;

        public SelfRegistrationServiceTests()
        {
            _countryRepository
                .Setup(x => x.GetCountryIdByRegionAsync("RU"))
                .ReturnsAsync(Country.RUSSIA_ID);

            _countryRepository
                .Setup(x => x.GetCountryIdByRegionAsync("UA"))
                .ReturnsAsync(Country.UKRAINE_ID);

            _countryRepository
                .Setup(x => x.GetCountryIdByRegionAsync("AZ"))
                .ReturnsAsync(Country.AZERBAIJAN_ID);

            _cityRepository
                .Setup(x => x.GetCitiesCacheAsync())
                .ReturnsAsync(new Dictionary<string, CityCacheEntry>
                {
                    ["МОСКВА"] =
                        new CityCacheEntry
                        {
                            Country = Country.RUSSIA_NAME,
                            CountryId = Country.RUSSIA_ID,
                            Lat = 55.75,
                            Lon = 37.62,
                            Name = "Москва",
                            Geoarea = "moscow"
                        },
                    ["ПОДОЛЬСК"] =
                        new CityCacheEntry
                        {
                            Country = Country.RUSSIA_NAME,
                            CountryId = Country.RUSSIA_ID,
                            Lat = 55.43,
                            Lon = 37.54,
                            Name = "Подольск",
                            Geoarea = "moscow"
                        },
                    ["КИЕВ"] =
                        new CityCacheEntry
                        {
                            Country = "Украина",
                            CountryId = Country.UKRAINE_ID,
                            Lat = 40.18,
                            Lon = 44.51,
                            Name = "Киев",
                            Geoarea = "kiev"
                        },
                    ["БАКУ"] =
                        new CityCacheEntry
                        {
                            Country = Country.AZERBAIJAN_NAME,
                            CountryId = Country.AZERBAIJAN_ID,
                            Lat = 40.37,
                            Lon = 49.83,
                            Name = "Баку",
                            Geoarea = "baku"
                        }
                });

            _parkRepository
                .Setup(x => x.FindAsync<ParkDriverHiringDto>(It.IsAny<FilterDefinition<ParkDoc>>(), null, 0,QueryMode.Slave))
                .ReturnsAsync(new List<ParkDriverHiringDto>
                {
                    new ParkDriverHiringDto
                    {
                        DriverHiring =
                            new ParkDriverHiring {Cities = new HashSet<string> {"Москва", "Подольск", "Мордор"}}
                    },
                    new ParkDriverHiringDto
                    {
                        DriverHiring =
                            new ParkDriverHiring {Cities = new HashSet<string> {"Ереван"}}
                    },
                    new ParkDriverHiringDto
                    {
                        DriverHiring =
                            new ParkDriverHiring {Cities = new HashSet<string> {"Баку"}}
                    }
                });

            _parkRepository
                .Setup(x => x.FindAsync<ParkSelfRegDto>(It.IsAny<FilterDefinition<ParkDoc>>(), null, 0,QueryMode.Slave))
                .ReturnsAsync(new List<ParkSelfRegDto>
                {
                    new ParkSelfRegDto
                    {
                        Id = "Park1"
                    },
                    new ParkSelfRegDto
                    {
                        Id = "Park2"
                    },
                    new ParkSelfRegDto
                    {
                        Id = "Park3"
                    }
                });

            _selfRegistrationService = new SelfRegistrationService(_fakeGlobalSettingsService, Mock.Of<ISmsService>(),
                Mock.Of<ICarMarkModelService>(), Mock.Of<ISelfRegistrationRepository>(), null,
                _countryRepository.Object, _cityRepository.Object, _parkRepository.Object, Mock.Of<ICarRepository>(),
                Mock.Of<IDriverRepository>(), Mock.Of<IRedisManagerAsync>(), Mock.Of<IDriverImportService>(),
                new FakeLogger<SelfRegistrationService>(), Mock.Of<ICultureService>(), Mock.Of<IDriverReferralsGateway>(),
                Mock.Of<IPersonalDataGateways>());
        }

        [Theory]
        [InlineData(60, 40, "RU", "Москва")]
        [InlineData(40, 40, "RU", "Подольск")]
        [InlineData(60, 40, "", "Москва")]
        [InlineData(40, 40, "", "Баку")]
        public async void SelfRegCityTest(double lat, double lon, string country, string City)
        {
            var culture = new TaximeterCultureInfo("ru", CultureCountry.Default);
            var nearestCity = await _selfRegistrationService.GetNearestCityAsync(country, lat, lon, culture);
            nearestCity.Id.Should().Be(City);
        }

        [Theory]
        [InlineData(60, 40, "UA")]
        public async void SelfRegCityNoRegTest(double lat, double lon, string country)
        {
            var culture = new TaximeterCultureInfo("ru", CultureCountry.Default);
            var nearestCity = await _selfRegistrationService.GetNearestCityAsync(country, lat, lon, culture);
            nearestCity.Should().BeNull();
        }

        [Theory]
        [InlineData(60, 40, "RU", "Баку")]
        [InlineData(60, 40, "", "Баку")]
        [InlineData(60, 40, "AZ", "Баку")]
        public async void AzSelfRegCityTest(double lat, double lon, string country, string City)
        {
            var culture = new TaximeterCultureInfo("ru", CultureCountry.Azerbaijan);
            var nearestCity = await _selfRegistrationService.GetNearestCityAsync(country, lat, lon, culture);
            nearestCity.Id.Should().Be(City);
        }

        private static readonly List<DriverCommonDto> driverDtos = new List<DriverCommonDto>
        {
            new DriverCommonDto {ParkId = "Park1"},
            new DriverCommonDto {ParkId = "Park3"}
        };

        [Fact]
        public async void GetAvailiableHiringParksTest()
        {
            var hiringParks = await _selfRegistrationService.GetAvailableHiringParks("Москва", driverDtos);
            hiringParks.Should().NotBeNull();
            hiringParks.Length.Should().Be(1);
        }

        [Fact]
        public async void GetAvailiableHiringParksTestThrow()
        {
            System.Func<Task> act = async () =>
            {
                await _selfRegistrationService.GetAvailableHiringParks("", driverDtos);
            };
            act.Should().Throw<System.Exception>().WithMessage("empty city");
        }
    }
}
