using System;
using FluentAssertions;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Options;
using Xunit;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Services;
using Yandex.Taximeter.Core.Services.Driver;
using Yandex.Taximeter.Integration.Tests.Fixtures;

namespace Yandex.Taximeter.Integration.Tests.Services.Driver
{
    public class TaxiDriverInformedConsentRepositoryTests : IClassFixture<SimpleFixture>
    {
        private readonly TaxiDriverInformedConsentRepository _repository;

        public TaxiDriverInformedConsentRepositoryTests(SimpleFixture fixture)
        {
            var factory = fixture.ServiceProvider.GetService<IMongoClientFactory>();
            _repository = new TaxiDriverInformedConsentRepository(factory);
        }

        [Fact]
        public async void SetPersonalDataAgreementStatus_SavesConsent()
        {
            var phone = "123456789";
            await _repository.SetInformedConsentAsync(phone);
            var result = await _repository.IsConsentAcceptedAsync(phone);
            result.Should().Be(true);
        }

        [Fact]
        public async void IsConsentRespondedAsync_ConsentNotSaved_ReturnsFalse()
        {
            var result = await _repository.IsConsentAcceptedAsync(Guid.NewGuid().ToString());
            result.Should().BeFalse();
        }
    }
}