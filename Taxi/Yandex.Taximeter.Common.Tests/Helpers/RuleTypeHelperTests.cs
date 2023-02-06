using FluentAssertions;
using Newtonsoft.Json;
using Xunit;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Helpers
{
    public class RuleTypeHelperTests
    {
        public class Item
        {
            [Fact]
            public void Serialization_IsYandex_SerializesAndDeserializesCancelCostAs0()
            {
                var item = new RuleTypeItem
                {
                    Name = "Яндекс",
                    CancelCost = 1
                };
                item.isYandex().Should().BeTrue();
                item.CancelCost.Should().Be(0);

                var deserialized = SerializeAndDeserialize(item);

                deserialized.isYandex().Should().BeTrue();
                deserialized.CancelCost.Should().Be(0);
            }

            [Fact]
            public void Serialization_IsYandex_InPartnerCase_SerializesAndDeserializesCancelCostAs0()
            {
                var item = new RuleTypeItem
                {
                    Name = RuleTypeHelper.DefaultNames.YandexToPartner[RuleTypeHelper.DefaultNames.YANDEX],
                    CancelCost = 1
                };
                item.isYandex().Should().BeTrue();
                item.CancelCost.Should().Be(0);
               
                TestUtils.CheckJsonSerialization(item);
            }
            
            [Fact]
            public void Serialization_NotIsYandex_SerializesAndDeserializesOriginalCancelCost()
            {
                var item = new RuleTypeItem
                {
                    CancelCost = 1
                };
                item.isYandex().Should().BeFalse();
                item.CancelCost.Should().Be(1);

                var deserialized = SerializeAndDeserialize(item);

                deserialized.isYandex().Should().BeFalse();
                deserialized.CancelCost.Should().Be(1);
            }

            private static RuleTypeItem SerializeAndDeserialize(RuleTypeItem item)
                => JsonConvert.DeserializeObject<RuleTypeItem>(JsonConvert.SerializeObject(item));
        }
    }
}