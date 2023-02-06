using Microsoft.AspNetCore.Http;

namespace Yandex.Taximeter.Test.Utils.Fakes
{
    public class FakeHttpContextAccessor : IHttpContextAccessor
    {
        public FakeHttpContext FakeHttpContext { get; set; } = new FakeHttpContext();

        public HttpContext HttpContext
        {
            get { return FakeHttpContext; }
            set { FakeHttpContext = (FakeHttpContext)value; }
        }
    }
}