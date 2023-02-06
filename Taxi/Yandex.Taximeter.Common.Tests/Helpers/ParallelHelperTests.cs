using System;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Helper;

namespace Yandex.Taximeter.Common.Tests.Helpers
{
    public class ParallelHelperTests
    {
        public class LimitedParallelizm
        {
            [Fact]
            public async void ParallelForEach_AllTasksSucceed_ManyElements()
            {
                var rand = new Random();
                var items = await Enumerable
                    .Range(0, 1000)
                    .ParallelForEach(16, async i =>
                {
                    await Task.Delay(rand.Next(5, 10));
                    return i * 2;
                });

                items.Should().BeEquivalentTo(Enumerable.Range(0, 1000).Select(i => i * 2));
            }


            [Fact]
            public async void ParallelForEach_AllTasksSucceed_FewElements()
            {
                var rand = new Random();

                var items = await Enumerable.Range(0, 5)
                    .ParallelForEach(16, async i =>
                    {
                        await Task.Delay(rand.Next(5, 10));
                        return i * 2;
                    });

                items.Should().BeEquivalentTo(Enumerable.Range(0, 5).Select(i => i * 2));
            }


            [Fact]
            public async void ParallelForEach_ExceptionsOccur_ThrowsException()
            {
                //Проверяем, что итерация остановится при Exception, т.е. не всё перечисление пройдёт
                var enumeratedCount = 0;
                var rand = new Random();
                await Assert.ThrowsAsync<Exception>(async () =>
                    await Enumerable.Range(0, 200)
                    .Select(x =>
                        {
                            enumeratedCount++;
                            return x;
                        })
                        .ParallelForEach(16, async x =>
                        {
                            if (x == 50) throw new Exception("FAILED");
                            await Task.Delay(rand.Next(5, 10));
                        }));

                enumeratedCount.Should().BeLessThan(200);
            }
        }

        public class UnlimitedParallelizm
        {
            [Fact]
            public async void ParallelForEach_AllTasksSucceed_ReturnsOrderedResults()
            {
                var rand = new Random();

                var items = await Enumerable.Range(0, 100).ParallelForEach(async x =>
                {
                    await Task.Delay(rand.Next(5, 10));
                    return x * 2;
                });

                items.Should().BeEquivalentTo(Enumerable.Range(0, 100).Select(i => i * 2));

            }

            [Fact]
            public async void ParallelForEach_ExceptionsOccur_ThrowsException()
            {
                var rand = new Random();
                await Assert.ThrowsAsync<Exception>(async () =>
                    await Enumerable.Range(0, 200)
                    .ParallelForEach(16, async x =>
                    {
                        if (x == 100) throw new Exception("FAILED");
                        await Task.Delay(rand.Next(5, 10));
                    }));
            }
        }
    }
}