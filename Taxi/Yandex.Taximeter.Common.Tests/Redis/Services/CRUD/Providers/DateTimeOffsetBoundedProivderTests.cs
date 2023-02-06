using System;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Redis.Services.CRUD.Providers;
using Yandex.Taximeter.Test.Utils.Redis;

namespace Yandex.Taximeter.Common.Tests.Redis.Services.CRUD.Providers
{
    public class DateTimeOffsetBoundedProivderTests
    {
        private static readonly DateTime MinValue = new DateTime(2018, 01, 02);

        private readonly DateTimeOffsetBoundedProivder _provider;

        public DateTimeOffsetBoundedProivderTests()
        {
            _provider = new DateTimeOffsetBoundedProivder(
                new RedisManagerMock().DataCloud.Object, "test-key", MinValue);
        }

        [Fact]
        public async void LoadAsync_NothingSaved_ReturnsDefault()
        {
            var time = await _provider.LoadAsync();

            time.Should().Be(MinValue);
        }

        [Fact]
        public async void LoadAsync_HasSavedValInThePast_ReturnsSavedVal()
        {
            var date = DateTime.Today;
            await _provider.SaveAsync(date);

            var loadedDate = await _provider.LoadAsync();

            loadedDate.Should().Be(date);
        }

        [Fact]
        public async void LoadAsync_HasSavedValInFuture_ReturnsCurrentTime()
        {
            await _provider.SaveAsync(DateTime.UtcNow.AddDays(1));

            var loadedDate = await _provider.LoadAsync();

            loadedDate.Should().BeCloseTo(DateTimeOffset.UtcNow);
        }

        [Fact]
        public async void LoadAsync_HasSavedValLessThanDefault_ReturnsDefaultTime()
        {
            await _provider.SaveAsync(MinValue.AddDays(-10));

            var loadedDate = await _provider.LoadAsync();

            loadedDate.Should().Be(MinValue);
        }
    }
}