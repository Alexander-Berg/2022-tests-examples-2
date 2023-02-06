using Newtonsoft.Json;
using Xunit;
using Yandex.Taximeter.Core.Services.Settings;

namespace Yandex.Taximeter.Common.Tests.Services.Settings
{
    public class BillingReportsGatewaySettingsTests
    {
        
        [Theory]
        [InlineData("{'work_mode':'disabled'}",false,false)]
        [InlineData("{'work_mode':'enabled'}",true,false)]
        [InlineData("{'work_mode':'enabled_fallback'}",true,true)]
        public void TestBillingReportsGatewaySettingsDeserialize(string json, bool enabled, bool fallbackEnabled)
        {
            var settings = JsonConvert.DeserializeObject<BillingReportsGatewaySettings>(json);
            Assert.Equal(enabled, settings.Enabled);
            Assert.Equal(fallbackEnabled, settings.FallbackEnabled);
        }
    }
}