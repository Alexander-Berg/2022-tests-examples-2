using System;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.Extensions.DependencyInjection;
using Xunit;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Redis;
using Yandex.Taximeter.Integration.Tests.Fixtures;
using Yandex.Taximeter.Test.Utils.Fakes;
using Yandex.Taximeter.Test.Utils.Utils;
#pragma warning disable 4014

namespace Yandex.Taximeter.Integration.Tests.Extensions
{
    public class RedisLockFactoryTests : IClassFixture<FullFixture>
    {
        private readonly IRedisManagerAsync _redisManager;
        private readonly IRedisLockFactory _redisLockFactory;
        private static readonly TimeSpan LockTtl = TimeSpan.FromSeconds(3);

        public RedisLockFactoryTests(FullFixture fixture)
        {
            _redisManager = fixture.ServiceProvider.GetService<StackExchangeRedisManager>();
            _redisLockFactory = new RedisLockFactory(_redisManager.TempCloud, new FakeLoggerFactory());
        }

        [Fact]
        public async void ExecuteSynchronized_LockNotTaken_InvokesAction()
        {
            var executed = false;

            await _redisLockFactory.ExecuteSynchronized(
                AsAsync(() => {executed = true;}), 
                TestUtils.NewId(), LockTtl);

            executed.Should().BeTrue();
        }

        [Fact]
        public async void ExecuteSynchronized_LockNotTaken_TakesAndReleasesLock()
        {
            var lockKey = TestUtils.NewId();

            await _redisLockFactory.ExecuteSynchronized(async () =>
            {
                var lockKeyVal1 = await _redisManager.TempCloud.Master.GetAsync<string>(lockKey);
                lockKeyVal1.Should().NotBeNullOrEmpty("Во время выполнения кода внутри лока, ключ должен быть в редисе");
            }, lockKey, LockTtl);

            var lockKeyVal2 = await _redisManager.TempCloud.Master.GetAsync<string>(lockKey);
            lockKeyVal2.Should().BeNullOrEmpty("После выполнения кода внутри лока, ключ должен удалиться");
        }

        [Fact]
        public async void ExecuteSynchronized_DoubleLockInSameContext_TakesAndReleasesLock()
        {
            var lockKey = TestUtils.NewId();

            await _redisLockFactory.ExecuteSynchronized(async () =>
            {
                var lockKeyVal1 = await _redisManager.TempCloud.Master.GetAsync<string>(lockKey);
                lockKeyVal1.Should().NotBeNullOrEmpty("Во время выполнения кода внутри лока, ключ должен быть в редисе");
                await _redisLockFactory.ExecuteSynchronized(async () =>
                {
                    var lockKeyVal2 = await _redisManager.TempCloud.Master.GetAsync<string>(lockKey);
                    lockKeyVal2.Should().NotBeNullOrEmpty("Во время выполнения кода внутри лока, ключ должен быть в редисе");
                }, lockKey, LockTtl);
            }, lockKey, LockTtl);

            var lockKeyVal3 = await _redisManager.TempCloud.Master.GetAsync<string>(lockKey);
            lockKeyVal3.Should().BeNullOrEmpty("После выполнения кода внутри лока, ключ должен удалиться");
        }

        [Fact]
        public async void ExecuteSynchronized_LockAlreadyTaken_WaitsForLock()
        {
            var lockKey = TestUtils.NewId();

            Task task1 = null;

            _redisLockFactory.ExecuteSynchronized(async () =>
            {
                task1 = Task.Delay(700);
                await task1;
            }, lockKey, LockTtl);
            await _redisLockFactory.ExecuteSynchronized(AsAsync(() => { }), lockKey, LockTtl);

            task1.Status.Should().Be(TaskStatus.RanToCompletion, "Второй ExecuteSynchronized не должен запуститься, пока полностью не выполнится код в первом ExecuteSynchronized");
        }

        [Fact]
        public async void ExecuteSynchronized_WithTimeout_LockReleasedBeforeTimeout_ExecutesTask()
        {
            //Arrange
            var lockKey = TestUtils.NewId();
            var firstTaskTime = 2700;
            var secondTaskTimeout = 3000;
            _redisLockFactory.ExecuteSynchronized(() => Task.Delay(firstTaskTime), lockKey, LockTtl);

            //Act
            var isExecuted = false;
            await _redisLockFactory.ExecuteSynchronized(
                AsAsync(() => { isExecuted = true; }), lockKey, LockTtl,
                TimeSpan.FromMilliseconds(secondTaskTimeout));

            //Assert
            isExecuted.Should().BeTrue();
        }

        [Fact]
        public async void ExecuteSynchronized_WithTimeout_TimeoutOccurs_ThrowsException()
        {
            //Arrange
            var lockKey = TestUtils.NewId();
            var firstTaskTime = 800;
            var secondTaskTimeout = 400;
            ParallelHelper.RunInBackground(
               () => _redisLockFactory.ExecuteSynchronized(() => Task.Delay(firstTaskTime), lockKey, LockTtl),
               new FakeLogger());

            //Act
            await Assert.ThrowsAnyAsync<OperationCanceledException>(() =>
                _redisLockFactory.ExecuteSynchronized(
                    AsAsync(() => { }), lockKey, LockTtl,
                    TimeSpan.FromMilliseconds(secondTaskTimeout)));
        }

        private Func<Task> AsAsync(Action action)
            => () =>
            {
                action();
                return Task.CompletedTask;
            };
    }
}
