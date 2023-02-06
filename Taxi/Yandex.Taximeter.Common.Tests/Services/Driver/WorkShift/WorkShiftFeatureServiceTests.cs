using System.Collections.Generic;
using System.Diagnostics.CodeAnalysis;
using MongoDB.Driver;
using Moq;
using Xunit;
using Yandex.Taximeter.Core.Clients;
using Yandex.Taximeter.Core.Repositories;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Park;
using Yandex.Taximeter.Core.Repositories.MongoDB.Dtos.Park;
using Yandex.Taximeter.Core.Repositories.Redis.Entities.Driver;
using Yandex.Taximeter.Core.Services.Driver;
using Yandex.Taximeter.Core.Services.Driver.WorkShift;
using Yandex.Taximeter.Test.Utils.Fakes;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Services.Driver.WorkShift
{
    [SuppressMessage("ReSharper", "ExplicitCallerInfoArgument")]
    public class WorkShiftFeatureServiceTests
    {
        private static readonly string TestDb = TestUtils.NewId();
        private static readonly DriverId DriverId = new DriverId(TestDb, TestUtils.NewId());
        private static readonly string WorkRuleId = TestUtils.NewId();

        private readonly WorkShiftFeatureService _featureService;
        private readonly FakeMemoryCache _memoryCache = new FakeMemoryCache();
        private readonly Mock<IDriverRepository> _driverRepository = new Mock<IDriverRepository>();
        private readonly Mock<IDriverWorkRuleService> _driverWorkRuleService =
            new Mock<IDriverWorkRuleService>();
        
        private readonly Mock<IParkRepository> _parkRepository =
            new Mock<IParkRepository>();

        public WorkShiftFeatureServiceTests()
        {
            _featureService = new WorkShiftFeatureService(
                _driverRepository.Object,
                new FakeLoggerFactory(),
                _driverWorkRuleService.Object,
                _parkRepository.Object,
                _memoryCache);
            _driverRepository.Setup(x => x.GetAsync(DriverId.Db, DriverId.Driver, y => y.RuleId, It.IsAny<QueryMode>(),
                    It.IsAny<string>(), It.IsAny<string>(), It.IsAny<int>()))
                .ReturnsAsync(WorkRuleId);
        }

        [Fact]
        public async void IsEnabledFastAsync_RuleWorkEnabled_ReturnsDbEnabled()
        {
            _parkRepository
                .Setup(x => x.FindAsync<ParkDtoBase>(It.IsAny<FilterDefinition<ParkDoc>>(), null, 0, It.IsAny<QueryMode>()))
                .ReturnsAsync(new List<ParkDtoBase> {new ParkDtoBase {Id = TestDb}});
            Assert.True(await _featureService.IsEnabledAsync(DriverId));

            _parkRepository
                .Setup(x => x.FindAsync<ParkDtoBase>(It.IsAny<FilterDefinition<ParkDoc>>(), null, 0,
                    It.IsAny<QueryMode>()))
                .ReturnsAsync(new List<ParkDtoBase>());
            Assert.False(await _featureService.IsEnabledAsync(DriverId));
        }

        [Fact]
        public async void IsEnabledFastAsync_RuleWorkDisabled_ReturnsFalse()
        {
            _driverWorkRuleService.Setup(x => x.GetAsync(DriverId.Db, WorkRuleId, false))
                .ReturnsAsync(new DriverWorkRule {WorkshiftsEnabled = false});
            _parkRepository
                .Setup(x => x.FindAsync<ParkDtoBase>(It.IsAny<FilterDefinition<ParkDoc>>(), null, 0,It.IsAny<QueryMode>()))
                .ReturnsAsync(new List<ParkDtoBase> {new ParkDtoBase {Id = TestDb}});
            
            Assert.False(await _featureService.IsEnabledAsync(DriverId), "Покупка запрещена в условии работы");
        }
    }
}
