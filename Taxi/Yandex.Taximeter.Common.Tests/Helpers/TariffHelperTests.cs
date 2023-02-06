using FluentAssertions;
using Newtonsoft.Json;
using Xunit;
using Yandex.Taximeter.Core.Helper;
#pragma warning disable 612

namespace Yandex.Taximeter.Common.Tests.Helpers
{
    public class TariffHelperTests: IClassFixture<CommonFixture>
    {
        [Theory]
        [InlineData("По расписанию", TariffHelper.Tariff.WorkType.Scheduled)]
        [InlineData("", null)]
        public void TariffItem_SerializedWithRawWorkType_EnumPropertyIsValid(string rawVal, TariffHelper.Tariff.WorkType? parsedVal)
        {
            var item = new TariffHelper.Tariff.Item {WorkTypeRaw = rawVal };
            var serialized = JsonConvert.SerializeObject(item);
            var deserialized = JsonConvert.DeserializeObject<TariffHelper.Tariff.Item>(serialized);
            deserialized.WorkType.Should().Be(parsedVal);
            deserialized.WorkTypeRaw.Should().Be(rawVal);
        }

        [Theory]
        [InlineData("Всегда", TariffHelper.Tariff.WorkType.Always)]
        [InlineData("", null)]
        public void TariffItem_SerializedWithEnumWorkType_DeserializedRawPropertyIsValid(string rawVal, TariffHelper.Tariff.WorkType? workType)
        {
            var item = new TariffHelper.Tariff.Item { WorkType = workType };
            var serialized = JsonConvert.SerializeObject(item);
            var deserialized = JsonConvert.DeserializeObject<TariffHelper.Tariff.Item>(serialized);
            deserialized.WorkType.Should().Be(workType);
            deserialized.WorkTypeRaw.Should().Be(rawVal);
        }

        [Theory]
        [InlineData("Всегда", TariffHelper.Tariff.WorkType.Always)]
        [InlineData("", null)]
        public void TariffItem_WorkTypeRawSet_EnumPropertyShouldChangeValue(string rawVal, TariffHelper.Tariff.WorkType? workTypeToSet)
        {
            var item = new TariffHelper.Tariff.Item { WorkTypeRaw = "По расписанию" };
            item.WorkType.Should().Be(TariffHelper.Tariff.WorkType.Scheduled);
            item.WorkType = workTypeToSet;
            item.WorkType.Should().Be(workTypeToSet);
            item.WorkTypeRaw.Should().Be(rawVal);
        }
    }
}
