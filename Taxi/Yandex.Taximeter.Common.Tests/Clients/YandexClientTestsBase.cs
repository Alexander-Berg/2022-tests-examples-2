using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using Microsoft.Extensions.Options;
using MongoDB.Driver;
using Moq;
using Xunit;
using Yandex.Taximeter.Core.Clients;
using Yandex.Taximeter.Core.Code;
using Yandex.Taximeter.Core.Configuration.Options;
using Yandex.Taximeter.Core.Graphite;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Repositories;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Park;
using Yandex.Taximeter.Core.Repositories.MongoDB.Dtos.Car;
using Yandex.Taximeter.Core.Repositories.MongoDB.Dtos.Driver;
using Yandex.Taximeter.Core.Repositories.MongoDB.Dtos.Park;
using Yandex.Taximeter.Core.Services.Blacklist;
using Yandex.Taximeter.Core.Services.Culture;
using Yandex.Taximeter.Core.Services.Driver;
using Yandex.Taximeter.Core.Services.Driver.Payments;
using Yandex.Taximeter.Core.Services.Geography;
using Yandex.Taximeter.Core.Services.NewQualityControl;
using Yandex.Taximeter.Core.Services.Order;
using Yandex.Taximeter.Core.Services.Push;
using Yandex.Taximeter.Core.Services.Settings;
using Yandex.Taximeter.Core.Services.Tvm;
using Yandex.Taximeter.Test.Utils.Fakes;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Clients
{
    [Collection(nameof(YandexClientTestsBase))]
    public class YandexClientTestsBase : IClassFixture<CommonFixture>
    {
        protected Mock<IDriverStatusService> DriverStatusService = new Mock<IDriverStatusService>();

        protected FakeHttpMessageHandler FakeHttpMessageHandler = new FakeHttpMessageHandler(
            new HttpResponseMessage(HttpStatusCode.OK) { Content = new StringContent("") });

        protected Mock<IOrderReserveService> OrderReserveService = new Mock<IOrderReserveService>();
        protected Mock<IBlacklistService> BlacklistService = new Mock<IBlacklistService>();
        protected Mock<IParkRepository> ParkRepository = new Mock<IParkRepository>();
        protected Mock<IDriverRepository> DriverRepository = new Mock<IDriverRepository>();
        protected Mock<ICarRepository> CarRepository = new Mock<ICarRepository>();

        protected readonly YandexClient YandexClient;

        protected static readonly string Db = TestUtils.NewId();
        protected static readonly string Driver = TestUtils.NewId();
        protected static readonly string Car = TestUtils.NewId();

        protected static readonly ProviderHelper.Config.Яндекс.Item YandexConfig = new ProviderHelper.Config.Яндекс.Item
        {
            apikey = TestUtils.NewId(),
            clid = TestUtils.NewId(),
            version = "1"
        };

        public YandexClientTestsBase()
        {
            ParkRepository
                .Setup(
                    x => x.GetDtoAsync<ParkSettingsDto>(It.IsAny<FilterDefinition<ParkDoc>>(), It.IsAny<QueryMode>()))
                .ReturnsAsync(new ParkSettingsDto
                {
                    Id = Db,
                    RobotSettings = new HashSet<ParkRobotSettings>()
                    {
                        ParkRobotSettings.DisableBusiness,
                        ParkRobotSettings.DisableComfort,
                        ParkRobotSettings.DisableComfortPlus,
                        ParkRobotSettings.DisableEconom,
                        ParkRobotSettings.DisableExpress,
                        ParkRobotSettings.DisableMinivan,
                        ParkRobotSettings.DisableStandard,
                        ParkRobotSettings.DisableStart,
                        ParkRobotSettings.DisableWagon
                    }
                });
            ParkRepository
                .Setup(x => x.GetDtoAsync<ParkCarStatusDto>(It.IsAny<FilterDefinition<ParkDoc>>(),
                    It.IsAny<QueryMode>()))
                .ReturnsAsync(
                    new ParkCarStatusDto
                    {
                        Id = Db,
                        ProviderConfig = new ParkProviderConfig
                        {
                            Yandex = new ProviderHelper.Config.Яндекс.Item
                            {
                                apikey = TestUtils.NewId(),
                                clid = TestUtils.NewId(),
                                version = "1"
                            }
                        }
                    }
                );
            ParkRepository
                .Setup(x => x.GetYandexConfigAsync(It.IsAny<string>(), It.IsAny<QueryMode>()))
                .ReturnsAsync(
                    new ProviderHelper.Config.Яндекс.Item
                    {
                        apikey = TestUtils.NewId(),
                        clid = TestUtils.NewId(),
                        version = "1"
                    }
                );

            DriverRepository.Setup(
                    x => x.GetAsync<DriverStatusCheckDto>(Db, Driver, It.IsAny<QueryMode>(), It.IsAny<string>(),
                        It.IsAny<string>(), It.IsAny<int>()))
                .ReturnsAsync(new DriverStatusCheckDto
                {
                    ParkId = Db,
                    DriverId = Driver,
                    CarId = Car,
                });

            CarRepository.Setup(x => x.GetAsync<CarStatusCheckDto>(Db, Car, It.IsAny<QueryMode>()))
                .ReturnsAsync(new CarStatusCheckDto
                {
                    ParkId = Db,
                    CarId = Car
                });

            // TODO Сделать рефакторинг и переписать тест, чтобы не инжектит в статики.
            RobotHelper.Inject(
                ParkRepository.Object,
                null, Mock.Of<IDriverStatusService>(), null,
                null, null, Mock.Of<IGlobalSettingsService>(),
                CarRepository.Object, DriverRepository.Object, null,
                Mock.Of<ICultureService>(),
                null, Mock.Of<IDriverCategoriesGateway>(), Mock.Of<ICountryService>(), new FakeLoggerFactory());


            var driverCheckService = new DriverCheckService(
                new FakeLogger<DriverCheckService>(),
                Mock.Of<IDriverPaymentService>(),
                BlacklistService.Object,
                Mock.Of<IGlobalSettingsService>(),
                Mock.Of<ICountryService>(),
                Mock.Of<IQcService>(),
                Mock.Of<IGraphiteService>(),
                OrderReserveService.Object,
                Mock.Of<IPushMessageService>(),
                DriverRepository.Object,
                CarRepository.Object,
                Mock.Of<ICarLockGateway>()
            );

            YandexClient = new YandexClient(
                Db,
                ParkRepository.Object,
                new FakeLoggerFactory(),
                DriverStatusService.Object,
                Mock.Of<ICountryService>(),
                CarRepository.Object,
                DriverRepository.Object,
                Options.Create(new TaxiBackendOptions
                {
                    TaximeterApiHost = "http://127.0.0.1",
                    GeoRecieverHost = "http://127.0.0.1",
                    TrackerHost = "http://127.0.0.1"
                }),
                null,
                driverCheckService,
                Mock.Of<IGlobalSettingsService>(),
                Mock.Of<ITvmService>()
            );
            YandexClient.HttpMessageHandlerFactory = () => FakeHttpMessageHandler;
            OrderReserveService
                .Setup(x => x.CheckDriverReserveAsync(It.IsAny<string>(), It.IsAny<string>()))
                .ReturnsAsync(ReserveState.Empty);
            BlacklistService
                .Setup(x => x.GetCarAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<bool>(), null))
                .ReturnsAsync(null);
            BlacklistService
                .Setup(x => x.GetDriverAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<bool>(), null))
                .ReturnsAsync(null);
        }

        protected static HttpResponseMessage BuildContentMessage(string contentType, string data)
        {
            var content = new StringContent(data);
            content.Headers.ContentType = MediaTypeHeaderValue.Parse(contentType);
            return new HttpResponseMessage(HttpStatusCode.OK) { Content = content };
        }
    }
}
