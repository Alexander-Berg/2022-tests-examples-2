using System.Linq;
using System.Net.Http;
using System.Threading.Tasks;
using FluentAssertions;
using GeoAPI.Geometries;
using Moq;
using Xunit;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Repositories;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Services.Driver.WorkShift.DataAccess;
using Yandex.Taximeter.Core.Services.Tvm;
using Yandex.Taximeter.Core.Services.Version;
using Yandex.Taximeter.Test.Utils.Fakes;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Services.Driver.WorkShift
{
    public class TaxiWorkShiftsGatewayTests
    {
        private readonly FakeTaxiClient _fakeTaxiClient;
        private readonly TaxiWorkShiftsGateway _taxiWorkShiftsGateway;

        public TaxiWorkShiftsGatewayTests()
        {
            _fakeTaxiClient = new FakeTaxiClient();

            var parkRepositoryMock = new Mock<IParkRepository>();
            var tvmServiceMock = new Mock<ITvmService>();
            tvmServiceMock
                .Setup(x => x.GetTicketAsync(It.IsAny<string>()))
                .ReturnsAsync("ticket");
            parkRepositoryMock
                .Setup(x => x.GetYandexConfigAsync(It.IsAny<string>(), It.IsAny<QueryMode>()))
                .ReturnsAsync(new ProviderHelper.Config.Яндекс.Item
                {
                    apikey = "supersecret",
                    clid = "100500"
                });
            
            _taxiWorkShiftsGateway = new TaxiWorkShiftsGateway(
                _fakeTaxiClient,
                parkRepositoryMock.Object,
                new FakeLogger<TaxiWorkShiftsGateway>(),
                tvmServiceMock.Object);
        }

        [Fact]
        public async void LoadAsync_DBConfigFound_BuildsCorrectRequestMsg()
        {
            _fakeTaxiClient.TaxiUtilsHandler.Response = new HttpResponseMessage
            {
                Content = new StringContent("{}")
            };

            var driverId = TestUtils.NewDriverId();
            await _taxiWorkShiftsGateway.LoadAsync(driverId, new Coordinate(12.5, 15.5), new TaximeterVersion(8,99, 999));

            var request = _fakeTaxiClient.TaxiUtilsHandler.Requests.Single();
            request.RequestUri.PathAndQuery.Should().Be(
                $"/utils/1.0/workshifts?clid=100500&db={driverId.Db}&uuid={driverId.Driver}&latitude=15.5&longitude=12.5&version=8.99%20(999)");
        }
    }
}
