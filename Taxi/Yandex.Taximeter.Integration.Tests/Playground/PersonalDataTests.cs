using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.Extensions.DependencyInjection;
using Newtonsoft.Json.Linq;
using Xunit;
using Yandex.Taximeter.Core.Clients.Personal;
using Yandex.Taximeter.Integration.Tests.Fixtures;

namespace Yandex.Taximeter.Integration.Tests.Playground
{
    public class PersonalDataTests : IClassFixture<FatFixture>
    {
        private readonly IPersonalDataPhonesGateway _pdPhonesGateway;
        private readonly IPersonalDataEmailsGateway _pdEmailsGateway;
        private readonly IPersonalDataLicensesGateway _pdLicensesGateway;
        private readonly IPersonalDataIdentificationsGateway _pdIdentificationsGateway;

        public PersonalDataTests(FatFixture fixture)
        {
            _pdPhonesGateway = fixture.ServiceProvider.GetService<IPersonalDataPhonesGateway>();
            _pdEmailsGateway = fixture.ServiceProvider.GetService<IPersonalDataEmailsGateway>();
            _pdLicensesGateway = fixture.ServiceProvider.GetService<IPersonalDataLicensesGateway>();
            _pdIdentificationsGateway = fixture.ServiceProvider.GetService<IPersonalDataIdentificationsGateway>();
        }

        [Fact]
        public async Task TestIdentificationsStore()
        {
            var number = "123";
            var data = new PersonalIdentificationsData
            {
                Number = number,
                Data = new Dictionary<string, string>
                {
                    {"issue_date", DateTime.UtcNow.ToString("O")},
                    {"issuer_country", "rus"},
                    {"issuer_organization", "test"},
                    {"number", number},
                    {"type", "passport"}
                }
            };
            
            var res = await _pdIdentificationsGateway.StoreAsync(data);
            Assert.NotNull(res.DataId);
            Assert.NotNull(res.NumberId);
        }

        [Fact]
        public async Task TestIdentificationsRetrieve()
        {
            var res = await _pdIdentificationsGateway.RetrieveAsync(new PersonalIdentificationsId
            {
                DataId = "a14b3613e5334ed6b648c0b85a21d5fa",
                NumberId = "82dbd490cd4e43acb28167f2d052a849"
            });

            Assert.NotNull(res.Data);
            Assert.NotNull(res.Number);
        }
    }
}
