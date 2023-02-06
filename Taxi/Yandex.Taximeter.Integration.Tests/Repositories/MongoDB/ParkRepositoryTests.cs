using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Integration.Tests.Fixtures;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Options;
using Yandex.Taximeter.Core.Configuration.Options;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Park;

namespace Yandex.Taximeter.Integration.Tests.Repositories.MongoDB
{
    public class ParkRepositoryTests : IClassFixture<FatFixture>
    {
        private readonly IParkRepository _repository;

        public ParkRepositoryTests(FatFixture fixture)
        {
            var loggerFactory = fixture.ServiceProvider.GetService<ILoggerFactory>();
            var logger = loggerFactory.CreateLogger<MongoClientFactory>();
            var mongoOpts = fixture.ServiceProvider.GetService<IOptions<MongoDbOptions>>();
            var mongoClientFactory = new MongoClientFactory(logger, mongoOpts);

            _repository = new ParkRepository(mongoClientFactory, loggerFactory);
        }

        public ParkDoc CreatePark(string parkId)
        {
            var itemContact = new DomainHelper.Contacts.Item
            {
                Id = "85ab44af805641748b49142358a9de90",
                Group = "Директор",
                Name = "Тест Тестович",
                Phones = "1112233",
                Email = "test@test.ru",
                Owner = "integration test"
            };
            
            var parkDoc = new ParkDoc
            {
                Id = parkId,
                IsActive = true,
                Login = "test",
                Name = "Тест",
                OrgName = "Тест",
                City = "Москва",
                ParkSetCarAlgorithm = ParkSetCarAlgorithmHelper.FromOld(0),
                ParkSetCarTimeout = 30,
                ParkBlacklistNoReserve = false,
                Owner = "integration test",
                CreatedDate = DateTime.UtcNow,
                Status = ParkStatus.Demo,
                Locale = "ru",
                IsDkkEnabled = true,
                DkkPeriod = 3,
                DkbPeriod = 5,
                Providers = new HashSet<ParkProvider> { ParkProvider.Yandex },
                RobotTime = 60,
                RobotDistance = 10,
                RobotProviders = new HashSet<ParkProvider> { ParkProvider.Yandex },
                Contacts = new Dictionary<string, ParkContact>
                {
                    [itemContact.Id] = ParkContact.FromOld(itemContact)
                },
                TimeZone = 3
            };

            return parkDoc;
        }

        [Fact]
        public async Task BasicCrudTest()
        {
            var parkId = "85ab44af805641748b49142358a9de90";
            var parkDoc = CreatePark(parkId);

            await _repository.DeleteAsync(parkId);
            await _repository.InsertAsync(parkDoc);
            var fetchedDoc = await _repository.GetAsync(parkId);
            await _repository.DeleteAsync(parkId);

            fetchedDoc.Id.Should().Be(parkId);
            fetchedDoc.ParkSetCarAlgorithm.Should().Be(ParkSetCarAlgorithm.None);
            fetchedDoc.Providers.Count.Should().Be(1);
            fetchedDoc.Providers.Should().Contain(ParkProvider.Yandex);
            fetchedDoc.DkkPeriod.Should().Be(3);
            fetchedDoc.DkbPeriod.Should().Be(5);
        }
    }
}
