using System.Collections.Generic;
using FluentAssertions;
using Newtonsoft.Json;
using Xunit;
using Yandex.Taximeter.Core.Models.Orders;
using Yandex.Taximeter.Core.Utils;

namespace Yandex.Taximeter.Common.Tests.Utils
{
    internal class DictTest
    {
        public Dictionary<OrderPhoneType, string> phones;
    }

    public class NewtonJObjectJTokenTest
    {
        [Fact]
        public void TestOrderPhoneType()
        {
            var test = new DictTest
            {
                phones = new Dictionary<OrderPhoneType, string>
                {
                    {OrderPhoneType.Dispatch, "+71231231212"}, {OrderPhoneType.Driver, "+74564564545"}
                }
            };

            var infoInvalid = JsonConvert.SerializeObject(test);
            infoInvalid.Should().Be("{\"phones\":{\"Dispatch\":\"+71231231212\",\"Driver\":\"+74564564545\"}}");
        }

        [Fact]
        public void TestValidInvalidHeaders()
        {
            var headersValid =
                "{\n    \"id\": \"cb3fdf529d604e4e9861ff4fcab95b8e\",\n    \"url\": \"/add-order\",\n    \"method\": \"POST\",\n    \"headers\": {\n      \"Content-Type\": \"application/json\"\n    },\n    \"content\": \"{\\\"park_id\\\":\\\"9aec0117764843419da8585647658f34\\\",\\\"driver_id\\\":\\\"a3de0628ff384dd2b96156fce1b70e54\\\",\\\"order_id\\\":\\\"2bd062e694c92d5995f0655cb8f11896\\\",\\\"total\\\":198.0,\\\"is_corp\\\":false,\\\"receipt_date\\\":\\\"2020-04-09T11:38:56.646436Z\\\",\\\"checkout_date\\\":\\\"2020-04-09T11:38:56.646436Z\\\",\\\"is_cashless\\\":true}\"\n  }";
            var headersInvalid =
                "{\n    \"id\": \"b41958dff7374b23afaddd75cbe23070\",\n    \"url\": \"/add-order\",\n    \"method\": \"POST\",\n    \"content\": \"{\\\"park_id\\\":\\\"279613e0fb264efcb7bb5f97b7d585bf\\\",\\\"driver_id\\\":\\\"832c207f6e5543d88fa8005f40223edd\\\",\\\"order_id\\\":\\\"aaea386e3cb91b198e29d5970079c620\\\",\\\"total\\\":181.0,\\\"is_cashless\\\":false,\\\"is_corp\\\":false,\\\"receipt_date\\\":\\\"2020-04-09T01:11:14.530204Z\\\",\\\"checkout_date\\\":\\\"2020-04-09T01:11:14.530204Z\\\"}\",\n    \"headers\": \"{\\\"Content-Type\\\":\\\"application/json\\\"}\"\n  }";

            var infoValid = JsonConvert.DeserializeObject<HttpRequestInfo>(headersValid);
            var infoInvalid = JsonConvert.DeserializeObject<HttpRequestInfo>(headersInvalid);

            infoInvalid.GetHeaders()["Content-Type"].Should().Be("application/json");
            infoValid.GetHeaders()["Content-Type"].Should().Be("application/json");
        }
    }
}
