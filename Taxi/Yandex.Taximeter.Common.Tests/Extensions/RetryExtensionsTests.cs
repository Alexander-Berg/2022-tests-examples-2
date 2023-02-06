using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;
using Yandex.Taximeter.Core.Extensions;

namespace Yandex.Taximeter.Common.Tests.Extensions
{
    /*
     * TODO: тесты могут флапать.
     * Нужно разбить Retry и его тесты на непосредственно ретрай с некоторой стратегией, абстрагированной от времени,
     * и стратегию, вычисляющую временные промежутки для ретрая.
     * Этог можно добиться, завернув Timespan, возвращаемый IDelayStrategy на Task.
    */
    public class RetryExtensionsTests
    {
        private readonly Mock<ILogger> _loggerMock;
        private readonly List<string> _retryInfo = new List<string>();

        public RetryExtensionsTests()
        {
            _loggerMock = new Mock<ILogger>();
            _loggerMock.Setup(x => x.Log(It.Is<LogLevel>(l=>l == LogLevel.Warning),
                It.IsAny<EventId>(), It.IsAny<object>(), It.IsAny<Exception>(), It.IsAny<Func<object, Exception, string>>()))
                .Callback<LogLevel, EventId, object, Exception, Func<object, Exception, string>>((level, @event, message, exception, formatter) => 
                {
                    _retryInfo.Add(message.ToString());
                });
        }

        [Fact(Skip = "Флапает из-за временных зависимостей")]
        public async Task FixedRightLogAndDelay()
        {
            var stopWatch = new Stopwatch();
            var firstTime = TimeSpan.Zero;
            
            Task<int> RetriableFunc()
            {
                if (firstTime == TimeSpan.Zero)
                    firstTime = stopWatch.Elapsed;
                
                throw new ExceptionA();
            }

            var maxRetry = 10;
            var delay = TimeSpan.FromMilliseconds(100);

            stopWatch.Start();
            await Assert.ThrowsAsync<ExceptionA>(
                () => Retry.Fixed(RetriableFunc, maxRetry, delay, _loggerMock.Object));
            var elapsed = stopWatch.Elapsed - firstTime;

            _retryInfo.Select(i => i.Split(':')[0]).Should()
                .ContainInOrder(Enumerable.Range(1, maxRetry).Select(i => $"Attempt {i}/{maxRetry}"));

            var expectedTime = TimeSpan.FromMilliseconds(delay.TotalMilliseconds * (maxRetry - 1));
            var precicion = CalcTimeAssertPrecision(maxRetry);
            elapsed.Should().BeCloseTo(expectedTime, precicion);
        }
        
        [Fact(Skip = "Флапает из-за временных зависимостей")]
        public async Task ExponentialRightLogAndDelay()
        {
            var stopWatch = new Stopwatch();
            var firstTime = TimeSpan.Zero;
            
            Task<int> RetriableFunc()
            {
                if (firstTime == TimeSpan.Zero)
                    firstTime = stopWatch.Elapsed;
                
                throw new ExceptionA();
            }

            var maxRetry = 5;
            var delay = TimeSpan.FromMilliseconds(50);

            stopWatch.Start();
            await Assert.ThrowsAsync<ExceptionA>(
                () => Retry.Exponential(RetriableFunc, maxRetry, delay, _loggerMock.Object));
            var elapsed = stopWatch.Elapsed - firstTime;
            
            _retryInfo.Select(i => i.Split(':')[0]).Should()
                .ContainInOrder(Enumerable.Range(1, maxRetry).Select(i => $"Attempt {i}/{maxRetry}"));

            var expectedTime = TimeSpan.FromMilliseconds(delay.TotalMilliseconds * (Math.Pow(2, maxRetry - 1) - 1));
            var precicion = CalcTimeAssertPrecision(maxRetry);
            elapsed.Should().BeCloseTo(expectedTime, precicion);
        }
        
        [Fact(Skip = "Флапает из-за временных зависимостей")]
        public async Task ExponentialDecayRightLogAndDelay()
        {
            var stopWatch = new Stopwatch();
            var firstTime = TimeSpan.Zero;
            
            Task<int> RetriableFunc()
            {
                if (firstTime == TimeSpan.Zero)
                    firstTime = stopWatch.Elapsed;
                
                throw new ExceptionA();
            }

            var maxRetry = 5;
            var delay = TimeSpan.FromMilliseconds(1000);
            stopWatch.Start();
            await Assert.ThrowsAsync<ExceptionA>(
                () => Retry.ExponentialDecay(RetriableFunc, maxRetry, delay, _loggerMock.Object));
            var elapsed = stopWatch.Elapsed - firstTime;
            
            _retryInfo.Select(i => i.Split(':')[0]).Should()
                .ContainInOrder(Enumerable.Range(1, maxRetry).Select(i => $"Attempt {i}/{maxRetry}"));

            var expectedTime = TimeSpan.FromMilliseconds(delay.TotalMilliseconds * (2 - Math.Pow(2, 2 - maxRetry)));
            var precicion = CalcTimeAssertPrecision(5 * maxRetry);
            elapsed.Should().BeCloseTo(expectedTime, precicion);
        }
        
