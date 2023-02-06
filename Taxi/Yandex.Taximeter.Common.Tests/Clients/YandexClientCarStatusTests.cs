using System.Linq;
using FluentAssertions;
using MongoDB.Driver;
using Moq;
using Xunit;
using Yandex.Taximeter.Core.Code;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Repositories;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Park;
using Yandex.Taximeter.Core.Repositories.MongoDB.Dtos.Park;
using Yandex.Taximeter.Core.Services.Driver;
using Yandex.Taximeter.Core.Services.Order;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Clients
{
    [Collection(nameof(YandexClientTestsBase))]
    public class YandexClientCarStatusTests : YandexClientTestsBase
    {
        public YandexClientCarStatusTests()
        {
            ParkRepository.Setup(x => x.GetDtoAsync<ParkCarStatusDto>(
                    It.IsAny<FilterDefinition<ParkDoc>>(), It.IsAny<QueryMode>()))
                .ReturnsAsync(new ParkCarStatusDto
                {
                    Id = Db,
                    ProviderConfig = new ParkProviderConfig
                    {
                        Yandex = YandexConfig
                    }
                });
        }

        [Theory]
        [InlineData(DriverServerStatus.Busy,
            YandexClient.eCarStatus.verybusy, true)]
        [InlineData(DriverServerStatus.Free,
            YandexClient.eCarStatus.free, false)]
        [InlineData(DriverServerStatus.InOrderBusy,
            YandexClient.eCarStatus.verybusy, true)]
        [InlineData(DriverServerStatus.InOrderFree,
            YandexClient.eCarStatus.verybusy, false)]
        public async void TaximeterToTrackerStatusConversionTests(
            DriverServerStatus serverStatus,
            YandexClient.eCarStatus expectedTrackerStatus, bool expectedDontChain)
        {
            await YandexClient.CarStatusTask(Driver, serverStatus);

            var uriParams = ParseLastRequestUri();
            AssertStatus(uriParams, expectedTrackerStatus);
            AssertDontChain(uriParams, isSet: expectedDontChain);
        }

        [Fact]
        public async void CarStatus_HasParkOrderInReserve_SendsVeryBusy()
        {
            OrderReserveService
                .Setup(x => x.CheckDriverReserveAsync(Db, Driver))
                .ReturnsAsync(new ReserveState(null, new SetCarItem(), false, null));

            await YandexClient.CarStatusTask(Driver, DriverServerStatus.Free);

            var uriParams = ParseLastRequestUri();
            AssertStatus(uriParams, YandexClient.eCarStatus.verybusy);
        }

        private void AssertStatus(ILookup<string, string> uriParams, YandexClient.eCarStatus status)
        {
            uriParams[YandexClient.STATUS_PARAM].Single().Should().Be(status.ToString());
        }

        private void AssertDontChain(ILookup<string, string> uriParams, bool isSet)
        {
            if (isSet)
                uriParams[YandexClient.DONT_CHAIN_PARAM].Single().Should().Be("1");
            else
                uriParams.Contains(YandexClient.DONT_CHAIN_PARAM).Should().BeFalse();
        }

        protected ILookup<string, string> ParseLastRequestUri()
            => FakeHttpMessageHandler.Requests.Single()
                .RequestUri.Query
                .Split('&')
                .Select(x => x.Split('='))
                .ToLookup(x => x[0], x => x[1]);
    }
}