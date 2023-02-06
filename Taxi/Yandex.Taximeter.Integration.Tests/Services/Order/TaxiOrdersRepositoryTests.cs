using System;
using FluentAssertions;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Options;
using Xunit;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Services;
using Yandex.Taximeter.Core.Services.Order;
using Yandex.Taximeter.Integration.Tests.Fixtures;

namespace Yandex.Taximeter.Integration.Tests.Services.Order
{
    public class TaxiOrdersRepositoryTests : IClassFixture<FatFixture>
    {
        private readonly TaxiOrdersRepository _repository;

        public TaxiOrdersRepositoryTests(FatFixture fixture)
        {
            var factory = fixture.ServiceProvider.GetService<IMongoClientFactory>();
            _repository = new TaxiOrdersRepository(factory);
        }

        [Fact]
        public async void GetActiveOrders_LoadsOrders()
        {
            var orders = await _repository.GetActiveOrders(TimeSpan.FromDays(1));
            orders.Should().NotBeNull();
        }

        [Fact]
        public async void GetClidByOrderAliasIdAsync_ReturnEmptyClie()
        {
            var clidDb = await _repository.GetClidAndDbByOrderAliasIdAsync("");
            clidDb.Should().BeNull();
        }
    }
}
