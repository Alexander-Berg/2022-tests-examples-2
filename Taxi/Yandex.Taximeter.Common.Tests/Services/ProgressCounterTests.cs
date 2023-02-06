using System.Collections.Concurrent;
using System.Linq;
using System.Threading.Tasks;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Services;

namespace Yandex.Taximeter.Common.Tests.Services
{
    public class ProgressCounterTests
    {
        const int TOTAL_PROGRESS = 70;
        const int PROGRESS_STEP = 10;

        [Fact]
        public void Increment_TotalCountGreaterThanNumberOfSteps_ReturnsAllProgressValuesBetween0AndTotalPercents()
        {
            const int totalCount = 59;
            var progressCounter = new ProgressCounter(totalCount, TOTAL_PROGRESS, PROGRESS_STEP);

            var progressChanges = IterateCounter(totalCount, progressCounter);

            for (var progressVal = PROGRESS_STEP; progressVal <= TOTAL_PROGRESS; progressVal += PROGRESS_STEP)
                progressChanges.Count(x => x == progressVal).Should().Be(1);
        }

        [Fact]
        public void Increment_TotalCountLessThanNumberOfSteps_ReturnsAtLeastMaxProgressValue()
        {
            const int totalCount = 3;
            var progressCounter = new ProgressCounter(totalCount, TOTAL_PROGRESS, PROGRESS_STEP);

            var progressChanges = IterateCounter(totalCount, progressCounter);

            progressChanges.Count(x => x == TOTAL_PROGRESS).Should().Be(1);
        }

        private static ConcurrentBag<int> IterateCounter(int totalCount, ProgressCounter progressCounter)
        {
            var progressChanges = new ConcurrentBag<int>();
            Parallel.For(0, totalCount, new ParallelOptions {MaxDegreeOfParallelism = 8},
                _ =>
                {
                    var newProgress = progressCounter.Increment();
                    if (newProgress != null)
                        progressChanges.Add(newProgress.Value);
                });
            return progressChanges;
        }
    }
}