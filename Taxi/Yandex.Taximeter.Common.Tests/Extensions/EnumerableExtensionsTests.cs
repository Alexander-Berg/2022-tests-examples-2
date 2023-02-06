using System;
using System.Linq;
using System.Linq.Expressions;
using FluentAssertions;
using Microsoft.AspNetCore.Mvc.DataAnnotations.Internal;
using Xunit;
using Yandex.Taximeter.Core.Extensions;
using Yandex.Taximeter.Core.Models.Orders;
using Yandex.Taximeter.Core.Utils;

namespace Yandex.Taximeter.Common.Tests.Extensions
{
    public class EnumerableExtensionsTests
    {
        [Fact]
        public void TestTakeLast_EmptySequence_ReturnsEmpty()
        {
            var result = Enumerable.Empty<int>().TakeLast(5).ToArray();
            result.Length.Should().Be(0);
        }
        
        [Fact]
        public void TestTakeLast_ZeroCount_ReturnsEmpty()
        {
            var result = Enumerable.Range(0,10).TakeLast(0).ToArray();
            result.Length.Should().Be(0);
        }
        
        [Fact]
        public void TestTakeLast_SameAsCount_ReturnsWhole()
        {
            var result = Enumerable.Range(0,10).TakeLast(10).ToArray();
            result.Should().BeEquivalentTo(Enumerable.Range(0,10));
        }
        
        [Fact]
        public void TestTakeLast_GreaterThanCount_ReturnsWhole()
        {
            var result = Enumerable.Range(0,10).TakeLast(18).ToArray();
            result.Should().BeEquivalentTo(Enumerable.Range(0,10));
        }
        
        [Fact]
        public void TestTakeLast_LessThanCount_ReturnsPart()
        {
            var result = Enumerable.Range(0,10).TakeLast(7).ToArray();
            result.Should().BeEquivalentTo(Enumerable.Range(3,7));
        }

        private class TestData
        {
            public string StringProperty { get; set; }
            
            public int IntProperty { get; set; }
        }
        
        [Fact]
        public void TestComparer()
        {
            var data = new[]
            {
                new TestData {StringProperty = "b", IntProperty = 1},
                new TestData {StringProperty = "b", IntProperty = 2},
                new TestData {StringProperty = "b", IntProperty = 3},
                new TestData {StringProperty = "a", IntProperty = 1},
                new TestData {StringProperty = "c", IntProperty = 4},
            };
            
            Array.Sort(data, ComparerBuilder<TestData>.OrderBy(x=>x.StringProperty).ThenByDescending(x=>x.IntProperty));
            data.Should().BeEquivalentTo(new[]
            {
                new TestData {StringProperty = "a", IntProperty = 1},
                new TestData {StringProperty = "b", IntProperty = 3},
                new TestData {StringProperty = "b", IntProperty = 2},
                new TestData {StringProperty = "b", IntProperty = 1},
                new TestData {StringProperty = "c", IntProperty = 4},
            }, o=> o.WithStrictOrdering());
        }
    }
}