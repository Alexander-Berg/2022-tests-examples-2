using FluentAssertions;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Options;
using Xunit;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Services;
using Yandex.Taximeter.Core.Services.Geography;
using Yandex.Taximeter.Core.Utils;
using Yandex.Taximeter.Integration.Tests.Fixtures;
using Yandex.Taximeter.Test.Utils;
using Yandex.Taximeter.Test.Utils.Fakes;
using Yandex.Taximeter.Test.Utils.Redis;

namespace Yandex.Taximeter.Integration.Tests.Services.Geography
{
    public class TaxiGeoareaRepositoryTests : IClassFixture<FatFixture>
    {
        private readonly TaxiGeoareaService _service;

        public TaxiGeoareaRepositoryTests(FatFixture fixture)
        {
            var repository = fixture.ServiceProvider.GetService<ITaxiGeoareaRepository>();
            var cacheFactory = fixture.ServiceProvider.GetService<ICacheFactory>();
            _service = new TaxiGeoareaService(repository,
                new RedisManagerMock().RedisManager.Object,
                new FakeLoggerFactory(),
                cacheFactory);
        }

        [Fact]
        public async void ListNamesAsync_SimpleTest()
        {
            var result = await _service.ListNamesAsync();
            result.Should().NotBeEmpty();
        }
    }
}