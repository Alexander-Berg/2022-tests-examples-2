using System;
using System.Threading;
using System.Threading.Tasks;
using FluentAssertions;
using Moq;
using Moq.Language.Flow;
using Xunit;
using Yandex.Taximeter.Core.Redis;
using Yandex.Taximeter.Test.Utils.Fakes;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Redis
{
    public class RedisLockTests : IDisposable
    {
        private readonly string _lockKey = TestUtils.NewId();
        private readonly string _lockId = TestUtils.NewId();

        private readonly Mock<IRedisMasterAsync> _redisMaster;
        private readonly RedisLock _lock;

        public RedisLockTests()
        {
            _redisMaster = new Mock<IRedisMasterAsync>();
            var redisCloud = new Mock<IRedisCloudAsync>();
            redisCloud.Setup(x => x.Master).Returns(_redisMaster.Object);
            _lock = new RedisLock(redisCloud.Object, new FakeLoggerFactory(), _lockKey, _lockId);
        }

        [Fact]
        public async void TakeAsync_NotTakenYet_TakesLock()
        {
            ConfigureLockTakeAsync(() => true);
            await _lock.TakeAsync(TimeSpan.MaxValue);
            _lock.IsTaken.Should().BeTrue();
        }

        [Fact]
        public async void TakeAsync_AlreadyTaken_WaitsUntilCancellation()
        {
            ConfigureLockTakeAsync(() => false);
            using (var cts = new CancellationTokenSource(TimeSpan.FromSeconds(1)))
            {
                await Assert.ThrowsAnyAsync<OperationCanceledException>(
                    () => _lock.TakeAsync(TimeSpan.FromSeconds(2), TimeSpan.MaxValue, cancellationToken:cts.Token));
                _lock.IsTaken.Should().BeFalse();
            }
        }

        [Fact]
        public async void TakeAsync_AlreadyTaken_WaitsUntilLockReleased()
        {
            var isLocked = false;
            ConfigureLockTakeAsync(() => isLocked)
                .Callback((string key, string id, TimeSpan t) => { isLocked = true; });

            using (var cts = new CancellationTokenSource(TimeSpan.FromSeconds(1)))
            {
                await _lock.TakeAsync(TimeSpan.FromSeconds(2), TimeSpan.MaxValue, cancellationToken:cts.Token);
                _lock.IsTaken.Should().BeTrue();
            }
        }

        [Fact]
        public async void TryTakeAsync_NotTakenYet_TakesLock()
        {
            ConfigureLockTakeAsync(() => true);

            await _lock.TryTakeAsync(TimeSpan.MaxValue);

            _lock.IsTaken.Should().BeTrue();
        }

        [Fact]
        public async void TryTakeAsync_AlreadyTaken_ReturnsFalse()
        {
            ConfigureLockTakeAsync(() => false);

            var isTaken = await _lock.TryTakeAsync(TimeSpan.MaxValue);
            isTaken.Should().BeFalse();
            _lock.IsTaken.Should().BeFalse();
        }

        [Fact]
        public async void StartAutoProlongingTask_LockTaken_ProlongsInBackground()
        {
            ConfigureLockTakeAsync(() => true);
            ConfigureProlongAsync(() => true).Verifiable();
                
            await _lock.TryTakeAsync(TimeSpan.FromSeconds(1));
            _lock.StartAutoProlongingTask(TimeSpan.FromMilliseconds(10), TimeSpan.FromMilliseconds(100));
            await Task.Delay(100);

            _redisMaster.Verify(x => x.ProlongLockAsync(_lockKey, _lockId, It.IsAny<TimeSpan>()), Times.AtLeast(3));
        }

        [Fact]
        public async void ReleaseAsync_LockTaken_ReleasesLockAsync()
        {
            ConfigureLockTakeAsync(() => true);
            ConfigureLockReleaseAsync();

            await _lock.TryTakeAsync(TimeSpan.MaxValue);
            await _lock.ReleaseAsync();

            _redisMaster.Verify(x => x.LockRelaseAsync(_lockKey, _lockId), Times.Once);
            _lock.IsTaken.Should().BeFalse();
        }

        [Fact]
        public async void ReleaseAsync_LockIsAutoProlonged_CancelsProlongation()
        {
            ConfigureLockTakeAsync(() => true);
            ConfigureLockReleaseAsync();
            int prolongCalledTimes = 0;
            ConfigureProlongAsync(() => true).Callback(() => { prolongCalledTimes++;});

            await _lock.TryTakeAsync(TimeSpan.MaxValue);
            _lock.StartAutoProlongingTask(TimeSpan.FromMilliseconds(10), TimeSpan.FromMilliseconds(100));
            await Task.Delay(100);
            var prolontedTimesBeforeRelease = prolongCalledTimes;

            await _lock.ReleaseAsync();
            await Task.Delay(100);

            prolongCalledTimes.Should().BeLessOrEqualTo(prolontedTimesBeforeRelease + 1);
        }

        private IReturnsResult<IRedisMasterAsync> ConfigureProlongAsync(Func<bool> result)
        {
            return _redisMaster.Setup(x => x.ProlongLockAsync(_lockKey, _lockId, It.IsAny<TimeSpan>()))
                .ReturnsAsync(result);
        }

        private void ConfigureLockReleaseAsync()
        {
            _redisMaster
                .Setup(x => x.LockRelaseAsync(_lockKey, _lockId)).ReturnsAsync(true);
        }

        private IReturnsResult<IRedisMasterAsync> ConfigureLockTakeAsync(Func<bool> result)
        {
            return _redisMaster
                .Setup(x => x.LockTakeAsync(_lockKey, _lockId, It.IsAny<TimeSpan>()))
                .ReturnsAsync(result);
        }

        public void Dispose()
        {
            _lock.ReleaseAsync().Wait();
        }
    }
}