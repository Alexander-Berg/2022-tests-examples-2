using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using FluentAssertions;
using MongoDB.Driver;
using Moq;
using Xunit;
using Yandex.Taximeter.Core.Models.Chat;
using Yandex.Taximeter.Core.Repositories;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Driver;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Park;
using Yandex.Taximeter.Core.Repositories.MongoDB.Dtos.Driver;
using Yandex.Taximeter.Core.Repositories.MongoDB.Dtos.Park;
using Yandex.Taximeter.Core.Services.AdminTasks;
using Yandex.Taximeter.Core.Services.AdminTasks.Spam;
using Yandex.Taximeter.Core.Services.AdminTasks.Spam.Model;
using Yandex.Taximeter.Core.Services.Culture;
using Yandex.Taximeter.Core.Services.Driver;
using Yandex.Taximeter.Core.Services.Push;
using Yandex.Taximeter.Core.Services.Push.Messages;
using Yandex.Taximeter.Test.Utils.Fakes;
using Yandex.Taximeter.Test.Utils.Redis;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Services.AdminTasks.Spam
{
    public class SpamTaskExecutionServiceTests : IClassFixture<CommonFixture>
    {
        private const string FAKE_VALID_CITY_ID = "FAKE CITY";

        private List<ParkDoc> _fakeDbs = new List<ParkDoc>();

        private readonly List<Tuple<string, string, ChatItem>> _sentChatMsgs =
            new List<Tuple<string, string, ChatItem>>();

        private readonly Mock<ISpamTaskRepository> _spamTaskRepository = new Mock<ISpamTaskRepository>();
        private readonly Mock<IDriverCarSearchService> _driverLoaderService = new Mock<IDriverCarSearchService>();
        private readonly Mock<IParkRepository> _parkRepository = new Mock<IParkRepository>();
        private readonly Mock<IPushMessageService> _pushMessageService = new Mock<IPushMessageService>();
        private readonly Mock<ITopicService> _topicService = new Mock<ITopicService>();
        private readonly FakeMailClient _mailClient = new FakeMailClient();
        private readonly FakeMdsClient _mdsClient = new FakeMdsClient();
        private readonly Mock<IDriverIdsCsvRepository> _spamCsvRepository = new Mock<IDriverIdsCsvRepository>();
        private readonly Mock<IDriverRepository> _driverRepository = new Mock<IDriverRepository>();
        private readonly SpamTaskExecutionService _service;
        private readonly Mock<IBrandService> _brandingService = new Mock<IBrandService>();
        private readonly Mock<ICultureService> _cultureService = new Mock<ICultureService>();

        public SpamTaskExecutionServiceTests()
        {
            _parkRepository
                .Setup(x => x.FindAsync<ParkSpamDto>(It.IsAny<FilterDefinition<ParkDoc>>(), null, 0,
                    It.IsAny<QueryMode>()))
                .ReturnsAsync(() => _fakeDbs.Select(doc => new ParkSpamDto
                {
                    Id = doc.Id,
                    City = doc.City,
                    Contacts = doc.Contacts
                }).ToList());
            _parkRepository
                .Setup(x => x.FindAsync<ParkLocaleDto>(It.IsAny<FilterDefinition<ParkDoc>>(), null, 0,
                    It.IsAny<QueryMode>()))
                .ReturnsAsync(() => _fakeDbs.Select(doc => new ParkLocaleDto
                {
                    Id = doc.Id,
                    City = doc.City
                }).ToList());

            var commonBrand = new Brand
            {
                GlobalBrandName = Brand.YANDEX,
                ParkSupportEmail = "support@taxi.yandex.com",
                NoReplyEmail = "no-reply@taxi.yandex.com",
                ControlEmail = "no-reply@taxi.yandex.com"
            };
            _brandingService
                .Setup(x => x.GetParkBrandAsync(It.IsAny<string>()))
                .ReturnsAsync(() => commonBrand);
            _brandingService
                .Setup(x => x.GetCityBrandAsync(It.IsAny<string>()))
                .ReturnsAsync(() => commonBrand);

            var redisManagerMock = new RedisManagerMock();
            _service = new SpamTaskExecutionService(
                _parkRepository.Object,
                _driverRepository.Object,
                redisManagerMock.RedisManager.Object,
                _mailClient,
                _driverLoaderService.Object,
                new FakeLoggerFactory(),
                _spamTaskRepository.Object,
                _mdsClient,
                _spamCsvRepository.Object,
                _pushMessageService.Object,
                _topicService.Object,
                _brandingService.Object,
                _cultureService.Object);
            FakeStaticDependencies();
        }

        private void FakeStaticDependencies()
        {
            _service.SendChatMessageAsync = FakeSendChatMsg;
        }

        [Fact]
        public async void ExecuteTaskAsync_Client_WorkingDomains_SendsMailToAllDomains()
        {
            //Arrange
            _fakeDbs = new List<ParkDoc>
            {
                new ParkDoc
                {
                    Id = TestUtils.NewId(),
                    Contacts = ContactsList(TestUtils.NewEmail())
                },
                new ParkDoc
                {
                    Id = TestUtils.NewId(),
                    Contacts = ContactsList(TestUtils.NewEmail(), TestUtils.NewEmail())
                },
                new ParkDoc
                {
                    Id = TestUtils.NewId(),
                    Contacts = ContactsList(TestUtils.NewEmail())
                }
            };
            var spamTask = ValidClientTask();
            _spamTaskRepository.Setup(x => x.GetAsync(It.IsAny<string>())).ReturnsAsync(spamTask);

            //Act
            await _service.ExecuteTaskAsync(spamTask.Id, CancellationToken.None);

            //Assert
            _mailClient.SentMails.Select(x => x.To)
                .Should().BeEquivalentTo(
                    _fakeDbs.SelectMany(x => x.Contacts.Select(y => y.Key).Where(y => y != null)));
        }

        [Fact]
        public async void ExecuteTaskAsync_Drivers_Online_SendesMessagesToTopics()
        {
            //Arrange
            var dbIds = new[] { TestUtils.NewId(), TestUtils.NewId() };
            _fakeDbs.Add(new ParkDoc { Id = dbIds[0], IsActive = true });
            _driverLoaderService
                .Setup(x => x.FindDriversAsync<DriverDtoBase>(dbIds[0], DriverFilter.Online, null, 0, null))
                .ReturnsAsync(new List<DriverDtoBase>());

            var topics = new[] { "topic1", "topic2" };
            _topicService.Setup(x => x.SelectGeoTopicsAsync(TopicGroup.Online, It.IsAny<ICollection<string>>()))
                .ReturnsAsync(topics);
            var spamTask = ValidDriverTask();
            _spamTaskRepository.Setup(x => x.GetAsync(It.IsAny<string>())).ReturnsAsync(spamTask);

            //Act
            await _service.ExecuteTaskAsync(spamTask.Id, CancellationToken.None);

            //Assert
            foreach (var topic in topics)
            {
                _pushMessageService.Verify(x => x.DriverSpamAsync(topic,
                    It.Is<string>(xx => xx == spamTask.Id), It.Is<PushDriverSpam>(
                        push => push.Message == spamTask.Message &&
                                push.SpamShowOnlineOffer == spamTask.ShowOnlineOffer &&
                                push.SpamFeature == spamTask.Feature &&
                                !string.IsNullOrEmpty(push.Id))));
            }
        }

        [Fact]
        public async void ExecuteTaskAsync_Drivers_Online_SendsMessagesToOnlineDriversWithoutTopicSupport()
        {
            //Arrange
            var dbIds = new[] { TestUtils.NewId(), TestUtils.NewId() };
            _fakeDbs = new List<ParkDoc>
            {
                new ParkDoc { Id = dbIds[0], IsActive = true, City = FAKE_VALID_CITY_ID },
            };
            var db0Drivers = new List<DriverPushDto>
            {
                new DriverPushDto
                {
                    ParkId = dbIds[0], DriverId = TestUtils.NewId(), TaximeterVersion = "8.41",
                    TaximeterVersionType = ""
                },
                new DriverPushDto
                {
                    ParkId = dbIds[0], DriverId = TestUtils.NewId(), TaximeterVersion = "8.41",
                    TaximeterVersionType = ""
                }
            };
            var db1Drivers = new List<DriverPushDto>
            {
                new DriverPushDto { ParkId = dbIds[1], DriverId = TestUtils.NewId() }
            };
            _driverLoaderService
                .Setup(x => x.FindDriversAsync<DriverPushDto>(dbIds[0], It.IsAny<DriverFilter>(), null,
                    BalanceFilter.All, null))
                .ReturnsAsync(db0Drivers);
            _driverLoaderService
                .Setup(x => x.FindDriversAsync<DriverPushDto>(dbIds[1], It.IsAny<DriverFilter>(), null,
                    BalanceFilter.All, null))
                .ReturnsAsync(db1Drivers);

            var spamTask = ValidDriverTask();
            _spamTaskRepository.Setup(x => x.GetAsync(It.IsAny<string>())).ReturnsAsync(spamTask);

            //Act
            await _service.ExecuteTaskAsync(spamTask.Id, CancellationToken.None);

            //Assert
            var actualReceivers = _sentChatMsgs.Select(x => x.Item2).ToList();
            actualReceivers.Should().BeEquivalentTo(db0Drivers.Select(x => x.DriverId));
            foreach (var receiver in db0Drivers)
            {
                var sentMsg = _sentChatMsgs.First(x => x.Item2 == receiver.DriverId);
                sentMsg.Item1.Should().Be(dbIds[0]);
                sentMsg.Item3.msg.Should().Be(spamTask.Message);
            }
        }

        [Fact]
        public async void ExecuteTaskAsync_DriversCsv_SendsAllMessagesFromCsv()
        {
            //Arrange
            var taskItems = new[,] { { "id1", "msg1" }, { "id2", "msg2" } };
            var task = ValidDriversCsvTask(taskItems);
            _spamTaskRepository.Setup(x => x.GetAsync(It.IsAny<string>())).ReturnsAsync(task);
            _driverRepository
                .Setup(x => x.FindAsync<DriverDtoBase>(It.IsAny<FilterDefinition<DriverDoc>>(), null, null, 0,
                    QueryMode.Slave))
                .ReturnsAsync(new List<DriverDtoBase>
                {
                    new DriverDtoBase { DriverId = "id1", ParkId = TestUtils.NewId() },
                    new DriverDtoBase { DriverId = "id1", ParkId = TestUtils.NewId() },
                    new DriverDtoBase { DriverId = "id2", ParkId = TestUtils.NewId() },
                });

            //Act
            await _service.ExecuteTaskAsync(task.Id, CancellationToken.None);

            //Assert
            _sentChatMsgs.Count.Should().Be(3);
            _sentChatMsgs[0].Item2.Should().Be("id1");
            _sentChatMsgs[0].Item3.msg.Should().Be("msg1");
            _sentChatMsgs[1].Item2.Should().Be("id1");
            _sentChatMsgs[1].Item3.msg.Should().Be("msg1");
            _sentChatMsgs[2].Item2.Should().Be("id2");
            _sentChatMsgs[2].Item3.msg.Should().Be("msg2");
        }

        [Fact]
        public async void ExecuteTaskAsync_DriversCsv_CancellationRequested_StopsTask()
        {
            //Arrange
            var taskItems = new[,] { { "id1", "msg1" }, { "id2", "msg2" } };
            var task = ValidDriversCsvTask(taskItems);
            _spamTaskRepository.Setup(x => x.GetAsync(It.IsAny<string>())).ReturnsAsync(task);
            _driverRepository
                .Setup(x => x.FindAsync<DriverDtoBase>(It.IsAny<FilterDefinition<DriverDoc>>(), null, null, 0,
                    QueryMode.Slave))
                .ReturnsAsync(new List<DriverDtoBase>
                {
                    new DriverDtoBase { DriverId = "id1", ParkId = TestUtils.NewId() },
                    new DriverDtoBase { DriverId = "id2", ParkId = TestUtils.NewId() },
                });
            using (var cts = new CancellationTokenSource())
            {
                _service.SendChatMessageAsync = async (db, driver, msg) =>
                {
                    await FakeSendChatMsg(db, driver, msg);
                    cts.Cancel(); //request cancellation after first message is sent
                };

                //Assert
                await Assert.ThrowsAsync<OperationCanceledException>(
                    () => _service.ExecuteTaskAsync(task.Id, cts.Token));
                (await _service.TaskStateSet.WithSuffix(task.Id).GetAllItemsAsync()).Should().NotBeNullOrEmpty();
            }
        }

        private Dictionary<string, ParkContact> ContactsList(params string[] emails)
            => emails.ToDictionary(x => x, x => new ParkContact { Email = x });

        private ClientSpamTask ValidClientTask() => new ClientSpamTask
        {
            Cities = new[] { FAKE_VALID_CITY_ID },
            Filter = ClientSpamTaskFilter.Working,
            Subject = "subj",
            Message = "msg",
            AuthorLogin = "login",
            CreationTime = DateTime.UtcNow
        };

        private DriversSpamTask ValidDriverTask() => new DriversSpamTask
        {
            Cities = new[] { FAKE_VALID_CITY_ID },
            Filter = DriversSpamTaskFilter.Online,
            Message = "msg",
            AuthorLogin = "login",
            CreationTime = DateTime.UtcNow,
            Format = ChatMessageFormat.Raw,
            Feature = SpamTaskFeature.Surge,
            ShowOnlineOffer = true
        };

        private DriversCsvSpamTask ValidDriversCsvTask(string[,] taskItems)
        {
            var fileId = TestUtils.NewId();
            var parsedTaskItems = new List<KeyValuePair<string, string>>();
            for (var i = 0; i < taskItems.GetLength(0); i++)
                parsedTaskItems.Add(new KeyValuePair<string, string>(taskItems[i, 0], taskItems[i, 1]));
            _spamCsvRepository.Setup(x => x.LoadAndParseAsync(fileId))
                .ReturnsAsync(parsedTaskItems);
            return new DriversCsvSpamTask
            {
                MdsTaskFileId = fileId,
                AuthorLogin = "login",
                CreationTime = DateTime.UtcNow,
                Format = ChatMessageFormat.Raw
            };
        }

        private Task FakeSendChatMsg(string db, string driver, ChatItem chatItem)
        {
            _sentChatMsgs.Add(Tuple.Create(db, driver, chatItem));
            return Task.CompletedTask;
        }
    }
}
