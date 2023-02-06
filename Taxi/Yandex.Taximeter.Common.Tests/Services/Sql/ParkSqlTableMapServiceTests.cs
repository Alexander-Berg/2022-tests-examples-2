using System;
using FluentAssertions;
using Moq;
using Xunit;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Configs;
using Yandex.Taximeter.Core.Services.Sql;
using Yandex.Taximeter.Test.Utils.Fakes;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Services.Sql
{
    public class ParkSqlTableMapServiceTests
    {
        private static readonly string ParkId = TestUtils.NewId();

        private static readonly ParkTableMapDoc ParkMap = new ParkTableMapDoc
        {
            IsSeparateTable = true,
            ParkId = ParkId
        };


        private readonly FakeCacheWithTimer<IParkSqlTableMapping> _fakeCacheWithTimer;
        private readonly Mock<IParkSqlTableMapRepository> _repositoryMock;
        private readonly ParkSqlTableMapService _service;

        public ParkSqlTableMapServiceTests()
        {
            _repositoryMock = new Mock<IParkSqlTableMapRepository>();
            var (cacheFactory, cache) = FakeCacheWithTimer<IParkSqlTableMapping>.BuildWithFactory();
            _fakeCacheWithTimer = cache;
            _service = new ParkSqlTableMapService(new FakeLoggerFactory(), 
                _repositoryMock.Object,
                cacheFactory);
        }

        [Fact]
        public async void GetMappingAsync_RepositoryFails_NoDataInMemoryCache_ThrowsException()
        {
            _repositoryMock.Setup(x => x.LoadParkTableMapAsync()).ThrowsAsync(new Exception());
            await Assert.ThrowsAsync<Exception>(
                async () => await _service.GetMappingAsync());
        }
    }
}