using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using FluentAssertions;
using Moq;
using Newtonsoft.Json;
using Xunit;
using Yandex.Taximeter.Core.Services.Driver.StatusLog;
using System.Linq;
using Microsoft.Extensions.Logging;
using Yandex.Taximeter.Core.Services.Driver;
using Yandex.Taximeter.Test.Utils.Fakes;
using Yandex.Taximeter.Test.Utils.Redis;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Services.Driver.StatusLog
{
    public class DriverStatusLogServiceTests
    {
        private RedisManagerMock _redisManagerMock = new RedisManagerMock();
        private DriverStatusLogService _statusLogService;

        public DriverStatusLogServiceTests()
        {
            _statusLogService = new DriverStatusLogService(_redisManagerMock.RedisManager.Object, new FakeLoggerFactory().CreateLogger<DriverStatusLogService>());
        }

        [Fact]
        public async void AddAsync_RequiredArgumentsSet_SavesLog()
        {
            _redisManagerMock.LogCloudMaster.SetReturnsDefault(Task.FromResult(true));
            _redisManagerMock.LogCloudMaster.Setup(
                    x => x.EnqueueItemOnListAsync(It.IsAny<string>(),
                        It.IsAny<string>()))
                .Callback((string key, string value) =>
                {
                    JsonConvert.DeserializeObject<DriverStatusLog>(value).Should().NotBeNull();
                })
                .Returns(() => Task.CompletedTask);

            await _statusLogService.AddAsync(
                TestUtils.NewId(), TestUtils.NewId(), DateTime.Now, DriverServerStatus.Free,
                "imei val",
                new DriverStatusLogData(DriverStatusLogType.AutoClose));
        }

        [Fact]
        public async void ListAsync_RedisReturnsNull_ReturnsEmptyList()
        {
            _redisManagerMock.LogCloudSlave.Setup(x => x.GetAllItemsFromListAsync(It.IsAny<string>()))
                .Returns(() => Task.FromResult<List<string>>(null));

            var result = await _statusLogService.ListAsync(TestUtils.NewId(), TestUtils.NewId());
            result.Should().BeEmpty().And.NotBeNull();
        }

        [Fact]
        public async void ListAsync_RedisReturnsNotNull_ReturnsListOfDeserializedLogs()
        {
            var driverId = TestUtils.NewId();
            var dbId = TestUtils.NewId();
            var logs = new List<DriverStatusLog>
            {
                new DriverStatusLog(),
                new DriverStatusLog()
            };

            _redisManagerMock.LogCloudSlave.Setup(
                x => x.GetAllItemsFromListAsync(It.Is<string>(key => key.Contains(driverId) && key.Contains(dbId))))
                .Returns(() => Task.FromResult(logs.Select(JsonConvert.SerializeObject).ToList()));

            var result = await _statusLogService.ListAsync(dbId, driverId);
            result.Should().HaveCount(logs.Count);
        }
    }
}