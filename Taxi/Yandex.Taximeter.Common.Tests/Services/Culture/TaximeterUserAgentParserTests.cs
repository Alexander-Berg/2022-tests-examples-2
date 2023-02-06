using System.Collections.Generic;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Services.Version;

// ReSharper disable HeapView.BoxingAllocation

namespace Yandex.Taximeter.Common.Tests.Services.Culture
{
    public struct MockAppParams
    {
        public string Version;
        public string Platform;
        public string VersionType;
        public string PlatformVersion;
        public string Brand;
        public string BuildType;
    }

    public class UserAgentParserTests
    {
        public static IEnumerable<object[]> OkData =>
            new List<object[]>
            {
                new object[]
                {
                    new MockAppParams
                    {
                        Version = "9.10 (1234)",
                        Platform = "android",
                        VersionType = "vezet"
                    },
                    new TaximeterApp(
                        version: new TaximeterVersion(9, 10, 1234),
                        platform: TaximeterPlatform.Android,
                        buildType: TaximeterBuildType.Default,
                        brand: TaximeterBrand.Vezet,
                        platformVersion: null
                    )
                },
                new object[]
                {
                    new MockAppParams
                    {
                        Version = "10.12 (23455)",
                        Platform = "ios",
                        PlatformVersion = "13.0.1",
                        Brand = "yandex",
                        BuildType = "x",
                    },
                    new TaximeterApp(
                        version: new TaximeterVersion(10, 12, 23455),
                        platform: TaximeterPlatform.Ios,
                        buildType: TaximeterBuildType.Experimental,
                        brand: TaximeterBrand.Yandex,
                        platformVersion: new PlatformVersion(13, 0, 1)
                    )
                },
                new object[]
                {
                    new MockAppParams
                    {
                        Version = "13.22 (2121)",
                        Platform = "android",
                        PlatformVersion = "15.0.1",
                        Brand = "yango",
                        BuildType = "beta",
                    },
                    new TaximeterApp(
                        version: new TaximeterVersion(13, 22, 2121),
                        platform: TaximeterPlatform.Android,
                        buildType: TaximeterBuildType.Beta,
                        brand: TaximeterBrand.Yango,
                        platformVersion: new PlatformVersion(15, 0, 1)
                    )
                },
                new object[]
                {
                    new MockAppParams
                    {
                        Version = "0.0 (0)",
                        Platform = "android",
                        PlatformVersion = "",
                        Brand = "",
                        BuildType = "",
                    },
                    new TaximeterApp(
                        version: new TaximeterVersion(),
                        platform: TaximeterPlatform.Android,
                        buildType: TaximeterBuildType.Default,
                        brand: TaximeterBrand.Yandex,
                        platformVersion: null
                    )
                },
            };

        [Theory]
        [MemberData(nameof(OkData))]
        public void Ok(MockAppParams appParams, TaximeterApp expectedApp)
        {
            var parsingResult = TaximeterAppParser.ParseParams(
                version: appParams.Version,
                platform: appParams.Platform,
                versionType: appParams.VersionType,
                platformVersion: appParams.PlatformVersion,
                brand: appParams.Brand,
                buildType: appParams.BuildType);

            parsingResult.Should().Be(expectedApp);
        }
    }
}
