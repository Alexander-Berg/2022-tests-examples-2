using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Extensions;

namespace Yandex.Taximeter.Common.Tests.Extensions
{
    public class AsyncEnumerableExtensionsTests
    {
        [Fact]
        public async void TaskForEachAsync_EmptyEnumerable_DoesNothing()
        {
            var processedItems = new List<int>();

            await AsyncEnumerable.Empty<int>().TaskForEachAsync(async val =>
            {
                await Task.Delay(1);
                processedItems.Add(val);
            });

            processedItems.Should().BeEmpty();
        }

        [Fact]
        public async void TaskForEachAsync_NotEmptyEnumerable_ProcessesItemsSequentially()
        {
            var processedItems = new List<int>();

            await AsyncEnumerable.Range(0, 100).TaskForEachAsync(async val =>
            {
                await Task.Delay(1);
                processedItems.Add(val);
            });

            Assert.True(processedItems.SequenceEqual(Enumerable.Range(0, 100)));
        }
    }
}