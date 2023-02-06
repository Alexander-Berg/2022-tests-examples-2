using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Utils;

namespace Yandex.Taximeter.Common.Tests.Services.Driver
{
    public class PhoneUtilsTests
    {
        [Theory]
        [InlineData("+7(926) 111-22-33", "+79261112233")] // Москва
        [InlineData("8(926) 111-22-33", "+79261112233")]
        [InlineData("+7(926) 111 22 33", "+79261112233")]
        [InlineData("8(926) 111 22 33", "+79261112233")]
        [InlineData("+7 926 111 22 33", "+79261112233")]
        [InlineData("8 926 111 22 33", "+79261112233")]
        [InlineData("9684997400", "+79684997400")]
        [InlineData(" 79259162654  ", "+79259162654")]
        [InlineData("37493419927", "+37493419927")] // Ереван
        [InlineData("374 77008081 ", "+37477008081")]
        [InlineData("+37493419927", "+37493419927")]
        [InlineData("+374 77008081 ", "+37477008081")]
        [InlineData("380993760848", "+380993760848")] // Киев
        [InlineData("+380993760848", "+380993760848")]
        [InlineData("375297779750", "+375297779750")] // Минск
        [InlineData("+375447008646", "+375447008646")]
        [InlineData("87072223051", "+77072223051")] // Алматы
        [InlineData("+77025555808", "+77025555808")]
        public void NormalizePhoneNumberTest(string phone, string expectedPhone)
        {
            var normalizedPhone = PhoneUtils.NormalizePhoneNumber(phone);
            normalizedPhone.Should().Be(expectedPhone);
        }
    }
}
