using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using FluentAssertions;
using Moq;
using Xunit;
using Yandex.Taximeter.Core.Services.Driver;
using Yandex.Taximeter.Core.Services.Integration;
using System.Linq;
using System.Xml.Linq;
using Microsoft.Extensions.Logging;
using MongoDB.Driver;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Repositories;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Park;
using Yandex.Taximeter.Core.Repositories.MongoDB.Dtos.Park;
using Yandex.Taximeter.Test.Utils.Fakes;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Services.Integration
{
    public class IntegratorServiceTests : IClassFixture<CommonFixture>
    {
        private readonly string _db1 = TestUtils.NewId();
        private readonly string _db2 = TestUtils.NewId();
        private readonly string _clid = TestUtils.NewId();
        private readonly string _apiKey = TestUtils.NewId();
        private readonly IDictionary<string, HashSet<string>> _dbsByClId = new Dictionary<string, HashSet<string>>();
        private readonly IDictionary<string, string> _dbByDriver = new Dictionary<string, string>();
        private readonly Mock<IDriverStatusService> _driverStatusService = new Mock<IDriverStatusService>();
        private readonly IntegratorService _service;
        
        private readonly List<ParkProviderDto> _clidParks = new List<ParkProviderDto>();

        public IntegratorServiceTests()
        {
            var parkRepository = new Mock<IParkRepository>();
//            parkRepository
//                .Setup(x => x.GetYandexConfigAsync(It.IsAny<string>(), It.IsAny<QueryMode>()))
//                .ReturnsAsync(new ProviderHelper.Config.Яндекс.Item
//                {
//                    clid = _clid,
//                    apikey = _apiKey
//                });
//            parkRepository
//                .Setup(x => x.GetParksIdsByClidAsync(It.IsAny<string>()))
//                .Returns((string x) => GetFakeDbsByClid(x));

            parkRepository
                .Setup(x => x.FindAsync<ParkProviderDto>(It.IsAny<FilterDefinition<ParkDoc>>(), null, 0, It.IsAny<QueryMode>()))
                .ReturnsAsync(_clidParks);
            
            _clidParks.Add(new ParkProviderDto {Id = _db1, ProviderConfig = Config(_clid, _apiKey)});
            _clidParks.Add(new ParkProviderDto {Id = _db2, ProviderConfig = Config(_clid, _apiKey)});

            var serviceMock = new Mock<IntegratorService>(parkRepository.Object, _driverStatusService.Object, new FakeLoggerFactory().CreateLogger<IntegratorService>(), Mock.Of<IDriverRepository>());
            serviceMock
                .Setup(x => x.GetDriverDbAsync(It.IsAny<string>()))
                .Returns<string>(GetFakeDbByDriver);
            
            serviceMock
                .Setup(x => x.GetDriverDbsAsync(It.IsAny<IEnumerable<string>>()))
                .Returns<IEnumerable<string>>(GetFakeDbsByDrivers);
            
            _service = serviceMock.Object;
        }

        [Fact]
        public async void AuthenticateAsync_UnknownClid_ThrowsAsync()
        {
            await Assert.ThrowsAsync<UnauthorizedAccessException>(
                () => _service.AuthenticateForIntegratorStatusesAsync(TestUtils.NewId(), TestUtils.NewId()));
        }

        [Fact]
        public async void AuthenticateAsync_KnownClidApiKeyDoesNotMatch_ThrowsException()
        {
            await Assert.ThrowsAsync<UnauthorizedAccessException>(
                () => _service.AuthenticateForIntegratorStatusesAsync(_clid, TestUtils.NewId()));
        }

        [Fact]
        public async void AuthenticateAsync_KnownClid_DbsAuthorized_ReturnsSetOfDbs()
        {
            var result = await _service.AuthenticateForIntegratorStatusesAsync(_clid, _apiKey);
            result.Should().BeEquivalentTo(_clidParks.Select(x => x.Id));
        }

        [Fact]
        public async void SetDriverStatusAsync_DbOfDriverNotAuthorized_ThrowsException()
        {
            _dbsByClId[_clid] = new HashSet<string> {_db1, _db2};
            var driver = TestUtils.NewId();
            _dbByDriver[driver] = TestUtils.NewId();

            await Assert.ThrowsAsync<UnauthorizedAccessException>(async () =>
                    await _service.SetDriverStatusAsync(_clid, TestUtils.NewId(), driver, IntegratorService.STATUS_FREE));
        }

        [Fact]
        public async void SetDriverStatusAsync_StatusFree_SetsStatus()
        {
            var dbs = new HashSet<string> {_db1, _db2};
            _dbsByClId[_clid] = dbs;
            var driver = TestUtils.NewId();
            _dbByDriver[driver] = dbs.First();

            await _service.SetDriverStatusAsync(_clid, _apiKey, driver, IntegratorService.STATUS_FREE);

            _driverStatusService.Verify(x => x.SetIntegratorFreeAsync(dbs.First(), driver), Times.Once);
        }

        [Fact]
        public async void SetDriverStatusAsync_StatusBusy_SetsStatus()
        {
            var dbs = new HashSet<string> {_db1, _db2};
            _dbsByClId[_clid] = dbs;
            var driver = TestUtils.NewId();
            _dbByDriver[driver] = dbs.First();

            await _service.SetDriverStatusAsync(_clid, _apiKey, driver, IntegratorService.STATUS_BUSY);

            _driverStatusService.Verify(x => x.SetIntegratorBusyAsync(dbs.First(), driver), Times.Once);
        }

        [Fact]
        public async void SetDriverStatusAsync_UnknownStatus_ThrowsException()
        {
            var dbs = new HashSet<string> {_db1, _db2};
            _dbsByClId[_clid] = dbs;
            var driver = TestUtils.NewId();
            _dbByDriver[driver] = dbs.First();

            await Assert.ThrowsAsync<UnauthorizedAccessException>(async () =>
                    await _service.SetDriverStatusAsync(_clid, TestUtils.NewId(), driver, "invalid status"));
        }

        [Fact]
        public async void SetDriverStatusesAsync_ValidXml_AllDriversFound_UpdatesStatuses()
        {
            _dbsByClId[_clid] = new HashSet<string> {_db1};
            //These are ids from test file
            var drivers = new[] {"7236482", "723643", "3582"};
            foreach (var driver in drivers)
                _dbByDriver[driver] = _db1;
            var document = XDocument.Load(Path.Combine("Services", "Integration", "TestFiles", "ValidCarStatusXml.xml"));
            List<string> setFree = null, setBusy = null;
            _driverStatusService.Setup(x => x.SetIntegratorBusyAsync(_db1, It.IsAny<List<string>>()))
                .Callback((string db, List<string> busy) => { setBusy = busy; })
                .Returns(Task.CompletedTask);
            _driverStatusService.Setup(x => x.SetIntegratorFreeAsync(_db1, It.IsAny<List<string>>()))
                .Callback((string db, List<string> free) => { setFree = free; })
                .Returns(Task.CompletedTask);

            await _service.SetDriverStatusesAsync(_clid, _apiKey, document);

            setBusy.Should().BeEquivalentTo(drivers[0], drivers[1]);
            setFree.Should().BeEquivalentTo(drivers[2]);
        }

        [Fact]
        public async void SetDriverStatusesAsync_InvalidXml_ThrownsInvalidOperationException()
        {
            _dbsByClId[_clid] = new HashSet<string> { _db1 };
            var document = XDocument.Load(Path.Combine("Services", "Integration", "TestFiles", "InvalidCarStatusXml.xml"));

            await Assert.ThrowsAsync<InvalidOperationException>(async () =>
                    await _service.SetDriverStatusesAsync(_clid, _apiKey, document));
        }

        /// <remarks>Delays logic is not currently implemented</remarks>
        [Fact]
        public async void SetDriverStatusesAsync_XmlWithDelays_IgnoresRecordsWithDelays()
        {
            //Driver id from test file
            var driver = "3582";
            _dbByDriver[driver] = _db1;
            _dbsByClId[_clid] = new HashSet<string> {_db1};
            var document = XDocument.Load(Path.Combine("Services", "Integration", "TestFiles", "CarStatusWithDelays.xml"));

            await _service.SetDriverStatusesAsync(_clid, _apiKey, document);

            _driverStatusService.Verify(x => x.SetIntegratorBusyAsync(_db1, It.IsAny<List<string>>()), Times.Exactly(1));
        }

        [Fact]
        public async void SetDriverStatusesAsync_SomeEntriesExecutedWithErrors_ThrowsIntegratorServiceException()
        {
            _dbsByClId[_clid] = new HashSet<string> { _db1 };
            var document = XDocument.Load(Path.Combine("Services", "Integration", "TestFiles", "ValidCarStatusXml.xml"));

            try
            {
                await _service.SetDriverStatusesAsync(_clid, _apiKey, document);
                throw new InvalidOperationException($"{nameof(IntegratorServiceException)} should have been thrown");
            }
            catch (IntegratorServiceException ex)
            {
                ex.Message.Split('\n').Should().HaveCount(4, "All 3 drivers from test file should be not found (1 extra line for a messae that no drivers were found)");
            }
        }

        private Task<IDictionary<string, string>> GetFakeDbsByDrivers(IEnumerable<string> drivers)
        {
            var result = drivers
                .Select(x => new KeyValuePair<string, string>(x, GetFakeDbByDriver(x).Result))
                .Where(x => !string.IsNullOrEmpty(x.Value))
                .ToDictionary(x => x.Key, x => x.Value);
            return Task.FromResult((IDictionary<string, string>)result);
        }

        private Task<string> GetFakeDbByDriver(string driver)
            => _dbByDriver.ContainsKey(driver)
                ? Task.FromResult(_dbByDriver[driver])
                : Task.FromResult<string>(null);

        private ParkProviderConfig Config(string clid, string apiKey)
            => new ParkProviderConfig
            {
                Yandex = new ProviderHelper.Config.Яндекс.Item
                {
                    clid = clid,
                    apikey = apiKey
                }
            };
    }
}
