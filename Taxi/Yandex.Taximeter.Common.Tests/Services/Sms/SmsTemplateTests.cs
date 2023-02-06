using System.Collections.Generic;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;
using Yandex.Taximeter.Core.Clients;
using Yandex.Taximeter.Core.Clients.Personal;
using Yandex.Taximeter.Core.Redis;
using Yandex.Taximeter.Core.Repositories;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Repositories.MongoDB.Dtos.Car;
using Yandex.Taximeter.Core.Repositories.MongoDB.Dtos.Driver;
using Yandex.Taximeter.Core.Repositories.Sql.Order;
using Yandex.Taximeter.Core.Services.Culture;
using Yandex.Taximeter.Core.Services.Order;
using Yandex.Taximeter.Core.Services.Settings;
using Yandex.Taximeter.Core.Services.Sms;

namespace Yandex.Taximeter.Common.Tests.Services.Sms
{
    public class SmsTemplateTests
    {
        private readonly SmsService _smsService;
        
        public SmsTemplateTests()
        {
            var driverRepository = new Mock<IDriverRepository>();
            driverRepository
                .Setup(x => x.GetAsync<DriverBalanceListDto>(It.IsAny<string>(), It.IsAny<string>(),
                    It.IsAny<QueryMode>(), It.IsAny<string>(), It.IsAny<string>(), It.IsAny<int>()))
                .ReturnsAsync(new DriverBalanceListDto
                {
                    FirstName = "Василий",
                    MiddleName = "Иванович",
                    LastName = "Чапаев",
                    Balance = 1234.56,
                    CarId = "test_car"
                });

            var carRepository = new Mock<ICarRepository>();
            carRepository
                .Setup(x => x.GetAsync<CarSimpleDto>(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<QueryMode>()))
                .ReturnsAsync(new CarSimpleDto
                {
                    Number = "TT00177",
                    Color = "Красный",
                    Brand = "BMW",
                    Model = "7er"
                });

            _smsService = new SmsService(
                Mock.Of<IParkRepository>(),
                Mock.Of<IRedisManagerAsync>(),
                Mock.Of<ISmsProviderFactory>(),
                Mock.Of<ISmsStatusCheckService>(),
                Mock.Of<ILogger<SmsService>>(),
                Mock.Of<ISmsTemplateService>(),
                Mock.Of<IMailClient>(),
                Mock.Of<IOrderRepository>(),
                driverRepository.Object,
                carRepository.Object,
                Mock.Of<ICustomizationService>(),
                Mock.Of<IBrandService>(),
                Mock.Of<ICultureService>(),
                Mock.Of<IOrderMessageService>(),
                Mock.Of<IPersonalDataPhonesGateway>()
            );
        }

        [Fact]
        private async void TestTemplate_Driver_AllParameters()
        {
            var template = "<ВОДИТЕЛЬ> <ТЕЛВОДИТЕЛЬ> <БАЛАНС> <ГОСНОМЕР> <ЦВЕТ> <TC>";
            var result = await _smsService.GenerateSms("test_db" , new TaximeterCultureInfo("ru-ru"), "test_driver", null, template, false);
            result.Should().BeEquivalentTo("Василий +8890001112233 1235 TT00177 Красный BMW 7er");
        }

        [Fact]
        private async void TestTemplate_Driver_SomeParameters()
        {
            var template = "<ВОДИТЕЛЬ> <ТЕЛВОДИТЕЛЬ>";
            var result = await _smsService.GenerateSms("test_db", null,"test_driver", null, template, false);
            result.Should().BeEquivalentTo("Василий +8890001112233");
        }
    }
}