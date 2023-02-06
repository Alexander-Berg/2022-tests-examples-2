using System;
using System.ComponentModel.DataAnnotations;
using System.Globalization;
using System.Runtime.Serialization;
using System.Text;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Extensions;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Car;
using Yandex.Taximeter.Core.Services.Resources;

namespace Yandex.Taximeter.Common.Tests.Extensions
{
    public class EnumExtensionsTests
    {
        public enum SomeEnum
        {
            [EnumMember(Value = "first")] One,
            [EnumMember(Value = "second")] Two
        }

        [Fact]
        public void TestSerialization()
        {
            SomeEnum.One.GetSerializedValue().Should().Be("first");
            SomeEnum.Two.GetSerializedValue().Should().Be("second");
        }

        [Fact]
        public void TestGetValues()
        {
            var str = new StringBuilder();
            foreach (var item in Enum.GetValues(typeof(SomeEnum)))
            {
                str.Append(item.As<SomeEnum>().GetSerializedValue());
            }
            str.ToString().Should().Be("firstsecond");
        }
    
        [Fact]
        public void TestDeserialization()
        {
            EnumExtensions.FromSerializedValue<SomeEnum>("first").Should().Be(SomeEnum.One);
            EnumExtensions.FromSerializedValue<SomeEnum>("second").Should().Be(SomeEnum.Two);
        }
        
        [Fact]
        public void Localize_DEBUG_DisplayAttributeMissing_ThrowsException()
        {
#if DEBUG
            Assert.Throws<InvalidOperationException>(
                () => EnumWithoutDisplayAttr.TestVal.Localize());
#endif
        }

        [Fact]
        public void Localize_RELEASE_DisplayAttributeMissing_ReturnsStringifiedEnumValue()
        {
#if RELEASE
            var value = EnumWithoutDisplayAttr.TestVal.Localize();
            value.Should().Be(EnumWithDisplayAttr.TestVal.ToString());
#endif
        }

        [Fact]
        public void Localize_DisplayAttributeApplied_ReturnsStringFromResource()
        {
            var actual = EnumWithDisplayAttr.TestVal.Localize();
            Backend.DriverPayGroup_Transaction.Should().Be(actual);

            actual = EnumWithDisplayAttr2.TestVal.Localize();
            Backend.DriverPayGroup_Commission.Should().Be(actual);

            actual = EnumWithDisplayAttr2.TestVal2.Localize();
            Backend.DriverPayGroup_Coupon.Should().Be(actual);
        }

        [Fact]
        public void Localize_CultureSpecified_DisplayAttributeApplied_ReturnsStringFromResource()
        {
            var culture = CultureInfo.CurrentUICulture.TwoLetterISOLanguageName == "ru"
                ? CultureInfo.GetCultureInfo("uk")
                : CultureInfo.GetCultureInfo("ru");

            var resourceManager = Backend.ResourceManager;

            var actual = EnumWithDisplayAttr.TestVal.Localize(culture);
            resourceManager.GetString(nameof(Backend.DriverPayGroup_Transaction), culture).
                Should().Be(actual);

            actual = EnumWithDisplayAttr2.TestVal.Localize(culture);
            resourceManager.GetString(nameof(Backend.DriverPayGroup_Commission), culture)
                .Should().Be(actual);

            actual = EnumWithDisplayAttr2.TestVal2.Localize(culture);
            resourceManager.GetString(nameof(Backend.DriverPayGroup_Coupon), culture)
                .Should().Be(actual);
        }

        [Fact]
        public void Localize_DisplayAttributeWithoutResourceType_ReturnsName()
        {
            EnumWithoutResourceType.TestVal.Localize().Should().Be("test_val");
        }

        [Fact]
        public void Enum_FromFlagsTest()
        {
            var items = new[]
            {
                CategoryFlags.Econom,
                CategoryFlags.ComfortPlus
            };

            items.FromFlags().Should().Be(CategoryFlags.Econom | CategoryFlags.ComfortPlus);
        }


        [Fact]
        public void Enum_ToFlagsTest()
        {
            var category = CategoryFlags.ComfortPlus | CategoryFlags.Econom;
            category.ToFlags().Should().BeEquivalentTo(new[] { CategoryFlags.Econom, CategoryFlags.ComfortPlus});
        }


        [Fact]
        public void ToFlagsTest()
        {
            var category = new CarCategory {Econom = true, Comfort = true};
            var flags = category.ToFlags<CategoryFlags, CarCategory>();
            flags.Should().Be(CategoryFlags.Econom | CategoryFlags.Comfort);
        }

        [Fact]
        public void ToObjectTest()
        {
            var flags = CategoryFlags.Econom | CategoryFlags.Comfort;
            var category = flags.ToObject<CategoryFlags, CarCategory>();
            category.Econom.Should().BeTrue();
            category.Comfort.Should().BeTrue();
            category.ComfortPlus.Should().BeFalse();
        }

        private enum EnumWithoutDisplayAttr
        {
            TestVal
        }
        
        private enum EnumWithDisplayAttr
        {
            [Display(ResourceType = typeof(Backend), Name = nameof(Backend.DriverPayGroup_Transaction))]
            TestVal
        }

        private enum EnumWithDisplayAttr2
        {
            [Display(ResourceType = typeof(Backend), Name = nameof(Backend.DriverPayGroup_Commission))]
            TestVal,
            [Display(ResourceType = typeof(Backend), Name = nameof(Backend.DriverPayGroup_Coupon))]
            TestVal2
        }

        public enum EnumWithoutResourceType
        {
            [Display(Name = "test_val")]
            TestVal
        }
    }
}
