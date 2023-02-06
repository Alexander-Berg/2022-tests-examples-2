using System;
using System.Collections.Generic;
using System.Text;
using FluentAssertions;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Abstractions;
using Microsoft.AspNetCore.Mvc.Filters;
using Microsoft.AspNetCore.Routing;
using Microsoft.Extensions.Options;
using Xunit;
using Yandex.Taximeter.Core.Configuration.Options;
using Yandex.Taximeter.Core.Mvc.Authentication;
using Yandex.Taximeter.Core.Mvc.Filters;
using Yandex.Taximeter.Test.Utils;
using Yandex.Taximeter.Test.Utils.Fakes;

namespace Yandex.Taximeter.Common.Tests.Mvc.Filters
{
    public class ZendeskApiAuthorizationFilterTests
    {
        private readonly ZendeskApiAuthorizationFilter _filter;

        public ZendeskApiAuthorizationFilterTests()
        {
            _filter = new ZendeskApiAuthorizationFilter(
                new OptionsWrapper<ZendeskOptions>(new ZendeskOptions
                {
                    CallbackLogin = "login",
                    CallbackPassword = "pass"
                }));
        }

        [Fact]
        public async void OnAuthorizationAsync_InvalidCredentials_Returns403()
        {
            var context = new FakeHttpContext();
            context.Request.Headers[AuthenticationConsts.AUTHORIZATION_HEADER] = "invalid";
            var authContext = WrapAuthContext(context);

            await _filter.OnAuthorizationAsync(authContext);

            Assert.True(((StatusCodeResult)authContext.Result).StatusCode == 403);
        }

        [Fact]
        public async void OnAuthorizationAsync_ValidCredentials_Passes()
        {
            var context = new FakeHttpContext();
            var credentials = Convert.ToBase64String(Encoding.UTF8.GetBytes("login:pass"));
            context.Request.Headers[AuthenticationConsts.AUTHORIZATION_HEADER] = $"Basic {credentials}";
            var authContext = WrapAuthContext(context);

            await _filter.OnAuthorizationAsync(authContext);

            authContext.Result.Should().BeNull();
        }

        private static AuthorizationFilterContext WrapAuthContext(FakeHttpContext context)
            => new AuthorizationFilterContext(
                new ActionContext(context, new RouteData(), new ActionDescriptor()),
                new List<IFilterMetadata>());
    }
}