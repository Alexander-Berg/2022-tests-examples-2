using System.Collections.Generic;
using System.Threading.Tasks;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Services.Geography;
using Yandex.Taximeter.Test.Utils.Redis;
using System;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Repositories.MongoDB.Dtos.DbTaxi;
using Yandex.Taximeter.Test.Utils.Fakes;

namespace Yandex.Taximeter.Common.Tests.Services.Geography
{
    public class TaxiGeoareaServiceTests
    {
        private readonly FakeCacheWithTimer<TaxiGeoareaService.GeoareasCache> _fakeCacheWithTimer;
        private readonly TestRepository _testRepository;
        private readonly TaxiGeoareaService _service;

        public TaxiGeoareaServiceTests()
        {
            (var cacheFactory,var cache) =
                FakeCacheWithTimer<TaxiGeoareaService.GeoareasCache>.BuildWithFactory();
            _fakeCacheWithTimer = cache;
            _testRepository = new TestRepository();
            _service = new TaxiGeoareaService(
                _testRepository,
                new RedisManagerMock().RedisManager.Object,
                new FakeLoggerFactory(),
                cacheFactory);
        }

        [Fact]
        public async void ListNamesAsync_CachesEmpty_LoadsFromMongoDb()
        {
            _testRepository.FakeResult = DefaultGeoareas;

            var result = await _service.ListNamesAsync();

            result.Should().BeEquivalentTo("moscow", "spb");
            _testRepository.QueryInvoked.Should().BeTrue();
        }

        [Fact]
        public async void ListNamesAsync_CachesEmpty_PopulatesRedisAndInMemoryCache()
        {
            _testRepository.FakeResult = DefaultGeoareas;

            await _service.ListNamesAsync();

            await AssertRedisCache(DefaultGeoareas);

            _fakeCacheWithTimer.FakeData.Geoareas.Values.Should().BeEquivalentTo(_testRepository.FakeResult);
        }

        [Fact]
        public async void ListNamesAsync_InMemoryCacheNotEmpty_GetsResultFromMemory()
        {
            _fakeCacheWithTimer.FakeData = new TaxiGeoareaService.GeoareasCache(DefaultGeoareas);

            var result = await _service.ListNamesAsync();

            result.Should().BeEquivalentTo("moscow", "spb");
        }

        [Fact]
        public async void ListNamesAsync_MemoryCacheNotEmpty_DoesNotQueryRedisAndMongoDb()
        {
            _fakeCacheWithTimer.FakeData = new TaxiGeoareaService.GeoareasCache(DefaultGeoareas);

            await _service.ListNamesAsync();

            _testRepository.QueryInvoked.Should().BeFalse();
            await AssertRedisCache(null);
        }

        [Fact]
        public async void ListNamesAsync_RedisCacheActual_LoadsFromRedis()
        {
            await _service.RedisGeoareas.SetAsync(new TaxiGeoareaService.GeoareasCache(DefaultGeoareas));

            var result = await _service.ListNamesAsync();

            result.Should().BeEquivalentTo("moscow", "spb");
        }

        [Fact]
        public async void ListNamesAsync_RedisCacheActual_UpdatesMemoryCache()
        {
            await _service.RedisGeoareas.SetAsync(new TaxiGeoareaService.GeoareasCache(DefaultGeoareas));

            await _service.ListNamesAsync();

            _fakeCacheWithTimer.FakeData.Geoareas.Values.Should().BeEquivalentTo(DefaultGeoareas);
            _testRepository.QueryInvoked.Should().BeFalse();
        }

        [Fact]
        public async void ListNamesAsync_RedisCacheNotActual_LoadsFromMongoDb()
        {
            await _service.RedisGeoareas.SetAsync(new TaxiGeoareaService.GeoareasCache
            {
                ReloadTime = DateTime.UtcNow.AddDays(-1),
                Geoareas = new Dictionary<string, GeoareaDto>()
            });
            _testRepository.FakeResult = DefaultGeoareas;

            var result = await _service.ListNamesAsync();

            result.Should().BeEquivalentTo("moscow", "spb");
        }

        [Fact]
        public async void ListNamesAsync_RedisCacheNotActual_UpdatesRedisAndInMemoryCache()
        {
            await _service.RedisGeoareas.SetAsync(new TaxiGeoareaService.GeoareasCache
            {
                ReloadTime = DateTime.UtcNow.AddDays(-1),
                Geoareas = new Dictionary<string, GeoareaDto>()
            });
            _testRepository.FakeResult = DefaultGeoareas;

            await _service.ListNamesAsync();

            _testRepository.QueryInvoked.Should().BeTrue();
            await AssertRedisCache(DefaultGeoareas);
            _fakeCacheWithTimer.FakeData.Geoareas.Values.Should().BeEquivalentTo(DefaultGeoareas);
        }

        private async Task AssertRedisCache(IReadOnlyList<GeoareaDto> expected)
        {
            var redisCache = await _service.RedisGeoareas.GetAsync();
            if (expected == null)
            {
                redisCache.Should().BeNull();
            }
            else
            {
                redisCache.Geoareas.Values.Should().BeEquivalentTo(expected);
            }
        }

        private static IReadOnlyList<GeoareaDto> DefaultGeoareas { get; } =
            new List<GeoareaDto>
            {
                new GeoareaDto {Name = "moscow"},
                new GeoareaDto {Name = "spb"}
            };

        private class TestRepository : ITaxiGeoareaRepository
        {
            public bool QueryInvoked { get; set; }

            public IReadOnlyList<GeoareaDto> FakeResult { get; set; }
            
            public Task<IReadOnlyList<GeoareaDto>> LoadWithoutActivailionZonesAsync()
            {
                QueryInvoked = true;
                return Task.FromResult(FakeResult);
            }
        }
    }
}
