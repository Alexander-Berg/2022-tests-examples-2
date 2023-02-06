using System;
using System.Globalization;
using System.Linq;
using FluentAssertions;
using Moq;
using Xunit;
using Yandex.Taximeter.Core.Models.Chat;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Services.Chat;
using Yandex.Taximeter.Test.Utils.Fakes;
using Yandex.Taximeter.Test.Utils.Redis;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Services.Chat
{
    public class ChatBanServiceTests
    {
        private readonly ChatBanService _service;

        public ChatBanServiceTests()
        {
            var redisMock = new RedisManagerMock();
            _service = new ChatBanService(
                new FakeLoggerFactory(),
                redisMock.RedisManager.Object,
                Mock.Of<IDriverRepository>());
        }

        [Fact]
        public async void BanAsync_ValidArgs_BansDriver()
        {
            var driverId = TestUtils.NewDriverId();

            await _service.BanAsync(new[]
            {
                new ChatBan(driverId, new ChatItem(), "test-login")
            });

            (await _service.IsBannedAsync(driverId)).Should().BeTrue();
            (await _service.IsBannedAsync(TestUtils.NewDriverId())).Should().BeFalse();
        }

        [Fact]
        public async void UnbanAsync_ValidArgs_UnbansDriver()
        {
            var driverId = TestUtils.NewDriverId();
            await _service.BanAsync(new[]
            {
                new ChatBan(driverId, new ChatItem(), "test-login")
            });

            await _service.UnbanAsync(driverId);

            (await _service.IsBannedAsync(driverId)).Should().BeFalse();
        }

        [Fact]
        public async void ListAsync_ValidArgs_NoQuery_ReturnsPage()
        {
            var bans = new[]
            {                      //хронологический порядок
                BuildBan("12:05"), //4
                BuildBan("12:10"), //5
                BuildBan("11:10"), //0
                BuildBan("11:15"), //1
                BuildBan("11:59"), //2
                BuildBan("12:01")  //3
            };
            await _service.BanAsync(bans);

            var listResult = await _service.ListAsync(3, 2, query: null);

            listResult.SequenceEqual(new[] {bans[4], bans[3]})
                .Should().BeTrue("ListAsync должен сортировать баны по дате от новых к старым");
        }

        [Fact]
        public async void ListAsync_ValidArgs_HasQuery_ReturnsPage()
        {
            var bans = new[]
            {                                       //хронологический порядок
                BuildBan("12:05", "fio", "msg"),    //4
                BuildBan("12:10", "fio", "msg"),    //5
                BuildBan("11:10", "fio 12:", "msg"), //0
                BuildBan("11:15", "fio", "msg 12:"), //1
                BuildBan("11:59", "fio", "msg"),    //2
                BuildBan("12:01", "fio", "msg")     //3
            };
            await _service.BanAsync(bans);

            var listResult = await _service.ListAsync(2, 3, query: "12:");

            listResult.Should().BeEquivalentTo(new[] {bans[5], bans[3], bans[2]});
        }

        private ChatBan BuildBan(string time) => BuildBan(time, "fio", TestUtils.NewId());

        private ChatBan BuildBan(string time, string driverFio, string message)
            => new ChatBan(TestUtils.NewDriverId(), new ChatItem
            {
                msg = message,
                guid = TestUtils.NewId(),
                date = DateTime.Today.AddDays(-1)
                       + TimeSpan.ParseExact(time, "hh\\:mm", CultureInfo.InvariantCulture)
            }, "test-login")
            {
                Channel = "test-channel",
                Reason = "test reason",
                DriverFio = driverFio,
                DriverLicense = "1A234"
            };
    }
}
