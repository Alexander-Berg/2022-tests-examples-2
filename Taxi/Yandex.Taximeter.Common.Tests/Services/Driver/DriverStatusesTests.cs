using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Services.Driver;

namespace Yandex.Taximeter.Common.Tests.Services.Driver
{
    public class DriverStatusesTests
    {
        [Fact]
        public void CrossStatus_IntegratorStatusFree_EqualsToTaximeterStatus()
        {
            var statuses = new DriverStatuses(DriverServerStatus.InOrderFree);

            statuses.CrossStatus.Should().Be(DriverServerStatus.InOrderFree);
        }

        [Fact]
        public void CrossStatus_IntNotFree_TaximeterFree_EqualsToIntStatus()
        {
            var statuses = new DriverStatuses(
                DriverServerStatus.Free,
                DriverServerStatus.Busy);

            statuses.CrossStatus.Should().Be(DriverServerStatus.Busy);
        }

        [Fact]
        public void CrossStatus_IntNotFree_TaximeterNotFree_EqualsToTaximeterStatus()
        {
            var statuses = new DriverStatuses(
                DriverServerStatus.Offline,
                DriverServerStatus.Busy);

            statuses.CrossStatus.Should().Be(DriverServerStatus.Offline);
        }
    }
}