using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;

namespace Yandex.Taximeter.Test.Utils.Fakes
{
    public class FakeHttpMessageHandler : HttpMessageHandler
    {
        public FakeHttpMessageHandler() : this(new HttpResponseMessage())
        {
        }

        public FakeHttpMessageHandler(HttpResponseMessage response)
            :this(response, new List<HttpRequestMessage>())
        {}

        public FakeHttpMessageHandler(HttpResponseMessage response, List<HttpRequestMessage> requestsCollection)
        {
            Response = response;
            Requests = requestsCollection;
        }

        public List<HttpRequestMessage> Requests { get; }

        public HttpResponseMessage Response { get; set; }
        
        public Func<HttpRequestMessage, Task> ValidateRequestAsync { get; set; }

        public void SetResourceAsResponse(string resourcePath)
        {
            var responseBody = File.ReadAllText(resourcePath);
            Response = new HttpResponseMessage(HttpStatusCode.OK)
            {
                Content = new StringContent(responseBody)
            };
        }

        protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request,
            CancellationToken cancellationToken)
        {
            if (ValidateRequestAsync != null)
            {
                await ValidateRequestAsync(request);
            }
            Requests.Add(request);
            return Response;
        }
    }
}
