using System;
using Yandex.Taximeter.Core.Services.Driver.StatusLog;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Services.Driver;
using Yandex.Taximeter.Test.Utils.Utils;

#pragma warning disable 618

namespace Yandex.Taximeter.Common.Tests.Services.Driver.StatusLog
{
    public class DriverStatusLogTests
    {
        [Fact]
        public void Serialization_AnyFields_SerializesAndDeserializes()
        {
            var log = new DriverStatusLog
            {
                i = "i val",
                s = (int) DriverServerStatus.Free,
                t = DateTime.Now.Ticks,
                Data = new DriverStatusLogData(DriverStatusLogType.DriverStatusChange, "arg1", "arg2")
            };

            TestUtils.CheckJsonSerialization(log);
        }

        [Fact]
        public void Data_Set_ShouldSetRawMessage()
        {
            var log = new DriverStatusLog();
            log.RawMessage.Should().BeNullOrEmpty();
            log.Data = new DriverStatusLogData(DriverStatusLogType.SwitchChain, "1");
            log.RawMessage.Should().Be(log.Data.BuildMessage());
        }
    }
}
