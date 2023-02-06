using System;
using System.Collections.Generic;
using FluentAssertions;
using MongoDB.Driver;
using Moq;
using Xunit;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Repositories;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Driver;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Park;
using Yandex.Taximeter.Core.Repositories.MongoDB.Dtos.Driver;
using Yandex.Taximeter.Core.Repositories.MongoDB.Dtos.Park;
using Yandex.Taximeter.Core.Services.Driver;
using Yandex.Taximeter.Core.Services.Driver.Payments;
using Yandex.Taximeter.Test.Utils.Fakes;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Services.Driver.Payments
{
    public class DriverPartnerDriverIdsCacheTests
    {
        private readonly Mock<IParkRepository> _parkRepo = new Mock<IParkRepository>();
        private readonly Mock<IDriverRepository> _driverRepo = new Mock<IDriverRepository>();
        private readonly DriverPartnerDriverIdsCache _cache;

        public DriverPartnerDriverIdsCacheTests()
        {
            _cache = new DriverPartnerDriverIdsCache(_parkRepo.Object, _driverRepo.Object, new FakeLoggerFactory());
        }

        [Fact]
        public void GetDriverByClid_ClidNotLoaded_ThrowsException()
        {
            Assert.ThrowsAny<Exception>(() => _cache.GetDriverByClid("clid1"));
        }

        [Fact]
        public async void GetDriverByClid_ClidLoaded_ReturnsId()
        {
            var clids = new[] {"clid1", "clid2"};
            var parks = new List<ParkMiscDto>
            {
                CreateParkProviderDto("parkId1", clids[0]),
                CreateParkProviderDto("parkId2", clids[1])
            };
            var drivers = new List<DriverDtoBase>
            {
                CreateDriverDtoBase(parks[0].Id, "driverId1"),
                CreateDriverDtoBase(parks[1].Id, "driverId2"),
            };

            SetupParks(parks);
            SetupDrivers(drivers);

            await _cache.LoadDriverIdsAsync(clids);

            CustomAssert.PropertiesEqual(
                new DriverPartnerCacheEntry(clids[0], true, new DriverId(parks[0].Id, drivers[0].DriverId)),
                _cache.GetDriverByClid(clids[0]));
            CustomAssert.PropertiesEqual(
                new DriverPartnerCacheEntry(clids[1], true, new DriverId(parks[1].Id, drivers[1].DriverId)),
                _cache.GetDriverByClid(clids[1]));
        }

        [Fact]
        public async void GetDriverByClid_ClidLoaded_ParkByClidNotFound_ReturnsResultWithNullId()
        {
            SetupParks(new List<ParkMiscDto>
            {
                CreateParkProviderDto("parkId1", "clid1")
            });
            SetupDrivers(new List<DriverDtoBase>
            {
                CreateDriverDtoBase("parkId1", "driverId1")
            });
            await _cache.LoadDriverIdsAsync(new[] {"clid1", "clid2"});

            var cacheEntry = _cache.GetDriverByClid("clid2");

            cacheEntry.DriverId.Should().BeNull();
            cacheEntry.DriverIdSearchError.Should().Be("parkId not found");
        }

        [Fact]
        public async void GetDriverByClid_ClidLoaded_DriverNotFound_ReturnsResultWithNullId()
        {
            const string clid = "clid1";
            SetupParks(new List<ParkMiscDto>
            {
                CreateParkProviderDto("parkId1", clid)
            });
            SetupDrivers(new List<DriverDtoBase>());
            await _cache.LoadDriverIdsAsync(new[] {clid});

            var cacheEntry = _cache.GetDriverByClid(clid);

            cacheEntry.DriverId.Should().BeNull();
            cacheEntry.DriverIdSearchError.Should().Be("driverId not found");
        }

        [Fact]
        public async void GetDriverByClid_ClidLoaded_MultipleDriversFound_ReturnsResultWithNullId()
        {
            const string clid = "clid1";
            const string parkId = "parkId1";
            SetupParks(new List<ParkMiscDto>
            {
                CreateParkProviderDto(parkId, clid)
            });
            SetupDrivers(new List<DriverDtoBase>
            {
                CreateDriverDtoBase(parkId, "driver1"),
                CreateDriverDtoBase(parkId, "driver2"),
            });
            await _cache.LoadDriverIdsAsync(new[] {clid});

            var cacheEntry = _cache.GetDriverByClid(clid);

            cacheEntry.DriverId.Should().BeNull();
            cacheEntry.DriverIdSearchError.Should().StartWith("multiplie driverIds");
        }

        private void SetupDrivers(List<DriverDtoBase> drivers)
        {
            _driverRepo
                .Setup(x => x.FindAsync<DriverDtoBase>(
                    It.IsAny<FilterDefinition<DriverDoc>>(), null, null, 0,It.IsAny<QueryMode>()))
                .ReturnsAsync(drivers);
        }

        private void SetupParks(List<ParkMiscDto> parks)
        {
            _parkRepo
                .Setup(x => x.FindAsync<ParkMiscDto>(It.IsAny<FilterDefinition<ParkDoc>>(), null, 0, It.IsAny<QueryMode>()))
                .ReturnsAsync(parks);
        }

        private static DriverDtoBase CreateDriverDtoBase(string parkId, string driverId)
            => new DriverDtoBase
            {
                DriverId = driverId,
                ParkId = parkId
            };

        private static ParkMiscDto CreateParkProviderDto(string parkId, string clid)
            => new ParkMiscDto
            {
                Id = parkId,
                ProviderConfig = new ParkProviderConfig
                {
                    Yandex = new ProviderHelper.Config.Яндекс.Item
                    {
                        clid = clid
                    }
                },
                DriverPartnerSource = DriverPartnerSource.Yandex
            };
    }
}