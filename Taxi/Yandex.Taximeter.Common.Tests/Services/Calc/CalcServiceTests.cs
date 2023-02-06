using FluentAssertions;
using Moq;
using Xunit;
using Yandex.Taximeter.Core.Clients.BillingReports;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.City;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Country;
using Yandex.Taximeter.Core.Repositories.Redis.Entities.Driver;
using Yandex.Taximeter.Core.Repositories.Sql;
using Yandex.Taximeter.Core.Repositories.Sql.Order;
using Yandex.Taximeter.Core.Services.Calc;
using Yandex.Taximeter.Core.Services.Culture;
using Yandex.Taximeter.Core.Services.Driver;
using Yandex.Taximeter.Core.Services.Driver.Payments;
using Yandex.Taximeter.Core.Services.Geography;
using Yandex.Taximeter.Core.Services.Settings;
using Yandex.Taximeter.Core.Services.Sms;
using Yandex.Taximeter.Test.Utils.Fakes;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Services.Calc
{
    public class CalcServiceTests
    {
        private static readonly string DbId = TestUtils.NewId();
        private static readonly string WorkRuleId = TestUtils.NewId();
        private const string ORDER_TYPE = "yandex";

        private readonly Mock<IDriverWorkRuleService> _driverWorkRuleService =
            new Mock<IDriverWorkRuleService>();

        private readonly Mock<ICountryService> _countryService = new Mock<ICountryService>();

        private readonly CalcService _service;

        public CalcServiceTests()
        {
            _service = new CalcService(
                new FakeLoggerFactory(),
                Mock.Of<IOrderRepository>(),
                Mock.Of<ISmsService>(),
                Mock.Of<IParkRepository>(),
                Mock.Of<IDriverRepository>(),
                Mock.Of<IBillingReportsGateway>(),
                _driverWorkRuleService.Object,
                _countryService.Object,
                Mock.Of<IDriverPaymentService>(),
                Mock.Of<ICultureService>(),
                Mock.Of<IGlobalSettingsService>());
        }

        [Fact]
        public async void CalculateDbComissionAsync_CalcTableEntryNotFound_ReturnsNull()
        {
            var result = await _service.CalculateDbComissionAsync(DbId, WorkRuleId, ORDER_TYPE, 100);

            result.Should().BeNull();
        }

        [Fact]
        public async void CalculateDbCommissionAsync_CalcTableEntryFound_Disabled_ReturnsNull()
        {
            _driverWorkRuleService.Setup(x => x.CalcTableLookupAsync(DbId, WorkRuleId, ORDER_TYPE))
                .ReturnsAsync(new DriverWorkRule.CalcTableItem
                {
                    Fix = 50,
                    Percent = 10,
                    IsEnabled = false
                });

            var result = await _service.CalculateDbComissionAsync(DbId, WorkRuleId, ORDER_TYPE, 100);

            result.Should().BeNull();
        }
        [Fact]
        public async void CalculateDbCommissionAsync_CalcTableEntryFound_Enabled_CalculatesCommission()
        {
            _driverWorkRuleService.Setup(x => x.CalcTableLookupAsync(DbId, WorkRuleId, ORDER_TYPE))
                .ReturnsAsync(new DriverWorkRule.CalcTableItem
                {
                    Fix = 50,
                    Percent = 10,
                    IsEnabled = true
                });

            var result = await _service.CalculateDbComissionAsync(DbId, WorkRuleId, ORDER_TYPE, 100);

            result.Should().Be(60d);
        }

        [Fact]
        public async void CalculateDbCommissionForSubventionAsync_WorkRuleNotFound_ReturnsZero()
        {
            var result =
                await _service.CalculateDbCommissionForSubventionAsync(DbId, CityDoc.ID_MOSCOW, WorkRuleId, 100);

            result.Should().Be(0m);
        }

        [Fact]
        public async void CalculateDbCommissionForSubventionAsync_WorkRuleFound_CalculatesCommission()
        {
            SetupWorkRulePercent(10);
            SetupCountryPercent(15);

            var result =
                await _service.CalculateDbCommissionForSubventionAsync(DbId, CityDoc.ID_MOSCOW, WorkRuleId, 100);

            result.Should().Be(10m);
        }

        [Fact]
        public async void
            CalculateDbCommissionForSubventionAsync_CountryPercentLessThanRulePercent_CalculatesUsingCountryPercent()
        {
            SetupWorkRulePercent(10);
            SetupCountryPercent(5);

            var result =
                await _service.CalculateDbCommissionForSubventionAsync(DbId, CityDoc.ID_MOSCOW, WorkRuleId, 100);

            result.Should().Be(5m);
        }

        private void SetupWorkRulePercent(int percent)
        {
            _driverWorkRuleService.Setup(x => x.GetAsync(DbId, WorkRuleId, false))
                .ReturnsAsync(new DriverWorkRule
                {
                    CommisisonForSubventionPercent = percent
                });
        }

        private void SetupCountryPercent(int percent)
        {
            _countryService.Setup(x => x.GetCountryByCityAsync(CityDoc.ID_MOSCOW))
                .ReturnsAsync(new Country
                {
                    MaxParkCommissionForSubventionPercent = percent
                });
        }
    }
}
