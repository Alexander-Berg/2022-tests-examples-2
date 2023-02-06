using System;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Helper;

namespace Yandex.Taximeter.Common.Tests.Extensions
{
    public class TypeExtensionsTests
    {
        [Theory]
        [InlineData("MyNamespace.SomeType", 32, "MyNamespace.SomeType")]
        [InlineData("MyNamespace.SomeType", 20, "MyNamespace.SomeType")]
        [InlineData("MyNamespace.SomeType", 19, "SomeType")]
        [InlineData("MyNamespace.SomeType", 8, "SomeType")]
        [InlineData("MyNamespace.SomeType+SubType", 8, "SubType")]
        [InlineData("MyNamespace.SomeType", 7, "omeType")]
        [InlineData("MyNamespace.SomeType", 4, "Type")]
        [InlineData("MyNamespace.MyModule.SomeType", 25, "MyModule.SomeType")]
        [InlineData("MyNamespace.MyModule.SomeType", 10, "SomeType")]
        public void TestTrimTypeName(string typeName, int len, string expected)
        {
            var result = typeName.TrimTypeName(len);
            result.Should().Be(expected);
        }
    }
}