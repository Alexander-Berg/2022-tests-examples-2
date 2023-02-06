using System;
using System.Threading.Tasks;
using Moq;
using Xunit;
using Yandex.Taximeter.Core.Services.Order.Events;
using Yandex.Taximeter.Core.Services.Order.Events.Processors;
using Yandex.Taximeter.Core.Services.Push;
using Yandex.Taximeter.Core.Services.Settings;
using Yandex.Taximeter.Test.Utils.Fakes;
using Yandex.Taximeter.Test.Utils.Redis;

namespace Yandex.Taximeter.Common.Tests.Services.Order.Events
{
    public class OrderBusyServiceTest
    {
        private readonly Mock<IPushMessageService> _pushMessageService;
        private readonly OrderBusyService _service;


        public OrderBusyServiceTest()
        {
            var redisManager = new RedisManagerMock().RedisManager.Object;
            _pushMessageService = new Mock<IPushMessageService>();
            _pushMessageService.Setup(s =>
                    s.StatusChangeAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>(), true))
                .Returns(() => Task.CompletedTask).Verifiable();
            var globalSettingsServiceMock = new Mock<IGlobalSettingsService>();
            globalSettingsServiceMock
                .Setup(s => s.GetAsync())
                .Returns(new ValueTask<GlobalSettings>(new GlobalSettings
                {
                    BusySettings = new BusyCalculationSettings { Enable = true, Threshold = 5 }
                }));
            _service = new OrderBusyService(redisManager, globalSettingsServiceMock.Object, new FakeLoggerFactory());
            _service.PushMessageService = _pushMessageService.Object;
        }

        private async Task AddAsync(OrderBusyService processor, string orderId, OrderEventType eventType)
        {
            var @event = new OrderStatisticsEvent
            {
                Db = "test_db",
                Driver = "test_driver",
                Order = orderId,
                EventType = eventType,
                ServerTime = DateTimeOffset.UtcNow
            };
            await Task.Delay(TimeSpan.FromTicks(100));
            await processor.ProcessAsync(@event);
        }

        [Fact]
        public async Task BusyTest_Simple()
        {
            for (var i = 0; i <= 5; i++)
            {
                await AddAsync(_service, $"test_order_{i}", OrderEventType.OrderCancelledOfferTimeout);
                if (i < 5)
                {
                    _pushMessageService.Verify(
                        s => s.StatusChangeAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>(), true),
                        Times.Never);
                }
            }

            _pushMessageService.Verify(
                s => s.StatusChangeAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>(), true),
                Times.Once);
        }

        [Fact]
        public async Task BusyTest_ResetCounter()
        {
            for (var i = 0; i <= 4; i++)
            {
                await AddAsync(_service, $"test_order_{i}", OrderEventType.RejectSeenImpossible);
                _pushMessageService.Verify(
                    s => s.StatusChangeAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>(), true),
                    Times.Never);
            }

            await AddAsync(_service, "test_order_reject", OrderEventType.Rejected);
            _pushMessageService.Verify(
                s => s.StatusChangeAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>(), true),
                Times.Never);

            for (var i = 0; i <= 4; i++)
            {
                await AddAsync(_service, $"test_order_new_{i}", OrderEventType.RejectAutocancel);
                _pushMessageService.Verify(
                    s => s.StatusChangeAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>(), true),
                    Times.Never);
            }
        }

        [Fact]
        public async Task BusyTest_SameOrder()
        {
            for (var i = 0; i <= 20; i++)
            {
                await AddAsync(_service, "test_order", OrderEventType.RejectAutocancel);
                _pushMessageService.Verify(
                    s => s.StatusChangeAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>(), true),
                    Times.Never);
            }

            for (var i = 0; i <= 3; i++)
            {
                await AddAsync(_service, $"test_order_new_{i}", OrderEventType.RejectAutocancel);
                _pushMessageService.Verify(
                    s => s.StatusChangeAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>(), true),
                    Times.Never);
            }

            await AddAsync(_service, "test_order_new_4", OrderEventType.RejectAutocancel);
            _pushMessageService.Verify(
                s => s.StatusChangeAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>(), true),
                Times.Once);
        }
    }
}
