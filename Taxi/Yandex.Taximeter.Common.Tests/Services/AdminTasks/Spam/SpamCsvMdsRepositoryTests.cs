using System.IO;
using FluentAssertions;
using Microsoft.AspNetCore.Http;
using Xunit;
using Yandex.Taximeter.Core.Services.AdminTasks;
using Yandex.Taximeter.Test.Utils.Fakes;

namespace Yandex.Taximeter.Common.Tests.Services.AdminTasks.Spam
{
    public class SpamCsvMdsRepositoryTests
    {
        private readonly FakeMdsClient _mdsClient = new FakeMdsClient();
        private readonly DriverIdsCsvMdsRepository _repository;

        public SpamCsvMdsRepositoryTests()
        {
            _repository = new DriverIdsCsvMdsRepository(_mdsClient);
        }

        [Fact]
        public async void SaveAsync_FileNotSelected_ThrowsException()
            => await Assert.ThrowsAsync<DriverIdsCsvFileParsingException>(
                async () => await _repository.SaveAsync(default(IFormFile)));

        [Fact]
        public async void AddDriversCsvTaskAsync_EmptyCsv_ThrowsException()
            => await Assert.ThrowsAsync<DriverIdsCsvFileParsingException>(
                async () => await _repository.SaveAsync(new FakeFormFile()));

        [Fact]
        public async void AddDriversCsvTaskAsync_InvalidCsv_ThrowsException()
        {
            var file = InvalidDriverCsvTaskFile();

            await Assert.ThrowsAsync<DriverIdsCsvFileParsingException>(
                async () => await _repository.SaveAsync(file));
        }

        [Fact]
        public async void AddDriversCsvTaskAsync_ValidCsv_SavesTask()
        {
            var id = await _repository.SaveAsync(ValidDriverCsvTaskFile());

            id.Should().NotBeNullOrEmpty();
            _mdsClient.SavedFiles.Should().NotBeEmpty();
        }

        private FakeFormFile ValidDriverCsvTaskFile()
            => BuildFakeFormFile("Services/AdminTasks/Spam/TestFiles/ValidSpamCsv.csv");

        private FakeFormFile InvalidDriverCsvTaskFile()
            => BuildFakeFormFile("Services/AdminTasks/Spam/TestFiles/InvalidSpamCsv.csv");

        private FakeFormFile BuildFakeFormFile(string filePath)
        {
            var path = Path.Combine(Directory.GetCurrentDirectory(), filePath);
            using (var fileStream = File.OpenRead(path))
                return new FakeFormFile(fileStream);
        }
    }
}