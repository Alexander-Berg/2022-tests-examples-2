using System.Net.Http;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Services.Communications;
using Yandex.Taximeter.Core.Services.Push;
using Yandex.Taximeter.Core.Services.Push.Messages;
using Yandex.Taximeter.Core.Utils;

namespace Yandex.Taximeter.Common.Tests.Utils
{
    public class PushPayloadWithApnsForcedTest
    {
        private static string CreateRequest(object repacked)
        {
            var request = new HttpRequestMessage(HttpMethod.Post, "/driver/notification/push")
            {
                Content = new JsonContent(new CommunicationsGateway.DriverPushRequestSingleModel
                {
                    ParkId = "park",
                    DriverId = "driver",
                    Action = "13",
                    Code = 13,
                    CollapseKey = "123",
                    Data = repacked,
                    Ttl = 64
                })
            };

            var body = request.Content.ReadAsStringAsync().Result;
            return body;
        }

        [Fact]
        public void TestRepack()
        {
            object payloadData = new PushOrderCancel {Order = "order_id"};
            var repacked = new PushPayloadWithApnsForced(payloadData);

            var body = CreateRequest(repacked);
            body.Should()
                .Be(
                    @"{""dbid"":""park"",""uuid"":""driver"",""collapse_key"":""123"",""code"":13,""action"":""13"",""ttl"":64,""data"":{""payload"":{""fake_empty"":""nothing""},""repack"":{""apns"":{""aps"":{""order"":""order_id"",""content-available"":1}}}}}");
        }
    }
}
