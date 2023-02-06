using System;
using System.Linq;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Services.Driver.StatusLog;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Services.Driver.StatusLog
{
    public class DriverStatusLogDataTests
    {
        private readonly DriverStatusLogType[] _typesWithoutArgs = {
                DriverStatusLogType.AutoClose,
                DriverStatusLogType.DriverStatusChange,
                DriverStatusLogType.PortsMeet,
                DriverStatusLogType.PortsBye,
                DriverStatusLogType.PortsAll
            };

        private readonly DriverStatusLogType[] _typesWithNumericArg = {
                DriverStatusLogType.RobotDistance,
                DriverStatusLogType.SetWorkStartTime,
                DriverStatusLogType.SetWorkEndTime,
                DriverStatusLogType.SetWaitTime
            };

        private readonly DriverStatusLogType[] _typesWithStringArg = {
            DriverStatusLogType.DriverStatusChange,
            DriverStatusLogType.SearchPoint,
            DriverStatusLogType.SearchPointHome
        };

        private readonly DriverStatusLogType[] _typesWithDateTimeArg = {
            DriverStatusLogType.RobotSearchDate
        };

        private readonly DriverStatusLogType[] _typesWithSwitchArg = {
            DriverStatusLogType.SwitchRobot,
            DriverStatusLogType.SwitchRobotAddr,
            DriverStatusLogType.SwitchRobotHome,
            DriverStatusLogType.SwitchPorts,
            DriverStatusLogType.SwitchEconom,
            DriverStatusLogType.SwitchComfort,
            DriverStatusLogType.SwitchBusiness,
            DriverStatusLogType.SwitchMinivan,
            DriverStatusLogType.SwitchComfPlus,
            DriverStatusLogType.SwitchUniversal,
            DriverStatusLogType.SwitchChain,
            DriverStatusLogType.SwitchStart,
            DriverStatusLogType.SwitchStandard,
            DriverStatusLogType.SwitchChildTariff,
            DriverStatusLogType.SwitchUltimate,
            DriverStatusLogType.SwitchMaybach,
            DriverStatusLogType.SwitchPromo,
            DriverStatusLogType.SwitchPremiumVan,
            DriverStatusLogType.SwitchPremiumSuv,
            DriverStatusLogType.SwitchSuv,
            DriverStatusLogType.SwitchPersonalDriver,
            DriverStatusLogType.SwitchCargo,
            DriverStatusLogType.SwitchNight,
            DriverStatusLogType.SwitchExpress,
            DriverStatusLogType.SwitchCourier,
            DriverStatusLogType.SwitchEda,
            DriverStatusLogType.SwitchLavka,
            DriverStatusLogType.SwitchScooters,
        };

        [Fact]
        public void Serialization_LogTypeWithoutArgs_SerializesAndDeserializes()
        {
            foreach (var type in _typesWithoutArgs)
                TestUtils.CheckJsonSerialization(new DriverStatusLogData(type));
        }

        [Fact]
        public void Serialization_LogTypeWithNumericArg_SerializesAndDeserializes()
        {
            foreach (var type in _typesWithNumericArg)
                TestUtils.CheckJsonSerialization(new DriverStatusLogData(type, (long)new Random().Next()));
            foreach (var type in _typesWithNumericArg)
                TestUtils.CheckJsonSerialization(new DriverStatusLogData(type, new Random().Next()));
        }

        [Fact]
        public void Serialization_LogTypeWithStringArg_SerializesAndDeserializes()
        {
            foreach (var type in _typesWithStringArg)
                TestUtils.CheckJsonSerialization(new DriverStatusLogData(type, "strArg"));
        }

        [Fact]
        public void Serialization_LogTypeWithDateTimeArg_SerializesAndDeserializes()
        {
            foreach (var type in _typesWithDateTimeArg)
                TestUtils.CheckJsonSerialization(new DriverStatusLogData(type, DateTime.UtcNow.Date));
        }

        [Fact]
        public void Serialization_LogTypeWithSwitchArg_SerializesAndDeserializes()
        {
            foreach (var type in _typesWithSwitchArg)
                TestUtils.CheckJsonSerialization(
                    new DriverStatusLogData(type, new Random().Next(2).ToString()));
        }

        [Fact]
        public void Serialization_AllLogTypesTested()
        {
            _typesWithSwitchArg.Concat(_typesWithStringArg)
                .Concat(_typesWithDateTimeArg)
                .Concat(_typesWithSwitchArg)
                .Concat(_typesWithNumericArg)
                .Concat(_typesWithoutArgs)
                .Distinct()
                .Should().BeEquivalentTo(
                    Enum.GetValues(typeof(DriverStatusLogType)).Cast<DriverStatusLogType>());
        }
    }
}
