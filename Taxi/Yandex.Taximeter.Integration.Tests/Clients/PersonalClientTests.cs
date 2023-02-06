using System.Linq;
using FluentAssertions;
using Microsoft.Extensions.DependencyInjection;
using Xunit;
using Yandex.Taximeter.Core.Clients.Personal;
using Yandex.Taximeter.Integration.Tests.Fixtures;

namespace Yandex.Taximeter.Integration.Tests.Clients
{
    public class PersonalClientTests : IClassFixture<FullFixture>
    {
        private readonly FullFixture _fixture;

        public PersonalClientTests(FullFixture fixture)
        {
            _fixture = fixture;
        }

        [Fact]
        public async void TestDriverLicenses()
        {
            var client = _fixture.ServiceProvider.GetService<IPersonalDataLicensesGateway>();

            var storeResponse = await client.StoreAsync("УУ11");
            var findResponse = await client.FindAsync("УУ11");
            var retrieveResponse = await client.RetrieveAsync(storeResponse.Id);

            storeResponse.Id.Should().Be(findResponse.Id);
            retrieveResponse.License.Should().Be(storeResponse.License);

            var bulkStoreResponse = await client.BulkStoreAsync(new[] {"УУ22", "УУ33"});
            var bulkRetrieveAsync = await client.BulkRetrieveAsync(bulkStoreResponse.Items.Select(x => x.Id).ToList());

            bulkRetrieveAsync.Items.FirstOrDefault(x => x.License == "YY22").Should().NotBeNull();
            bulkRetrieveAsync.Items.FirstOrDefault(x => x.License == "YY33").Should().NotBeNull();
        }
    }
}
