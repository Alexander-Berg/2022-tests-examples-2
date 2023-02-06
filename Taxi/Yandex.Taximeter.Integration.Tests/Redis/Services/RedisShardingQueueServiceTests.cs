using System.Linq;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.Extensions.DependencyInjection;
using Xunit;
using Yandex.Taximeter.Core.Redis;
using Yandex.Taximeter.Core.Redis.Services;
using Yandex.Taximeter.Integration.Tests.Fixtures;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Integration.Tests.Redis.Services
{
    public class RedisShardingQueueServiceTests : IClassFixture<FatFixture>
    {
        private const string TAG = nameof(RedisShardingQueueServiceTests);

        private readonly IRedisManagerAsync _redisManager;
        private readonly RedisShardingQueueService<string> _queueService;

        public RedisShardingQueueServiceTests(FatFixture fixture)
        {
            _redisManager = fixture.ServiceProvider.GetService<IRedisManagerAsync>();
            _queueService = new RedisShardingQueueService<string>(_redisManager.TempCloud, TAG);
        }

        [Fact]
        public async void AddAsync_CalledMultipleTimes_AddsToDifferentRedisShards()
        {
            const int testKeysQuantity = 20;
            await CleanupKeysAsync();

            for (var itemIdx = 0; itemIdx < testKeysQuantity; itemIdx++)
            {
                await _queueService.AddAsync(TestUtils.NewId());
            }

            var shardWithKeys = 0;
            for (var clientIdx = 0; clientIdx < _redisManager.TempCloud.Clients.Count; clientIdx++)
            {
                var keys = await _redisManager.TempCloud.Sharding.GetAllItemsFromListAsync(clientIdx, TAG);
                if (keys.Any())
                {
                    shardWithKeys++;
                }
            }

            /*
             * Can flap with probability of (1/_redisManager.TempCloud.Clients.Count ^ (testKeysQuantity - 1)),
             * which should mean VERY rarely
             */
            shardWithKeys.Should().BeGreaterThan(1);
        }

        private async Task CleanupKeysAsync()
        {
            await _redisManager.TempCloud.Master.RemoveAllAsync_Server(new[] {TAG});
        }
    }
}