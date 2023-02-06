using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using FluentAssertions;
using MongoDB.Driver;
using Moq;
using Xunit;
using Yandex.Taximeter.Core.Repositories;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Driver;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Park;
using Yandex.Taximeter.Core.Repositories.MongoDB.Dtos.Driver;
using Yandex.Taximeter.Core.Repositories.MongoDB.Dtos.Park;
using Yandex.Taximeter.Core.Services.Driver;
using Yandex.Taximeter.Core.Services.Driver.StatusLog;
using Yandex.Taximeter.Core.Services.Integration;
using Yandex.Taximeter.Core.Utils;
using Yandex.Taximeter.Test.Utils.Fakes;
using Yandex.Taximeter.Test.Utils.Redis;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Services.Driver
{
    public class DriverStatusServiceTests
    {
        private static readonly string Db = TestUtils.NewId();
        private static readonly string Driver = TestUtils.NewId();
        private readonly Mock<IDriverStatusLogService> _driverStatusLogService = new Mock<IDriverStatusLogService>();
        private readonly Mock<IDriverRepository> _driverRepository = new Mock<IDriverRepository>();
        private readonly Mock<IProviderTasksService> _providerTasksService = new Mock<IProviderTasksService>();
        private readonly Mock<IParkRepository> _parkRepository = new Mock<IParkRepository>();
        private readonly RedisManagerMock _redisManagerMock = new RedisManagerMock();
        private readonly RedisInsights<int> _statusInsights;
        private readonly FakeMessageDispatcher _messageDispatcher = new FakeMessageDispatcher();
        private readonly FakeDriverStatusChangeDateRepository _statusChangeDateRepository =
            new FakeDriverStatusChangeDateRepository();
        private readonly DriverStatusService _statusService;

        public DriverStatusServiceTests()
        {
           _driverRepository.Setup(x => x.FindAsync(
                   It.IsAny<FilterDefinition<DriverDoc>>(),
                   It.IsAny<ProjectionDefinition<DriverDoc, DriverDtoBase>>(),
                   null, 
                   0,
                   It.IsAny<QueryMode>()))
                .ReturnsAsync(new List<DriverDtoBase>());

            _statusService = new DriverStatusService(
                _driverStatusLogService.Object,
                _providerTasksService.Object,
                _redisManagerMock.RedisManager.Object,
                _statusChangeDateRepository,
                _parkRepository.Object,
                new FakeLoggerFactory(),
                _messageDispatcher,
                _driverRepository.Object);

            _statusInsights = _redisManagerMock.TempCloudMaster.Object.Insights<int>();
        }

        public class SetIntegratorStatusesTests : DriverStatusServiceTests
        {
            [Fact]
            public async void SetIntegratorFreeAsync_SetsIntegratorStatusInRedis()
            {
                await _statusService.SetIntegratorFreeAsync(Db, Driver);
                var savedStatus = await _statusService.GetIntegratorStatusAsync(Db, Driver);
                savedStatus.Should().Be(DriverServerStatus.Free);
            }

            [Fact]
            public async void SetIntegratorBusyAsync_SetsIntegratorStatusInRedis()
            {
                await _statusService.SetIntegratorBusyAsync(Db, Driver);
                var savedStatus = await _statusService.GetIntegratorStatusAsync(Db, Driver);
                savedStatus.Should().Be(DriverServerStatus.Busy);
            }

            [Fact]
            public async void SetIntegratorStatusAsync_SumStatusChanged_StartsProviderTask()
            {
                var oldStatuses = new DriverStatuses(DriverServerStatus.Free);
                await SetStatusesInRedis(oldStatuses);

                await _statusService.SetIntegratorBusyAsync(Db, Driver);

                VerifyProviderTasksStarted(Times.Once);
            }

            [Fact]
            public async void SetIntegratorStatusAsync_MultipleDrivers_SetsStatusesInRedis()
            {
                await _statusService.SetIntegratorBusyAsync(Db, new List<string> { Driver });
                var savedStatus = await _statusService.GetIntegratorStatusAsync(Db, Driver);
                savedStatus.Should().Be(DriverServerStatus.Busy);
            }

            [Fact]
            public async void SetIntegratorStatusAsync_MultipleDrivers_SumStatusChanged_StartsProviderTask()
            {
                var oldStatuses = new DriverStatuses(DriverServerStatus.Free);
                await SetStatusesInRedis(oldStatuses);

                await _statusService.SetIntegratorBusyAsync(Db, new List<string> { Driver });

                VerifyProviderTasksStarted(Times.Once);
            }
        }

        [Fact]
        public async void GetAsync_StatusPresentInDictionary_ReturnsLocalStatus()
        {
            var expected = new DriverStatuses(DriverServerStatus.Busy);
            await SetStatusesInRedis(expected);

            var actual = await _statusService.GetAsync(Db, Driver);

            actual.Should().Be(expected.TaximeterStatus);
        }

        [Fact]
        public async void GetAsync_StatusNotPresentInDictionary_ReturnsOffline()
        {
            var status = await _statusService.GetAsync(Db, Driver);

            status.Should().Be(DriverServerStatus.Offline);
        }

        [Theory]
        [InlineData(DriverServerStatus.Busy, DriverServerStatus.Busy)]
        [InlineData(DriverServerStatus.Busy, DriverServerStatus.Free)]
        public async void GetStatusesAsync_ReturnsValidStatuses(DriverServerStatus taximeterStatus, DriverServerStatus intStatus)
        {
            var savedStatuses = new DriverStatuses(taximeterStatus, intStatus);
            await SetStatusesInRedis(savedStatuses);

            var loadedStatuses = await _statusService.GetStatusesAsync(Db, Driver);

            loadedStatuses.Should().Be(savedStatuses);
        }

        public class ExpireIntegratorStatusesTests : DriverStatusServiceTests
        {
            private static readonly TimeSpan ExpireTime = TimeSpan.FromMinutes(10);
            private static readonly DateTime ExpiredDate = DateTime.UtcNow - ExpireTime - ExpireTime;
            private readonly HashSet<string> _dbsWithIntegration = new HashSet<string>();
            private readonly List<string> _drivers = new List<string> { Driver, TestUtils.NewId(), TestUtils.NewId() };

            public ExpireIntegratorStatusesTests()
            {
                _parkRepository
                    .Setup(x => x.FindAsync<ParkIntegrationDto>(
                        It.IsAny<FilterDefinition<ParkDoc>>(), 
                        It.IsAny<SortDefinition<ParkDoc>>(),
                        It.IsAny<int>(), 
                        It.IsAny<QueryMode>()))
                    .ReturnsAsync((FilterDefinition<ParkDoc> f, SortDefinition<ParkDoc> s, int l,  QueryMode q) =>
                        _dbsWithIntegration.Select(x => new ParkIntegrationDto {Id = x}).ToList());
                _driverRepository.Setup(x => x.FindAsync<DriverDtoBase>(Db,
                        It.IsAny<FilterDefinition<DriverDoc>>(),
                        It.IsAny<QueryMode>()))
                    .ReturnsAsync(
                        (string db, FilterDefinition<DriverDoc> f, QueryMode q)
                            => _drivers.Select(x => new DriverDtoBase {ParkId = Db, DriverId = x}).ToList());
            }

            [Fact]
            public async void ExpireIntegratorStatusesAsync_DbIntegrationDisabled_DoesNothing()
            {
                await _statusService.ExpireIntegratorStatusesAsync(TimeSpan.FromMinutes(10), new FakeLogger(), new Counters());

                _providerTasksService.Verify(x => x.AddAsync(It.IsAny<DriverStatusProviderTask>()), Times.Never);
            }

            [Fact]
            public async void ExpireIntegratorStatusesAsync_DbGlobalUpdateTimeExpired_SetsWholeParkToBusy()
            {
                _dbsWithIntegration.Add(Db);
                await _statusService.IntGlobalUpdateTimesHash.SetAsync(Db, ExpiredDate);

                await _statusService.ExpireIntegratorStatusesAsync(ExpireTime, new FakeLogger(), new Counters());

                var busyDrivers = await _statusService.IntegratorStatusesSet.WithPrefix(Db).GetAllItemsAsync();
                _drivers.Should().BeEquivalentTo(busyDrivers);
                var driverExpirationTimes = await _statusService.IntStatusesUpdateTimesHash.WithPrefix(Db).GetAllAsync();
                _drivers.Should().BeEquivalentTo(driverExpirationTimes.Keys);
                var dbIsExpired = await _statusService.ExpiredIntegrationsSet.ContainsAsync(Db);
                dbIsExpired.Should().BeTrue();
            }

            /// <summary>
            /// it is assumed that all drivers have already been set to busy, that's why no actions should be executed for db that is already expired
            /// </summary>
            [Fact]
            public async void ExpireIntegratorStatusesAsync_DbIsAlreadyExpired_DoesNothing()
            {
                _dbsWithIntegration.Add(Db);
                var alreadyBusyDrivers = new[] {Driver};
                await _statusService.IntGlobalUpdateTimesHash.SetAsync(Db, DateTime.UtcNow - ExpireTime - ExpireTime);
                await _statusService.SetIntegratorBusyAsync(Db, Driver);

                var busyDrivers = await _statusService.IntegratorStatusesSet.WithPrefix(Db).GetAllItemsAsync();
                busyDrivers.Should().BeEquivalentTo(alreadyBusyDrivers);
                var driverExpirationTimes = await _statusService.IntStatusesUpdateTimesHash.WithPrefix(Db).GetAllAsync();
                driverExpirationTimes.Keys.Should().BeEquivalentTo(alreadyBusyDrivers);
            }

            [Fact]
            public async void ExpireIntegratorStatusesAsync_DbGlobalTimeNotExpired_SetsDriversWithExpiredIntStatusesToBusy()
            {
                _dbsWithIntegration.Add(Db);
                await _statusService.IntGlobalUpdateTimesHash.SetAsync(Db, DateTime.UtcNow);
                await _statusService.IntStatusesUpdateTimesHash.WithPrefix(Db).SetAsync(Driver, ExpiredDate);
                var statusBefore = await _statusService.GetIntegratorStatusAsync(Db, Driver);

                await _statusService.ExpireIntegratorStatusesAsync(TimeSpan.FromMinutes(0), new FakeLogger(), new Counters());

                var statusAfter = await _statusService.GetIntegratorStatusAsync(Db, Driver);
                statusBefore.Should().Be(DriverServerStatus.Free);
                statusAfter.Should().Be(DriverServerStatus.Busy);
            }

            [Fact]
            public async void ExpireIntegratorStatusesAsync_DbGlobalTimeNotExpired_SetsDriversWithoutIntStatusesToBusy()
            {
                _dbsWithIntegration.Add(Db);
                await _statusService.IntGlobalUpdateTimesHash.SetAsync(Db, DateTime.UtcNow);
                var statusBefore = await _statusService.GetIntegratorStatusAsync(Db, Driver);

                await _statusService.ExpireIntegratorStatusesAsync(TimeSpan.FromMinutes(0), new FakeLogger(), new Counters());

                var statusAfter = await _statusService.GetIntegratorStatusAsync(Db, Driver);
                statusBefore.Should().Be(DriverServerStatus.Free);
                statusAfter.Should().Be(DriverServerStatus.Busy);
            }

            [Fact]
            public async void ExpireIntegratorStatusesAsync_DbGlobalTimeNotExpired_BusyDriversRemainBusy()
            {
                _dbsWithIntegration.Add(Db);
                await _statusService.IntGlobalUpdateTimesHash.SetAsync(Db, DateTime.UtcNow);
                await _statusService.IntStatusesUpdateTimesHash.WithPrefix(Db).SetAsync(Driver, ExpiredDate);
                await _statusService.IntegratorStatusesSet.WithPrefix(Db).AddAsync(Driver);
                var statusBefore = await _statusService.GetIntegratorStatusAsync(Db, Driver);

                await _statusService.ExpireIntegratorStatusesAsync(TimeSpan.FromMinutes(0), new FakeLogger(), new Counters());

                var statusAfter = await _statusService.GetIntegratorStatusAsync(Db, Driver);
                statusBefore.Should().Be(DriverServerStatus.Busy);
                statusAfter.Should().Be(DriverServerStatus.Busy);
            }
        }

        private void VerifyProviderTasksStarted(Func<Times> times)
        {
            _providerTasksService.Verify(x => x.AddAsync(It.IsAny<DriverStatusProviderTask>()), times);
        }

        private void AssertSavedStatus(DriverServerStatus expectecStatus)
        {
            var actualStatus = (DriverServerStatus)
                _statusInsights.Hashes().First().Value[Driver];
            actualStatus.Should().Be(expectecStatus);
        }

        private async Task SetStatusesInRedis(DriverStatuses statuses)
        {
            await SetStatusInRedis(statuses.TaximeterStatus);
            await SetIntegratorStatusInRedis(statuses.IntegratorStatus);
        }

        private async Task SetIntegratorStatusInRedis(DriverServerStatus status)
        {
            if (status == DriverServerStatus.Free)
                await _statusService.IntegratorStatusesSet.WithPrefix(Db).RemoveAsync(Driver);
            else
                await _statusService.IntegratorStatusesSet.WithPrefix(Db).AddAsync(Driver);
        }

        private Task SetStatusInRedis(DriverServerStatus status)
            =>  _statusService.TaximeterStatusesHash.WithPrefix(Db).SetAsync(Driver, (int)status);

        private class FakeDriverStatusChangeDateRepository : IDriverStatusChangeDateRepository
        {
            private readonly Dictionary<string, DateTime> _statusDateChanges = new Dictionary<string, DateTime>();

            public Task SetAsync(string db, string driver, DateTime value)
            {
                _statusDateChanges[driver] = value;
                return Task.CompletedTask;
            }

            public Task RemoveAsync(string db, string driver)
            {
                _statusDateChanges.Remove(driver);
                return Task.CompletedTask;
            }

            public Task<Dictionary<string, DateTime>> ListAsync(string db, string[] drivers = null)
            {
                if (drivers == null)
                    return Task.FromResult(_statusDateChanges);
                else
                    throw new NotImplementedException();
            }
        }
    }
}

