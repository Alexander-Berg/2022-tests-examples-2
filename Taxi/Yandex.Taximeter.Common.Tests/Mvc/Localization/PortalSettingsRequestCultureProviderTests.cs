using System.Collections.Generic;
using System.Linq;
using FluentAssertions;
using Microsoft.AspNetCore.Http.Internal;
using Xunit;
using Yandex.Taximeter.Core.Mvc.Localization;
using Yandex.Taximeter.Test.Utils;
using Yandex.Taximeter.Test.Utils.Fakes;

namespace Yandex.Taximeter.Common.Tests.Mvc.Localization
{
    public class PortalSettingsRequestCultureProviderTests
    {
        private readonly PortalSettingsRequestCultureProvider _provider
            = new PortalSettingsRequestCultureProvider(new FakeLoggerFactory());

        [Fact]
        public void DetermineProviderCultureResult_NoCookie_ReturnsNull()
        {
            var result = _provider.DetermineProviderCultureResult(new FakeHttpContext()).Result;
            result.Should().BeNull();
        }

        [Theory]
        [InlineData("YycCAAMA", "en")]
        [InlineData("YycCAAIA", "uk")]
        [InlineData("YycCAAQrATMA", "kk")]
        [InlineData("YysBMwA", default(string))]
        [InlineData("YyYBASsBMzoBAQA", default(string))]
        public void DetermineProviderCultureResult_ValidCookie_ParsesCultureFromCookie(string myCookie, string expetedLang)
        {
            var context = BuildContextWithMyCookie(myCookie);

            var result = _provider.DetermineProviderCultureResult(context).Result;

            var resultCulture = result?.UICultures?.FirstOrDefault();
            resultCulture?.Value.Should().Be(expetedLang);
        }

        [Fact]
        public void DetermineProviderCultureResult_InvalidCookie_ReturnsNull()
        {
            var context = BuildContextWithMyCookie("invalid cookie val 123");

            var result = _provider.DetermineProviderCultureResult(context).Result;

            result.Should().BeNull();
        }

        private static FakeHttpContext BuildContextWithMyCookie(string myCookie)
        {
            var context = new FakeHttpContext();
            context.Request.Cookies = new RequestCookieCollection(
                new Dictionary<string, string> { { "my", myCookie } });
            return context;
        }
    }
}
