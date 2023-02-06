using System.Linq;
using System.Xml.Linq;
using FluentAssertions;
using Newtonsoft.Json;
using Xunit;
using Yandex.Taximeter.Core.Code;
using Yandex.Taximeter.Core.Helper;

namespace Yandex.Taximeter.Common.Tests.Clients
{
    [Collection(nameof(YandexClientTestsBase))]
    public class YandexClientVoiceForwardingTests
    {
        [Fact]
        public void SeralizationTest()
        {
            var xml = XDocument.Parse(@"
<Forwardings>
  <Forwarding>
    <Orderid>1111</Orderid>
    <Phone>+70000000000</Phone>
    <Ext>123</Ext>
    <TtlSeconds>100</TtlSeconds>
  </Forwarding>
</Forwardings>");


            var voiceForwarding = (from e in xml.Root.Elements("Forwarding")
                let forwarding = StaticHelper.FromXml<VoiceForwarding>(e)
                select forwarding).FirstOrDefault();

            voiceForwarding.Should().NotBeNull();
            voiceForwarding.OrderId.Should().BeEquivalentTo("1111");
            voiceForwarding.Phone.Should().BeEquivalentTo("+70000000000");
            voiceForwarding.Ext.Should().BeEquivalentTo("123");
            voiceForwarding.TtlSeconds.Should().Be(100L);

            var json = JsonConvert.SerializeObject(voiceForwarding, Formatting.None);
            json.Should().BeEquivalentTo(
                @"{""order_id"":""1111"",""phone"":""+70000000000"",""ext"":""123"",""ttl_seconds"":100}");
        }
    }
}