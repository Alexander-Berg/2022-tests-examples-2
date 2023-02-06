using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Threading;
using FluentAssertions;
using Moq;
using Newtonsoft.Json;
using Xunit;
using Yandex.Taximeter.Core.Clients;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Services;
using Yandex.Taximeter.Core.Services.Driver;
using Yandex.Taximeter.Core.Services.Subventions;
using Yandex.Taximeter.Test.Utils.Fakes;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Services.Subventions
{
    public class TaxiSubventionRulesRepositoryTests
    {
        private readonly Mock<ITaxiClient> _taxiClient;
        private readonly TaxiSubventionRulesRepository _repository;

        private static readonly string Db = TestUtils.NewId();
        private static readonly string Driver = TestUtils.NewId();

        public TaxiSubventionRulesRepositoryTests()
        {
            _taxiClient = new Mock<ITaxiClient>();
            var driverPositionService = new Mock<IDriverPositionService>();
            driverPositionService
                .Setup(x => x.GetCurrentAsync(It.IsAny<string>(), It.IsAny<string>(), CancellationToken.None))
                .ReturnsAsync(new DriverPosition {Latitude = 51.5, Longitude = 15.5});

            _repository = new TaxiSubventionRulesRepository(driverPositionService.Object, _taxiClient.Object, new FakeLoggerFactory());
        }

        [Fact]
        public async void LoadAsync_DriverId_QueriesRulesForDriverGps()
        {
            //Arrange
            var expectedRule = new SubventionRuleDto
            {
                Kind = TaxiSubventionRulesRepository.ONCE_BONUS,
                Zone = "zone1",
                Tariff = "econom",
                Branding = Array.Empty<string>()
            };
            var requests = SetupHttp(expectedRule);

            //Act
            var rules = await _repository.LoadAsync(new DriverId(Db, Driver));

            //Assert
            rules.Single().Geoarea.Should().Be(expectedRule.Zone);
            requests.Single()
                .RequestUri.PathAndQuery
                .Should()
                .Be("/utils/1.0/subvention-rules?latitude=51.5&longitude=15.5&kind=once_bonus");
        }

        [Fact]
        public async void LoadAsync_Geozones_QueriesRulesForGeozones()
        {
            //Arrange
            const string zone1 = "zone1";
            const string zone2 = "zone2";
            var expectedRule1 = new SubventionRuleDto
            {
                Kind = TaxiSubventionRulesRepository.ONCE_BONUS,
                Zone = zone1,
                Tariff = "econom",
                Branding = Array.Empty<string>()
            };
            var expectedRule2 = new SubventionRuleDto
            {
                Kind = TaxiSubventionRulesRepository.ONCE_BONUS,
                Zone = zone2,
                Tariff = "econom",
                Branding = Array.Empty<string>()
            };
            var requests = SetupHttp(expectedRule1, expectedRule2);

            //Act
            var rules = await _repository.LoadAsync(new[] {zone1, zone2});

            //Assert
            rules[zone1].Select(x => x.Geoarea)
                .SequenceEqual(new[] {expectedRule1}.Select(x => x.Zone))
                .Should().BeTrue();
            rules[zone2].Select(x => x.Geoarea)
                .SequenceEqual(new[] {expectedRule2}.Select(x => x.Zone))
                .Should().BeTrue();
            requests.Single()
                .RequestUri.PathAndQuery
                .Should()
                .Be("/utils/1.0/subvention-rules?kind=once_bonus&zone=zone1&zone=zone2");
        }

        private List<HttpRequestMessage> SetupHttp(params SubventionRuleDto[] rules)
        {
            var rulesDto = new  {rules = rules.ToList()};
            var responseMessage = new HttpResponseMessage(HttpStatusCode.OK)
            {
                Content = new StringContent(JsonConvert.SerializeObject(rulesDto))
            };
            var handler = new FakeHttpMessageHandler(responseMessage);
            _taxiClient.Setup(x => x.TaxiUtils)
                .Returns(new HttpClient(handler)
                    { BaseAddress = new Uri("http://base.addr") });
            return handler.Requests;
        }
    }
}