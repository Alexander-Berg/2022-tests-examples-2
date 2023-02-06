using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.AspNetCore.Http;
using Moq;
using Xunit;
using Yandex.Taximeter.Core.Dto;
using Yandex.Taximeter.Core.Models.Admin;
using Yandex.Taximeter.Core.Models.Chat;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Services.AdminTasks;
using Yandex.Taximeter.Core.Services.AdminTasks.Spam;
using Yandex.Taximeter.Core.Services.AdminTasks.Spam.Model;
using Yandex.Taximeter.Test.Utils.Fakes;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Services.AdminTasks.Spam
{
    public class SpamTaskServiceTests
    {
        private const string FAKE_VALID_CITY_ID = "FAKE CITY";
        private const string FAKE_INVALID_CITY_ID = "invalid city id";
        private const string USER_LOGIN = "user-login";
        private const string USER_DISPLAY_NAME = "Display Name";

        private readonly FakeSpamTaskRepository _spamTaskRepository = new FakeSpamTaskRepository();
        private readonly FakePassportClient _passportClient = new FakePassportClient();
        private readonly FakeMdsClient _mdsClient = new FakeMdsClient();
        private readonly FakeSpamQueueService _queueService = new FakeSpamQueueService();
        private readonly Mock<IDriverIdsCsvRepository> _spamCsvRepository = new Mock<IDriverIdsCsvRepository>();
        private readonly SpamTaskService _spamTaskService;

        public SpamTaskServiceTests()
        {
            var httpContextAccessor = new FakeHttpContextAccessor();
            httpContextAccessor.FakeHttpContext.SetUser(USER_LOGIN);
            var fakeCityRepository = new Mock<ICityRepository>();

            fakeCityRepository.Setup(x => x.ExistsAsync(It.IsAny<string>()))
                .ReturnsAsync((string key) => FakeCityExistsAsync(key));

            _spamTaskService = new SpamTaskService(
                httpContextAccessor, new FakePassportClientFactory(_passportClient), _mdsClient,
                fakeCityRepository.Object, _queueService, _spamTaskRepository, _spamCsvRepository.Object);
        }

        #region AddClientsTaskAsync

        [Fact]
        public async void AddClientsTaskAsync_FilterValueNotDefined_ThrowsArumentException()
        {
            var model = ValidClientTaskModel();
            model.Filter = (ClientSpamTaskFilter) 123456;
            await Assert.ThrowsAsync<ArgumentException>(() => _spamTaskService.AddClientsTaskAsync(model));
        }

        [Fact]
        public async void AddClientsTaskAsync_CityNotpecified_ThrowsArgumentException()
        {
            var model = ValidClientTaskModel();
            model.SelectedCities = Array.Empty<string>();
            await Assert.ThrowsAsync<ArgumentException>(() => _spamTaskService.AddClientsTaskAsync(model));
        }

        [Fact]
        public async void AddClientsTaskAsync_SpecifiedCityNotFound_ThrowsArgumentException()
        {
            var model = ValidClientTaskModel();
            model.SelectedCities = new[] { FAKE_INVALID_CITY_ID };
            await Assert.ThrowsAsync<ArgumentException>(() => _spamTaskService.AddClientsTaskAsync(model));
        }

        [Fact]
        public async void AddClientsTaskAsync_AllArgumentsValid_SavesTask()
        {
            var model = ValidClientTaskModel();

            await _spamTaskService.AddClientsTaskAsync(model);

            var task = (ClientSpamTask)_spamTaskRepository.Tasks.Single();
            task.Cities.Should().BeEquivalentTo(model.SelectedCities);
            task.Message.Should().Be(model.Message);
            task.Subject.Should().Be(model.Subject);
            task.Filter.Should().Be(model.Filter);
            SpamTaskBaseFieldsShouldBeDefault(task);
        }

        [Fact]
        public async void AddClientsTaskAsync_FileSpecified_UploadsFileToMds()
        {
            var fileName = "file.name";
            var model = ValidClientTaskModel();
            model.File = AspNetUtils.BuildFormFile(fileName, new byte[0]);

            await _spamTaskService.AddClientsTaskAsync(model);

            var savedTask = (ClientSpamTask)_spamTaskRepository.Tasks.Single();
            _mdsClient.SavedIds[0].Should().Be(savedTask.MdsFileId).And.NotBeNull();
            savedTask.FileName.Should().Be(fileName);
        }

        [Fact]
        public async void AddClientsTaskAsync_FileSpecified_UploadedFileShouldHaveValidContent()
        {
            string fileName = "file.name";
            var fileContent = Encoding.UTF8.GetBytes("file content");
            var model = ValidClientTaskModel();
            model.File = AspNetUtils.BuildFormFile(fileName, fileContent);

            await _spamTaskService.AddClientsTaskAsync(model);

            var mdsFileContent = _mdsClient.SavedFiles.First().Value;
            Assert.True(fileContent.SequenceEqual(mdsFileContent));
        }

        #endregion

        #region AddDriversTaskAsync

        [Fact]
        public async void AddDriversTaskAsync_FilterValueNotDefined_ThrowsArumentException()
        {
            var model = ValidDriverTaskModel();
            model.Filter = (DriversSpamTaskFilter)123456;
            await Assert.ThrowsAsync<ArgumentException>(
                () => _spamTaskService.AddDriversTaskAsync(model));
        }

        [Fact]
        public async void AddDriversTaskAsync_CityNotSpecified_ThrowsArgumentException()
        {
            var model = ValidDriverTaskModel();
            model.SelectedCities = null;
            await Assert.ThrowsAsync<ArgumentException>(
                () => _spamTaskService.AddDriversTaskAsync(model));
        }

        [Fact]
        public async void AddDriversTaskAsync_SpecifiedCityNotFound_ThrowsArgumentException()
        {
            var model = ValidDriverTaskModel();
            model.SelectedCities = new [] { FAKE_INVALID_CITY_ID };
            await Assert.ThrowsAsync<ArgumentException>(
                () => _spamTaskService.AddDriversTaskAsync(model));
        }

        [Fact]
        public async void AddDriversTaskAsync_AllArgumentsValid_SavesTask()
        {
            var model = ValidDriverTaskModel();

            await _spamTaskService.AddDriversTaskAsync(model);

            var task = (DriversSpamTask)_spamTaskRepository.Tasks.Single();
            task.Cities.Should().BeEquivalentTo(model.SelectedCities);
            task.Message.Should().Be(model.Message);
            task.Filter.Should().Be(model.Filter);
            task.Feature.Should().Be(model.Feature);
            task.ShowOnlineOffer.Should().Be(model.ShowOnlineOffer);
            SpamTaskBaseFieldsShouldBeDefault(task);
        }

        #endregion

        #region AddDriversCsvTaskAsync

        [Fact]
        public async void AddDriversCsvTaskAsync_InvalidCsv_ThrowsException()
        {
            _spamCsvRepository.Setup(x => x.SaveAsync(It.IsAny<IFormFile>()))
                .ThrowsAsync(new DriverIdsCsvFileParsingException("msg"));

            await Assert.ThrowsAsync<DriverIdsCsvFileParsingException>(
                async () => await _spamTaskService.AddDriversCsvTaskAsync(
                    new FakeFormFile(), ChatMessageFormat.Raw));
        }

        [Fact]
        public async void AddDriversCsvTaskAsync_ValidCsv_SavesTask()
        {
            var fileId = TestUtils.NewId();
            _spamCsvRepository.Setup(x => x.SaveAsync(It.IsAny<IFormFile>())).ReturnsAsync(fileId);

            await _spamTaskService.AddDriversCsvTaskAsync(new FakeFormFile(), ChatMessageFormat.Raw);

            var task = (DriversCsvSpamTask)_spamTaskRepository.Tasks.Single();
            task.MdsTaskFileId.Should().Be(fileId);
            SpamTaskBaseFieldsShouldBeDefault(task);
        }

        #endregion

        #region ListAsync

        [Fact]
        public async void ListAsync_NoTasksCreated_ReturnsEmptyList()
        {
            var tasks = await _spamTaskService.ListAsync(0, 10);
            tasks.Should().NotBeNull().And.BeEmpty();
        }

        [Fact]
        public async void ListAsync_ShouldReturnAllSavedTasks()
        {
            await _spamTaskRepository.CreateAsync(new ClientSpamTask());
            await _spamTaskRepository.CreateAsync(new DriversCsvSpamTask());
            await _spamTaskRepository.CreateAsync(new DriversSpamTask());

            var savedModels = await _spamTaskService.ListAsync(0, 10);

            savedModels.Count.Should().Be(3);
        }

        [Fact]
        public async void ListAsync_ValidArgs_ConvertsSavedTasksToModels()
        {
            var model = ValidClientTaskModel();
            _passportClient.AddPassportInfo(new PassportInfoDto
            {
                DisplayName = USER_DISPLAY_NAME,
                Login = USER_LOGIN
            });

            await _spamTaskService.AddClientsTaskAsync(model);
            var listItemModel = (await _spamTaskService.ListAsync(0, 10)).First();

            listItemModel.Author.Login.Should().Be(USER_LOGIN);
            listItemModel.Author.Name.Should().Be(USER_DISPLAY_NAME);
            listItemModel.CreationTime.Should().BeCloseTo(DateTime.UtcNow, 500);
            listItemModel.Status.Should().Be(SpamTaskStatus.New);
            listItemModel.Subject.Should().Be(model.Subject);
            listItemModel.Sender.Should().BeNull();
        }

        #endregion

        #region GetAsync

        [Fact]
        public async void GetAsync_TaskNotFound_ReturnsNull()
        {
            var task = await _spamTaskService.GetAsync(TestUtils.NewId());
            task.Should().BeNull();
        }

        [Fact]
        public async void GetAsync_ClientTask_ReturnsConvertedModel()
        {
            var creationModel = ValidClientTaskModel();
            var taskId = await _spamTaskService.AddClientsTaskAsync(creationModel);

            var readModel = (ClientSpamTaskInfoModel)await _spamTaskService.GetAsync(taskId);

            readModel.Cities.Should().BeEquivalentTo(creationModel.SelectedCities);
            readModel.Author.Login.Should().Be(USER_LOGIN);
            readModel.Filter.Should().Be(creationModel.Filter);
            readModel.Message.Should().Be(creationModel.Message);
            readModel.Subject.Should().Be(creationModel.Subject);
        }

        [Fact]
        public async void GetAsync_DriversTask_ReturnsConvertedModel()
        {
            var creationModel = ValidDriverTaskModel();
            var taskId = await _spamTaskService.AddDriversTaskAsync(creationModel);

            var readModel = (DriversSpamTaskInfoModel)await _spamTaskService.GetAsync(taskId);

            readModel.Cities.Should().BeEquivalentTo(creationModel.SelectedCities);
            readModel.Author.Login.Should().Be(USER_LOGIN);
            readModel.Filter.Should().Be(creationModel.Filter);
            readModel.Subject.Should().Be(creationModel.Message);
            readModel.Feature.Should().Be(creationModel.Feature);
            readModel.ShowOnlineOffer.Should().Be(creationModel.ShowOnlineOffer);
        }

        [Fact]
        public async void GetAsync_DriversCsvTask_ReturnsConvertedModel()
        {
            var task = new DriversCsvSpamTask
            {
                AuthorLogin = USER_LOGIN,
                Format = ChatMessageFormat.Markdown,
                CreationTime = DateTime.UtcNow,
            };
            await _spamTaskRepository.CreateAsync(task);

            var readModel = (DriversCsvSpamTaskInfoModel)await _spamTaskService.GetAsync(task.Id);

            readModel.Author.Login.Should().Be(task.AuthorLogin);
            readModel.Subject.Should().NotBeNullOrEmpty();
            readModel.Format.Should().Be(task.Format);
            readModel.CreationTime.Should().Be(task.CreationTime);
        }

        #endregion

        [Fact]
        public async void StartSpamTaskAsync_PutsTaskInQueue()
        {
            var taskId = await _spamTaskService.AddClientsTaskAsync(ValidClientTaskModel());

            await _spamTaskService.StartSpamTaskAsync(taskId);

            var task = await _spamTaskService.GetAsync(taskId);
            task.Sender.Should().NotBeNull();
            task.Status.Should().Be(SpamTaskStatus.InQueue);
            (await _queueService.CountAsync()).Should().Be(1);
            (await _queueService.GetNextAsync()).Should().Be(taskId);
        }

        [Fact]
        public async void DownloadDriversCsvTaskFile_TaskNotFound_ReturnsNull()
        {
            var file = await _spamTaskService.DownloadDriversCsvTaskFile(TestUtils.NewId());
            file.Should().BeNull();
        }

        [Fact]
        public async void DownloadDriversCsvTaskFile_TaskFound_DownloadsFileFromMds()
        {
            var task = new DriversCsvSpamTask { MdsTaskFileId = TestUtils.NewId() };
            await _spamTaskRepository.CreateAsync(task);
            var taskFile = new byte[24];
            _spamCsvRepository.Setup(x => x.LoadAsync(task.MdsTaskFileId)).ReturnsAsync(taskFile);

            var downloadedFile = await _spamTaskService.DownloadDriversCsvTaskFile(task.Id);

            downloadedFile.Length.Should().Be(taskFile.Length);
        }

        private CreateClientSpamTaskModel ValidClientTaskModel() => new CreateClientSpamTaskModel
        {
            SelectedCities = new[] { FAKE_VALID_CITY_ID },
            Filter = ClientSpamTaskFilter.All,
            Subject = "subj",
            Message = "msg"
        };

        private CreateDriversSpamTaskModel ValidDriverTaskModel() => new CreateDriversSpamTaskModel
        {
            SelectedCities= new[] { FAKE_VALID_CITY_ID },
            Filter = DriversSpamTaskFilter.Online,
            Message = "msg",
            Feature = SpamTaskFeature.GuaranteedMinimum,
            ShowOnlineOffer = true
        };

        private static void SpamTaskBaseFieldsShouldBeDefault(SpamTaskBase task)
        {
            task.AuthorLogin.Should().Be(USER_LOGIN);
            task.CreationTime.Should().BeCloseTo(DateTime.UtcNow, 500);
            task.Progress.Should().Be(0);
            task.Status.Should().Be(SpamTaskStatus.New);
        }

        private static bool FakeCityExistsAsync(string key) => key == FAKE_VALID_CITY_ID;

        private class FakeSpamQueueService : FakeQueueService<string>, ISpamTaskQueueService
        {}

        private class FakeSpamTaskRepository : ISpamTaskRepository
        {
            public List<SpamTaskBase> Tasks { get; } = new List<SpamTaskBase>();

            public Task CreateAsync(SpamTaskBase task)
            {
                Tasks.Add(task);
                return Task.CompletedTask;
            }

            public Task<SpamTaskBase> GetAsync(string id) => Task.FromResult(Tasks.FirstOrDefault(x => x.Id == id));

            public Task<Dictionary<string, SpamTaskBase>> GetOrderedRangeAsync(int skip, int take)
                => Task.FromResult(Tasks.Skip(skip).Take(take).ToDictionary(x => x.Id));

            public Task<Dictionary<string, SpamTaskBase>> GetRangeAsync(string[] ids)
                => Task.FromResult(Tasks.Where(x => ids.Contains(x.Id)).ToDictionary(x => x.Id));

            public Task UpdateAsync(SpamTaskBase task) => Task.CompletedTask;
        }
    }
}
