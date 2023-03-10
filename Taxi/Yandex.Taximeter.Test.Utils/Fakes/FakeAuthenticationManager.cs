using System;
using System.Collections.Generic;
using System.Security.Claims;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Http.Authentication;
using Microsoft.AspNetCore.Http.Features.Authentication;

namespace Yandex.Taximeter.Test.Utils.Fakes
{
    public class FakeAuthenticationManager : AuthenticationManager
    {
        private HttpContext _context;

        public override IEnumerable<AuthenticationDescription> GetAuthenticationSchemes()
        {
            throw new NotImplementedException();
        }

        public override Task AuthenticateAsync(AuthenticateContext context)
        {
            throw new NotImplementedException();
        }

        public override HttpContext HttpContext { get; }

        public override Task SignOutAsync(string authenticationScheme, AuthenticationProperties properties)
        {
            throw new NotImplementedException();
        }

        public override Task SignInAsync(string authenticationScheme, ClaimsPrincipal principal, AuthenticationProperties properties)
        {
            throw new NotImplementedException();
        }

        public override Task ChallengeAsync(string authenticationScheme, AuthenticationProperties properties, ChallengeBehavior behavior)
        {
            throw new NotImplementedException();
        }

        public override Task<AuthenticateInfo> GetAuthenticateInfoAsync(string authenticationScheme)
        {
            throw new NotImplementedException();
        }

        public void SetContext(HttpContext context)
        {
            _context = context;
        }
    }
}