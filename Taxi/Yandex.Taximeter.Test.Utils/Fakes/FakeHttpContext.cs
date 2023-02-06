using System;
using System.Collections.Generic;
using System.Security.Claims;
using System.Threading;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Http.Authentication;
using Microsoft.AspNetCore.Http.Features;

namespace Yandex.Taximeter.Test.Utils.Fakes
{
    public class FakeHttpContext : HttpContext
    {
        private readonly HttpRequest _request;
        private readonly IFeatureCollection _featureCollection;

        public FakeHttpContext()
        {
            _featureCollection = new FeatureCollection();
            _request = new FakeHttpRequest(this);
            _request.Headers["X-Real-IP"] = "127.0.0.1";
        }

        public override void Abort()
        {
            throw new NotImplementedException();
        }

        public override IFeatureCollection Features => _featureCollection;
        public override HttpRequest Request => _request;
        public override HttpResponse Response { get; } = null;
        public override ConnectionInfo Connection { get; } = null;
        public override WebSocketManager WebSockets { get; } = null;
        
        [Obsolete("This is obsolete and will be removed in a future version. The recommended alternative is to use Microsoft.AspNetCore.Authentication.AuthenticationHttpContextExtensions. See https://go.microsoft.com/fwlink/?linkid=845470.")]
        public override AuthenticationManager Authentication => null;
        
        public override ClaimsPrincipal User { get; set; }
        public override IDictionary<object, object> Items { get; set; } = new Dictionary<object, object>();
        public override IServiceProvider RequestServices { get; set; }
        public override CancellationToken RequestAborted { get; set; }
        public override string TraceIdentifier { get; set; }
        public override ISession Session { get; set; }

        public void SetUser(string userName)
        {
            User = new ClaimsPrincipal(
                new ClaimsIdentity(
                    new[] {new Claim(ClaimTypes.Name, userName)}));
        }
    }
}