        [Fact(Skip = "флапает из-за временных гонок")]
        public async Task ExponentialFixedRightLogAndDelay()
        {
            var stopWatch = new Stopwatch();
            var firstTime = TimeSpan.Zero;
            
            Task<int> RetriableFunc()
            {
                if (firstTime == TimeSpan.Zero)
                    firstTime = stopWatch.Elapsed;
                
                throw new ExceptionA();
            }

            var maxExpRetry = 5;
            var maxFixedRetry = 5;
            var delay = TimeSpan.FromMilliseconds(50);
            stopWatch.Start();
            await Assert.ThrowsAsync<ExceptionA>(
                () => Retry.ExponentialFixed(RetriableFunc, maxExpRetry, maxFixedRetry, delay, _loggerMock.Object));
            var elapsed = stopWatch.Elapsed - firstTime;

            _retryInfo.Select(i => i.Split(':')[0]).Should()
                .ContainInOrder(Enumerable.Range(1, maxExpRetry + maxFixedRetry).Select(i => $"Attempt {i}/{maxExpRetry + maxFixedRetry}"));

            var expectedTime = TimeSpan.FromMilliseconds(
                delay.TotalMilliseconds * (Math.Pow(2, maxExpRetry) - 1 + Math.Pow(2, maxExpRetry - 1) * (maxFixedRetry - 1)));
            var precicion = CalcTimeAssertPrecision(maxExpRetry + maxFixedRetry);
            elapsed.Should().BeCloseTo(expectedTime, precicion);
        }
        

        [Fact]
        public async Task FixedRightShouldRetry()
        {
            Task<int> RetriableFunc()
            {
                throw new ExceptionB();
            }

            var maxRetry = 10;
            var delay = TimeSpan.FromMilliseconds(100);
            var retryTask = Retry.Fixed(RetriableFunc, maxRetry, delay, _loggerMock.Object, 
                (ex, nextDelay) => ex is ExceptionA);
            
            await Assert.ThrowsAsync<ExceptionB>(() => retryTask);

            _retryInfo.Count.Should().Be(1);
        }
        
        [Fact]
        public async Task ExponentialRightShouldRetry()
        {
            Task<int> RetriableFunc()
            {
                throw new ExceptionB();
            }

            var maxRetry = 10;
            var delay = TimeSpan.FromMilliseconds(100);
            var retryTask = Retry.Exponential(RetriableFunc, maxRetry, delay, _loggerMock.Object, 
                (ex, nextDelay) => ex is ExceptionA);
            
            await Assert.ThrowsAsync<ExceptionB>(() => retryTask);

            _retryInfo.Count.Should().Be(1);
        }

        [Fact]
        public async Task ExponentialDecayRightShouldRetry()
        {
            Task<int> RetriableFunc()
            {
                throw new ExceptionB();
            }

            var maxRetry = 10;
            var delay = TimeSpan.FromMilliseconds(100);
            var retryTask = Retry.ExponentialDecay(RetriableFunc, maxRetry, delay, _loggerMock.Object, 
                (ex, nextDelay) => ex is ExceptionA);
            
            await Assert.ThrowsAsync<ExceptionB>(() => retryTask);

            _retryInfo.Count.Should().Be(1);
        }
        
        [Fact(Skip = "Флапает из-за временных зависимостей")]
        public async Task ExponentialFixedRightShouldRetry()
        {
            Task<int> RetriableFunc()
            {
                throw new ExceptionB();
            }

            var maxExpRetry = 5;
            var maxFixedRetry = 5;
            var delay = TimeSpan.FromMilliseconds(100);
            var retryTask = Retry.ExponentialFixed(RetriableFunc, maxExpRetry, maxFixedRetry, delay, _loggerMock.Object, 
                (ex, nextDelay)=> ex is ExceptionA);
            
            await Assert.ThrowsAsync<ExceptionB>(() => retryTask);

            _retryInfo.Count.Should().Be(1);
        }

        private int CalcTimeAssertPrecision(int retryCount) => 10 * retryCount;

        private class ExceptionA : Exception
        {

        }

        private class ExceptionB : Exception
        {

        }
    }
}
