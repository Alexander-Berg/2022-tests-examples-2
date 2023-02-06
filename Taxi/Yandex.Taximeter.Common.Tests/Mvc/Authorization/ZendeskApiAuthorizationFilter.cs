using System;
using System.Text;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Mvc.Authentication;
using Yandex.Taximeter.Test.Utils;
using Yandex.Taximeter.Test.Utils.Fakes;

namespace Yandex.Taximeter.Common.Tests.Mvc.Authorization
{
    public class BasicAuthorizationCredentialsTests
    {
        [Fact]
        public void Parse_AcceptableHeader_ParsesCredentials()
        {
            var request = new FakeHttpRequest();
            var requestCredentials = Convert.ToBase64String(Encoding.UTF8.GetBytes("log:pass"));
            request.Headers[AuthenticationConsts.AUTHORIZATION_HEADER] = $"Basic {requestCredentials}";

            var credentials = BasicAuthorizationCredentials.Parse(request);

            AssertCredentials(credentials, "log", "pass");
        }

        [Fact]
        public void Parse_HeaderNotPresent_ReturnsEmpty()
        {
            var request = new FakeHttpRequest();

            var credentials = BasicAuthorizationCredentials.Parse(request);

            AssertCredentials(credentials, null, null);
        }

        [Fact]
        public void Parse_HeaderNotBasic_ReturnsEmpty()
        {
            var request = new FakeHttpRequest();
            request.Headers[AuthenticationConsts.AUTHORIZATION_HEADER] = "Bearer some-token";

            var credentials = BasicAuthorizationCredentials.Parse(request);

            AssertCredentials(credentials, null, null);
        }

        [Fact]
        public void Parse_HeaderNotParseable_ReturnsEmpty()
        {
            var request = new FakeHttpRequest();
            var requestCredentials = Convert.ToBase64String(Encoding.UTF8.GetBytes("cr1:cr2:cr3"));
            request.Headers[AuthenticationConsts.AUTHORIZATION_HEADER] = $"Basic {requestCredentials}";

            var credentials = BasicAuthorizationCredentials.Parse(request);

            AssertCredentials(credentials, null, null, $"В строке {nameof(requestCredentials)} более одного разделителя");
        }

        private static void AssertCredentials(BasicAuthorizationCredentials actualCredentials,
            string expectedLogin, string expectedPassword,
            string explanation = null)
        {
            actualCredentials.Login.Should().Be(expectedLogin, explanation);
            actualCredentials.Password.Should().Be(expectedPassword, explanation);
        }
    }
}