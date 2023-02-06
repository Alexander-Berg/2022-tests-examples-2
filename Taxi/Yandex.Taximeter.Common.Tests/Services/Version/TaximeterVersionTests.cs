using System;
using FluentAssertions;
using Newtonsoft.Json;
using Xunit;
using Yandex.Taximeter.Core.Services.Version;
using Yandex.Taximeter.Test.Utils.Fakes;

namespace Yandex.Taximeter.Common.Tests.Services.Version
{
    public class TaximeterVersionTests
    {
        [Theory]
        [InlineData("8.00", 8, 0, 0)]
        [InlineData("8.01 (100)", 8, 1, 100)]
        [InlineData("8.01(100)", 8, 1, 100)]
        [InlineData("8,02", 8, 2, 0)]
        [InlineData("Taximeter 8,02,101", 8, 2, 101)]
        [InlineData("Unknown", 0, 0, 0)]
        public void TestVersionParser(string versionStr, ushort major, ushort minor, uint build)
        {
            var version = TaximeterVersion.Parse(versionStr, false);
            var expectedVersion = new TaximeterVersion(major, minor, build);
            version.Should().Be(expectedVersion);
        }

        [Theory]
        [InlineData(8, 0, 0, "8.00")]
        [InlineData(8, 1, 100, "8.01 (100)")]
        [InlineData(0,0,0, "")]
        public void TestToString(ushort major, ushort minor, uint build, string expectedStr)
        {
            var version = new TaximeterVersion(major, minor, build);
            version.ToString().Should().Be(expectedStr);
        }

        [Fact]
        public void TestUserAgent()
        {
            var ctx = new FakeHttpContext();
            try
            {
                var version = ctx.Request.TaximeterVersion(new FakeLogger());
                version.Should().Be(TaximeterVersion.Empty);
            }
            catch (Exception ex)
            {
                // User-Agent header is absent
                ex.Message.Should().Contain("Object reference not set to an instance of an object");
            }

            ctx = new FakeHttpContext();
            ctx.Request.Headers["X-Request-Platform"] = "android";
            ctx.Request.Headers["X-Request-Application-Version"] = "8.01 (101)";
            {
                var version = ctx.Request.TaximeterVersion(new FakeLogger());
                version.Should().Be(new TaximeterVersion(8, 1, 101));
            }
        }


        [Theory]
        [InlineData("8.00", 8, 0, 0)]
        [InlineData("\"8.01 (100)\"", 8, 1, 100)]
        [InlineData("{\"Major\":8,\"Minor\":20,\"Build\":149,\"Revision\":-1,\"MajorRevision\":-1,\"MinorRevision\":-1}", 8, 20, 149)]
        public void TestJsonDeserialize(string versionJson, ushort major, ushort minor, uint build)
        {
            var version = JsonConvert.DeserializeObject<TaximeterVersion>(versionJson);
            version.Should().Be(new TaximeterVersion(major,minor,build));
        }
    }
}
