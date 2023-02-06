using System;
using System.Threading.Tasks;
using FluentAssertions;
using Moq;
using Xunit;
using Yandex.Taximeter.Core.Models.Access;
using Yandex.Taximeter.Core.Models.User;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.City;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Country;
using Yandex.Taximeter.Core.Services.Geography;
using Yandex.Taximeter.Core.Services.Settings;
using Yandex.Taximeter.Test.Utils.Fakes;

namespace Yandex.Taximeter.Common.Tests.Models.Access
{
    public class DriverAccessTests
    {
        private readonly string _parkId1 = Guid.NewGuid().ToString("N");
        private readonly string _parkId2 = Guid.NewGuid().ToString("N");
        private readonly string _parkCity = "Москва";

        private readonly Mock<ICountryRepository> _countryRepository = new Mock<ICountryRepository>();
        private readonly Mock<ICountryService> _countryService = new Mock<ICountryService>();
        private readonly Mock<ICityRepository> _cityRepository = new Mock<ICityRepository>();

        public DriverAccessTests()
        {
            _countryRepository
                .Setup(x => x.GetAsync(Country.RUSSIA_NAME))
                .ReturnsAsync(new Country
                {
                    Id = Country.RUSSIA_ID,
                    Name = Country.RUSSIA_NAME
                });

            _countryRepository
                .Setup(x => x.GetAsync(Country.RUSSIA_ID))
                .ReturnsAsync(new Country
                {
                    Id = Country.RUSSIA_ID,
                    Name = Country.RUSSIA_NAME
                });

            _cityRepository
                .Setup(x => x.GetCountryAsync(CityDoc.ID_MOSCOW))
                .ReturnsAsync(Country.RUSSIA_NAME);

            _cityRepository
                .Setup(x => x.GetCountryIdAsync(CityDoc.ID_MOSCOW))
                .ReturnsAsync(Country.RUSSIA_ID);

            _countryService
                .Setup(x => x.GetCountryByParkAsync(_parkId1))
                .ReturnsAsync(new Country
                {
                    Id = Country.RUSSIA_ID,
                    Name = Country.RUSSIA_NAME
                });

            _countryService
                .Setup(x => x.GetCountryByParkAsync(_parkId2))
                .ReturnsAsync(new Country
                {
                    Id = Country.RUSSIA_ID,
                    Name = Country.RUSSIA_NAME
                });
        }

        [Fact]
        public async Task EditNameLicenceForNewDriverEnabledAndForOldDriverDisabled()
        {
            var driverAccess = new DriverAccess();
            var userSession = new UserSession
            {
                db = _parkId1,
                db_city = _parkCity,
                IsDriverPartner = false
            };

            var settings = new FakeGlobalSettingsService
            {
                GlobalSettings = new GlobalSettings
                {
                    DenyEditDriverNameAndLicense = new DriverEditSettings
                    {
                        Enable = true,
                        GraceDays = 3
                    }
                }
            };

            await driverAccess.AdjustToUserSessionAsync(userSession, _countryService.Object, settings);

            driverAccess.DriverNameWriteEnabled(DateTime.UtcNow).Should().BeTrue();
            driverAccess.DriverNameWriteEnabled(DateTime.UtcNow.AddDays(-4)).Should().BeFalse();

            driverAccess.DriverLicenseWriteEnabled(DateTime.UtcNow).Should().BeTrue();
            driverAccess.DriverLicenseWriteEnabled(DateTime.UtcNow.AddDays(-4)).Should().BeFalse();
        }

        [Fact]
        public async Task EditNameLicenceForAllDriversEnabled()
        {
            var driverAccess = new DriverAccess();
            var userSession = new UserSession
            {
                db = _parkId1,
                db_city = _parkCity,
                IsDriverPartner = false
            };

            var settings = new FakeGlobalSettingsService
            {
                GlobalSettings = new GlobalSettings
                {
                    DenyEditDriverNameAndLicense = new DriverEditSettings
                    {
                        Enable = false,
                        GraceDays = 3
                    }
                }
            };

            await driverAccess.AdjustToUserSessionAsync(userSession, _countryService.Object, settings);

            driverAccess.DriverNameWriteEnabled(DateTime.UtcNow).Should().BeTrue();
            driverAccess.DriverNameWriteEnabled(DateTime.UtcNow.AddDays(-4)).Should().BeTrue();

            driverAccess.DriverLicenseWriteEnabled(DateTime.UtcNow).Should().BeTrue();
            driverAccess.DriverLicenseWriteEnabled(DateTime.UtcNow.AddDays(-4)).Should().BeTrue();
        }

        [Fact]
        public async Task EditNameLicenceForNewDriverEnabledAndForOldDriverDisabled1()
        {
            var driverAccess1 = new DriverAccess();
            var driverAccess2 = new DriverAccess();
            var driverAccess3 = new DriverAccess();

            var userSession1 = new UserSession
            {
                db = _parkId1,
                db_city = _parkCity,
                IsDriverPartner = false
            };

            var userSession2 = new UserSession
            {
                db = _parkId2,
                db_city = _parkCity,
                IsDriverPartner = false
            };

            var userSession3 = new UserSession
            {
                db = _parkId1,
                db_city = _parkCity,
                IsDriverPartner = true
            };

            var settings = new FakeGlobalSettingsService
            {
                GlobalSettings = new GlobalSettings
                {
                    DenyEditDriverNameAndLicense = new DriverEditSettings
                    {
                        Enable = true,
                        GraceDays = 3,
                        Dbs = { _parkId1 },
                        SelfEmployedPartnersIncluded = false
                    }
                }
            };

            await driverAccess1.AdjustToUserSessionAsync(userSession1, _countryService.Object, settings);
            await driverAccess2.AdjustToUserSessionAsync(userSession2, _countryService.Object, settings);
            await driverAccess3.AdjustToUserSessionAsync(userSession3, _countryService.Object, settings);

            driverAccess1.DriverNameWriteEnabled(DateTime.UtcNow).Should().BeTrue();
            driverAccess1.DriverNameWriteEnabled(DateTime.UtcNow.AddDays(-4)).Should().BeFalse();

            driverAccess2.DriverLicenseWriteEnabled(DateTime.UtcNow).Should().BeTrue();
            driverAccess2.DriverLicenseWriteEnabled(DateTime.UtcNow.AddDays(-4)).Should().BeTrue();

            driverAccess3.DriverLicenseWriteEnabled(DateTime.UtcNow).Should().BeTrue();
            driverAccess3.DriverLicenseWriteEnabled(DateTime.UtcNow.AddDays(-4)).Should().BeTrue();
        }
    }
}
