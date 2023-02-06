using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Http.Internal;

namespace Yandex.Taximeter.Test.Utils.Fakes
{
    public class FakeHttpRequest : HttpRequest
    {
        private readonly IHeaderDictionary _headerDictionary = new HeaderDictionary();
        private IRequestCookieCollection _cookies = new RequestCookieCollection();
        private HttpContext _httpContext;

        public FakeHttpRequest(HttpContext httpContext)
        {
            _httpContext = httpContext;
        }

        public FakeHttpRequest()
        {}

        public override Task<IFormCollection> ReadFormAsync(CancellationToken cancellationToken = new CancellationToken())
        {
            throw new NotImplementedException();
        }

        public override HttpContext HttpContext => _httpContext;
        public override string Method { get; set; }
        public override string Scheme { get; set; }
        public override bool IsHttps { get; set; }
        public override HostString Host { get; set; }
        public override PathString PathBase { get; set; }
        public override PathString Path { get; set; }
        public override QueryString QueryString { get; set; }
        public override IQueryCollection Query { get; set; }
        public override string Protocol { get; set; }
        public override IHeaderDictionary Headers => _headerDictionary;

        public override IRequestCookieCollection Cookies
        {
            get { return _cookies; }
            set { _cookies = value; }
        }

        public override long? ContentLength { get; set; }
        public override string ContentType { get; set; }
        public override Stream Body { get; set; }
        public override bool HasFormContentType { get; }
        public override IFormCollection Form { get; set; }
    }
}