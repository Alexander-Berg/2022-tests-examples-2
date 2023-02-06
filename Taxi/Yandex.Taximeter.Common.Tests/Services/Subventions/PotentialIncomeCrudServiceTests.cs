using System;
using System.Collections.Generic;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Services.Driver;
using Yandex.Taximeter.Core.Services.Subventions;
using Yandex.Taximeter.Test.Utils.Fakes;
using Yandex.Taximeter.Test.Utils.Redis;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Services.Subventions
{
    public class PotentialIncomeCrudServiceTests
    {
        private readonly PotentialIncomeCrudService _service;

        private static readonly DriverId DriverId = new DriverId(TestUtils.NewId(), TestUtils.NewId());

        public PotentialIncomeCrudServiceTests()
        {
            var redis = new RedisManagerMock().RedisManager.Object;
            _service = new PotentialIncomeCrudService(redis, new FakeLoggerFactory());
        }

        [Fact]
        public async void SetAsync_NotEmptyRules_SetsPotentialIncomeToMax()
        {
            const decimal expected = 1000;
            var rules = new List<SubventionRule>
            {
                new SubventionRule {Sum = 100},
                new SubventionRule {Sum = 0},
                new SubventionRule {Sum = expected},
            };

            await _service.SetAsync(DriverId, rules);

            var actual = await _service.GetAsync(DriverId.Db, DriverId.Driver);
            actual.Value.Should().Be(expected);
        }

        [Fact]
        public async void SetAsync_NullOrEmptyRules_RemovesValue()
        {
            await _service.SetAsync(DriverId, new[] {new SubventionRule {Sum = 100}});

            await _service.SetAsync(DriverId, Array.Empty<SubventionRule>());

            var actual = await _service.GetAsync(DriverId.Db, DriverId.Driver);
            actual.Should().BeNull();
        }
    }
}