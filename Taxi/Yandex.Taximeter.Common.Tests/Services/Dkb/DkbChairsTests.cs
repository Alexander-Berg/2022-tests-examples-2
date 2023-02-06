using System.Collections.Generic;
using FluentAssertions;
using Newtonsoft.Json;
using Xunit;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Car;

namespace Yandex.Taximeter.Common.Tests.Services.Dkb
{
    public class DkbChairsTests
    {
        [Fact]
        public void TestEquals()
        {
            var chair1 = new CarChair
            {
                Brand = "Test",
                Isofix = true,
                Categories = new SortedSet<int> {1, 2, 3}
            };

            var chair2 = new CarChair
            {
                Brand = "Test",
                Isofix = true,
                Categories = new SortedSet<int> { 1, 2, 3 }
            };

            var chair3 = new CarChair
            {
                Brand = "Test",
                Isofix = true,
                Categories = new SortedSet<int> { 0, 1 }
            };

            chair1.Should().Be(chair2);
            chair1.Should().NotBe(chair3);
        }

        [Fact]
        public void TestSerialize()
        {
            var chair = new CarChair
            {
                Brand = "Test",
                Isofix = true,
                Categories = new SortedSet<int> { 1, 2, 3 }
            };
            var chairJson = JsonConvert.SerializeObject(chair);
            chairJson.Should().Be("{\"brand\":\"Test\",\"categories\":[1,2,3],\"isofix\":true,\"settings\":30}");
        }

        [Fact]
        public void TestCreate()
        {
            var chair = new CarChair("Test", (ChairSettings)30);
            chair.Brand.Should().Be("Test");
            chair.Isofix.Should().BeTrue();
            chair.Categories.Should().BeEquivalentTo(new[] { 1, 2, 3 });
        }

        [Fact]
        public void TestDeserialize_New()
        {
            var chairJson = "{'brand':'Test','isofix':true,'categories':[1,2,3]}";
            var chair = JsonConvert.DeserializeObject<CarChair>(chairJson);
            chair.Brand.Should().Be("Test");
            chair.Isofix.Should().BeTrue();
            chair.Categories.Should().BeEquivalentTo(new[] { 1, 2, 3 });
        }
    }
}
