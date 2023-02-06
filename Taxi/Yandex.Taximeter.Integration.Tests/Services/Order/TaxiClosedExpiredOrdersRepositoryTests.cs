using System;
using FluentAssertions;
using Xunit;
using Microsoft.Extensions.DependencyInjection;
using Yandex.Taximeter.Core.Services.Order;
using Microsoft.Extensions.Options;
using Yandex.Taximeter.Integration.Tests.Fixtures;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Services;
using Yandex.Taximeter.Test.Utils.Fakes;

namespace Yandex.Taximeter.Integration.Tests.Services.Order
{
    public class TaxiClosedExpiredOrdersRepositoryTests : IClassFixture<FatFixture>
    {
        private readonly TaxiClosedExpiredOrdersRepository _repository;

        public TaxiClosedExpiredOrdersRepositoryTests(FatFixture fixture)
        {
            var factory = fixture.ServiceProvider.GetService<IMongoClientFactory>();
            _repository = new TaxiClosedExpiredOrdersRepository(factory, 
                new FakeLogger<TaxiClosedExpiredOrdersRepository>());
        }

        [Fact]
        public async void LoadUpdatesAsync_SimpleTest()
        {
            var result = await _repository.LoadUpdatesAsync();
            result.Should().NotBeNull();
        }

        [Fact]
        public async void LoadUpdatesAsync_DateArg_SimpleTest()
        {
            var result = await _repository.LoadUpdatesAsync(DateTime.UtcNow - TimeSpan.FromDays(7));
            result.Should().NotBeNull();
        }
    }
}