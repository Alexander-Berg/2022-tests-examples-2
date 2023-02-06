using System;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Extensions;

namespace Yandex.Taximeter.Common.Tests.Utils
{
    public class StringTrimmerTest
    {
        [Fact]
        public void TestStringTrimmer_Test()
        {
            "b\u0061\u0308\u0061\u0308".TrimToLen(2).Should().Be("b\u0061\u0308");
            "b\u0061\u0308\u0061\u0308".TrimToLen(1).Should().Be("b\u0061");
            "bb\u0061\u0308\u0061\u0308".TrimToLen(1).Should().Be("b");
            "bb\u0061\u0308\u0061\u0308".TrimToLen(4).Should().Be("bb\u0061\u0308");
            "bb\u0061\u0308\u0061\u0308".TrimToLen(5).Should().Be("bb\u0061\u0308\u0061");
            "\ud83d\udc6e КОНСТАНТИН\ud83d\ude962\ufe0f\u20e3".TrimToLen(16).Should().Be("\ud83d\udc6e КОНСТАНТИН\ud83d\ude962");
        }
    }
}
