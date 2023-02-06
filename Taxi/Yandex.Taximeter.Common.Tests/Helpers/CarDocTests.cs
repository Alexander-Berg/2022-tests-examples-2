using System;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Car;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Helpers
{
    public class CarDocTests
    {
        [Fact]
        public void CarItem_Serialization_ShouldBeDeserializedWithInitialItems()
        {
            var item = new CarDoc
            {
                ParkId = "park",
                CarId = "car",
                Transmission = CarTransmission.Mechanical,
                BoosterCount = 2,
                Color = "Белый",
                Category = new CarCategory { Business = true },
                Status = CarWorkStatus.InGarage
            };

            TestUtils.CheckJsonSerialization(item);
        }

        [Fact]
        public void CategoryFlags_Parse()
        {
            ((CategoryFlags)Enum.Parse(typeof(CategoryFlags), "Econom, Comfort"))
                .Should()
                .HaveFlag(CategoryFlags.Comfort);
        }

        [Fact]
        public void CategoryFlags_FromYandexCategory()
        {
            var result = CarCategoryHelper.FromYandexCategory("econom", "business");
            result.Should().Be(CategoryFlags.Econom | CategoryFlags.Comfort);
        }
    }
}