using System;
using System.Collections.Generic;
using System.Linq;
using FluentAssertions;
using Microsoft.Extensions.Options;
using Moq;
using Xunit;
using Yandex.Taximeter.Core.Code;
using Yandex.Taximeter.Core.Configuration.Options;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Services.Driver;
using Yandex.Taximeter.Core.Services.Geography;
using Yandex.Taximeter.Core.Services.Integration;
using Yandex.Taximeter.Core.Services.Settings;
using Yandex.Taximeter.Core.Services.Tvm;
using Yandex.Taximeter.Test.Utils.Fakes;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Services.Integration
{
    public class IntegrationProviderFactoryTests
    {
        private readonly IntegrationProviderFactory _factory;

        public IntegrationProviderFactoryTests()
        {
         var yandexClientFactory = new YandexClientFactory((db) =>
                new YandexClient(db,
                    Mock.Of<IParkRepository>(),
                    new FakeLoggerFactory(),
                    Mock.Of<IDriverStatusService>(),
                    Mock.Of<ICountryService>(),
                    Mock.Of<ICarRepository>(),
                    Mock.Of<IDriverRepository>(),
                    new OptionsWrapper<TaxiBackendOptions>(new TaxiBackendOptions()),
                    null,
                    Mock.Of<IDriverCheckService>(),
                    Mock.Of<IGlobalSettingsService>(),
                    Mock.Of<ITvmService>())
            );

            _factory = new IntegrationProviderFactory(
                yandexClientFactory,
                new FormulaClientFactory(db => new FormulaClient(db, null, new FakeLoggerFactory())),
                new OfficialTaxiClientFactory(db => new OfficialTaxiClient(db, null, new FakeLoggerFactory())),
                new IntegrationClientFactory(db =>
                    new IntegrationClient(db, Mock.Of<IParkRepository>(), null, new FakeLoggerFactory())));
        }

        [Fact]
        public void GetSetGpsClient_ProviderTypeInSet_CreatesNewClient()
        {
            AssertCreatesClients(_factory.SetGpsClients,
                (f, type) => f.GetSetGpsClient(TestUtils.NewId(), type));
        }

        [Fact]
        public void GetSetGpsClient_ProviderTypeNotInSet_ThrowsException()
        {
            AssertThrowsForProvidersNotInSet(_factory.SetGpsClients,
                (f, type) => f.GetSetGpsClient(TestUtils.NewId(), type));
        }

        [Fact]
        public void GetCarStatusTaskClient_ProviderTypeInSet_CreatesNewClient()
        {
            AssertCreatesClients(_factory.CarStatusTaskClients,
                (f, type) => _factory.GetCarStatusTaskClient(TestUtils.NewId(), type));
        }

        [Fact]
        public void GetCarStatusTaskClient_ProviderTypeNotInSet_ThrowsException()
        {
            AssertThrowsForProvidersNotInSet(_factory.CarStatusTaskClients,
                (f, type) => f.GetCarStatusTaskClient(TestUtils.NewId(), type));
        }

        [Fact]
        public void GetRequestConfirmClient_ProviderTypeInSet_CreatesNewClient()
        {
            AssertCreatesClients(_factory.RequestConfirmClients,
                (f, type) => f.GetRequestConfirmClient(TestUtils.NewId(), type));
        }

        [Fact]
        public void GetRequestConfirm_ProviderTypeNotInSet_ThrowsException()
        {
            AssertThrowsForProvidersNotInSet(_factory.RequestConfirmClients,
                (f, type) => f.GetRequestConfirmClient(TestUtils.NewId(), type));
        }

        private void AssertCreatesClients<TClient>(HashSet<Provider> providerSet,
            Func<IIntegrationProviderFactory, Provider, TClient> factoryInvokation)
        {
            foreach (var providerType in providerSet)
            {
                var provider = factoryInvokation(_factory, providerType);
                provider.Should().NotBeNull();
            }
        }

        private void AssertThrowsForProvidersNotInSet<TClient>(HashSet<Provider> providersSet,
            Func<IIntegrationProviderFactory, Provider, TClient> factoryInvokation)
        {
            foreach (var providerType in ProvidersNotInSet(providersSet))
                Assert.Throws<InvalidOperationException>(
                    () => factoryInvokation(_factory, providerType));
        }

        private IEnumerable<Provider> ProvidersNotInSet(HashSet<Provider> set)
            => Enum.GetValues(typeof(Provider))
                .Cast<Provider>()
                .Where(x => !set.Contains(x));
    }
}
