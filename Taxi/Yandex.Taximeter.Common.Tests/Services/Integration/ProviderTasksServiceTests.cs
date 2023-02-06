using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using FluentAssertions;
using MongoDB.Driver;
using Moq;
using Xunit;
using Yandex.Taximeter.Core.Graphite;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Repositories;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Park;
using Yandex.Taximeter.Core.Repositories.MongoDB.Dtos.Park;
using Yandex.Taximeter.Core.Services.Driver;
using Yandex.Taximeter.Core.Services.Integration;
using Yandex.Taximeter.Test.Utils.Fakes;
using Yandex.Taximeter.Test.Utils.Redis;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Services.Integration
{
    public class ProviderTasksServiceTests
    {
        private const DriverServerStatus CHANGED_STATUS = DriverServerStatus.Free;

        private readonly string _driverId = TestUtils.NewId();

        private readonly ParkProviderIntegrationDto _park = new ParkProviderIntegrationDto
        {
            Id = TestUtils.NewId(),
            IntegrationEvents = new HashSet<ParkIntegrationEvent>(),
            Providers = new HashSet<ParkProvider>()
        };

        private readonly SortedSet<ParkProvider> _driverProviders = new SortedSet<ParkProvider>();

        private readonly Mock<IIntegrationProviderFactory> _providerFactory 
            = new Mock<IIntegrationProviderFactory>();
        private readonly RedisInsights<DriverStatusProviderTask> _insights;
        private readonly ProviderTasksService _service;

        private readonly Mock<IGraphiteService> _graphiteService = new Mock<IGraphiteService>();
        public ProviderTasksServiceTests()
        {
            var parkRepositoryMock = new Mock<IParkRepository>();
            parkRepositoryMock
                .Setup(x => x.FindAsync<ParkIntegrationDto>(It.IsAny<FilterDefinition<ParkDoc>>(), 
                    null, 0, It.IsAny<QueryMode>()))
                .ReturnsAsync(new List<ParkIntegrationDto>());
            parkRepositoryMock
                .Setup(x => x.GetDtoAsync<ParkProviderIntegrationDto>(It.IsAny<FilterDefinition<ParkDoc>>(),
                    It.IsAny<QueryMode>()))
                .ReturnsAsync(_park);

            var driverRepository = new Mock<IDriverRepository>();
            driverRepository
                // ReSharper disable ExplicitCallerInfoArgument
                .Setup(repo => repo.GetAsync(_park.Id, _driverId, x => x.Providers, It.IsAny<QueryMode>(),
                    It.IsAny<string>(), It.IsAny<string>(), It.IsAny<int>()))
                // ReSharper restore ExplicitCallerInfoArgument
                .ReturnsAsync(_driverProviders);

            var redisManagerMock = new RedisManagerMock();
            _insights = redisManagerMock.TempCloudSharding
                .Object.Insights<DriverStatusProviderTask>();
            _service = new ProviderTasksService(
                _providerFactory.Object,
                redisManagerMock.RedisManager.Object,
                parkRepositoryMock.Object,
                new FakeLoggerFactory(),
                _graphiteService.Object,
                driverRepository.Object);
        }
        
        private void AssertTask(DriverStatusProviderTask expected, DriverStatusProviderTask actual)
        {
            expected.Db.Should().Be(actual.Db);
            expected.Driver.Should().Be(actual.Driver);
            expected.IntegrationEvent.Should().Be(actual.IntegrationEvent);
            expected.Providers.Should().Be(actual.Providers);
        }

        #region DequeueTaskAsync

        [Fact]
        public async void DequeueTaskAsync_NoTasksInQueue_ReturnsNull()
        {
            var task = await _service.GetNextAsync();
            task.Should().BeNull();
        }

        [Fact]
        public async void DequeueTaskAsync_TasksAddedInQueue_DequeuesTasks()
        {
            var t1 = new DriverStatusProviderTask {Driver = TestUtils.NewId()};
            var t2 = new DriverStatusProviderTask {Driver = TestUtils.NewId()};
            await _service.AddAsync(t1);
            await _service.AddAsync(t2);

            var task1 = await _service.GetNextAsync();
            var task2 = await _service.GetNextAsync();
            var task3 = await _service.GetNextAsync();

            AssertTask(task1, t1);
            AssertTask(task2, t2);
            task3.Should().BeNull();
        }

        #endregion
        
        public class StartTaskTests : ProviderTasksServiceTests
        {
            private readonly HashSet<Provider> _carStatusTaskClients = new HashSet<Provider>();

            public StartTaskTests()
            {
                _providerFactory.SetupGet(x => x.CarStatusTaskClients)
                    .Returns(_carStatusTaskClients);
            }

            [Fact]
            public void StartTask_HasProviders_StartsTaskForEveryProvider()
            {
                var provider2 = Provider.Яндекс;
                
                var provider2Client = AddProviderClient(provider2);
                var extraProviderClient = AddProviderClient(Provider.Формула);

                var task = CreateTaskWithProvider(provider2);
                _service.StartTask(task, CHANGED_STATUS);

                VerifyCarStatusTaskStarted(provider2Client);
                VerifyCarStatusTaskNotStarted(extraProviderClient);
            }

            [Fact]
            public void StartTask_HasIntegrationEvent_StartsIntegrationClientTask()
            {
                var integrationClient = AddIntegratioinClient();

                var task = CreateTaskWithIntegrationClient();
                _service.StartTask(task, CHANGED_STATUS);

                VerifyCarStatusTaskStarted(integrationClient);
            }

            [Fact]
            public async void StartTask_ProviderClientSucceeded_WritesSuccessToGraphite()
            {
                var providerType = Provider.Яндекс;
                var providerClient = AddProviderClient(providerType);
                
                _graphiteService.Setup(x => x.Increment($"provider_clients.success.{providerType}", 1)).Returns(Task.CompletedTask);
                _graphiteService.Setup(x => x.Increment($"provider_clients.all.{providerType}", 1)).Returns(Task.CompletedTask);
                
                providerClient.Setup(x => x.CarStatusTask(_driverId, CHANGED_STATUS, null))
                    .Returns(Task.CompletedTask);

                var task = CreateTaskWithProvider(providerType);
                await _service.StartTask(task, CHANGED_STATUS);
                
                _graphiteService.VerifyAll();
            }

            [Fact]
            public async void StartTask_ProviderClientFailed_WritesFailireToGraphite()
            {
                var providerType = Provider.Яндекс;
                var providerClient = AddProviderClient(providerType);
                
                _graphiteService.Setup(x => x.Increment($"provider_clients.failure.{providerType}", 1)).Returns(Task.CompletedTask);
                _graphiteService.Setup(x => x.Increment($"provider_clients.all.{providerType}", 1)).Returns(Task.CompletedTask);
                
                providerClient.Setup(x => x.CarStatusTask(_driverId, CHANGED_STATUS, null))
                    .Returns(Task.FromException(new Exception()));

                var task = CreateTaskWithProvider(providerType);
                await _service.StartTask(task, CHANGED_STATUS);
                _graphiteService.VerifyAll();
            }

            [Fact]
            public async void StartTask_IntegrationClientSucceeded_WritesSuccessToGraphite()
            {
                var integrationClient = AddIntegratioinClient();
                
                _graphiteService.Setup(x => x.Increment($"provider_clients.success.{GraphiteConsts.INTEGRATION_CLIENT_KEY}", 1)).Returns(Task.CompletedTask);
                _graphiteService.Setup(x => x.Increment($"provider_clients.all.{GraphiteConsts.INTEGRATION_CLIENT_KEY}", 1)).Returns(Task.CompletedTask);
                
                integrationClient.Setup(x => x.CarStatusTask(_driverId, CHANGED_STATUS, null))
                    .Returns(Task.CompletedTask);

                var task = CreateTaskWithIntegrationClient();
                await _service.StartTask(task, CHANGED_STATUS);
                _graphiteService.VerifyAll();

            }

            [Fact]
            public async void StartTask_IntegrationClientFailed_WritesFailireToGraphite()
            {
                var integrationClient = AddIntegratioinClient();
                
                _graphiteService.Setup(x => x.Increment($"provider_clients.failure.{GraphiteConsts.INTEGRATION_CLIENT_KEY}", 1)).Returns(Task.CompletedTask);
                _graphiteService.Setup(x => x.Increment($"provider_clients.all.{GraphiteConsts.INTEGRATION_CLIENT_KEY}", 1)).Returns(Task.CompletedTask);
                
                integrationClient.Setup(x => x.CarStatusTask(_driverId, CHANGED_STATUS, null))
                    .Returns(Task.FromException(new Exception()));

                var task = CreateTaskWithIntegrationClient();
                await _service.StartTask(task, CHANGED_STATUS);
                _graphiteService.VerifyAll();
            }

            private void VerifyCarStatusTaskNotStarted(Mock<IProviderCarStatusTaskClient> notAddedProviderClient)
            {
                notAddedProviderClient.Verify(x => x.CarStatusTask(_driverId, CHANGED_STATUS, null), Times.Never);
            }

            private Mock<IProviderCarStatusTaskClient> AddIntegratioinClient()
            {
                var integrationClient = new Mock<IProviderCarStatusTaskClient>();
                _providerFactory.Setup(x => x.GetCarStatusIntegrationClient(_park.Id))
                    .Returns(() => integrationClient.Object);
                return integrationClient;
            }

            private void VerifyCarStatusTaskStarted(Mock<IProviderCarStatusTaskClient> provider1Client)
            {
                provider1Client.Verify(x => x.CarStatusTask(_driverId, CHANGED_STATUS, null), Times.Once);
            }

            private Mock<IProviderCarStatusTaskClient> AddProviderClient(Provider provider)
            {
                _carStatusTaskClients.Add(provider);
                var providerClient = new Mock<IProviderCarStatusTaskClient>();
                _providerFactory.Setup(x => x.GetCarStatusTaskClient(_park.Id, provider))
                   .Returns(() => providerClient.Object);
                return providerClient;
            }
        }

        private DriverStatusProviderTask CreateTaskWithIntegrationClient()
            => new DriverStatusProviderTask
            {
                Db = _park.Id,
                Driver = _driverId,
                IntegrationEvent = true,
                Providers = 0
            };

        private DriverStatusProviderTask CreateTaskWithProvider(Provider provider)
            => new DriverStatusProviderTask
            {
                Db = _park.Id,
                Driver = _driverId,
                IntegrationEvent = false,
                Providers = provider
            };
    }
}
