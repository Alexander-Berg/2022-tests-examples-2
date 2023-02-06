using System.Net.Http;
using Newtonsoft.Json;
using Xunit;
using Yandex.Taximeter.Core.Services.Settings;

namespace Yandex.Taximeter.Common.Tests.Services.Settings
{
    public class ClientQosSettingsTests
    {
        
        [Theory]
        [InlineData("{'timeout-ms':1000,'attempts':2}",1000,2)]
        [InlineData("{'timeout-ms':1000,'retries':2}",1000,2)]
        [InlineData("{'timeout_ms':1000,'attempts':2}",1000,2)]
        [InlineData("{'timeout':1000,'attempts':2}",1000,2)]
        [InlineData("{'timeout-ms':1000,'attempts':0}",1000,1)]
        [InlineData("{'timeout-ms':1000}",1000,1)]
        public void TestClientQosHandleSettingsDeserialize(string json, int timeout, int retries)
        {
            var settings = JsonConvert.DeserializeObject<ClientQosHandleSettings>(json);
            Assert.Equal(timeout, settings.TimeoutMs);
            Assert.Equal(retries, settings.Attempts);
        }
        
        [Theory]
        [InlineData("{'__default__':{'timeout-ms':1000,'attempts':2}}", "/v1/test", "POST", 1000,2)]
        [InlineData("{'__default__':{'timeout-ms':2000,'attempts':4},'POST /v1/test':{'timeout-ms':1000,'attempts':2}}", "/v1/test", "POST", 1000,2)]
        [InlineData("{'__default__':{'timeout-ms':2000,'attempts':4},'POST /v1/test':{'timeout-ms':1000,'attempts':2}}", "/v1/test", "GET", 2000,4)]
        [InlineData("{'__default__':{'timeout-ms':2000,'attempts':4},'/v1/test':{'timeout-ms':1500,'attempts':3},'POST /v1/test':{'timeout-ms':1000,'attempts':2}}", "/v1/test", "POST", 1000,2)]
        [InlineData("{'__default__':{'timeout-ms':2000,'attempts':4},'/v1/test@post':{'timeout-ms':1000,'attempts':2}}", "/v1/test", "POST", 1000,2)]
        [InlineData("{'__default__':{'timeout-ms':2000,'attempts':4},'/v1/test@post':{'timeout-ms':1000,'attempts':2}}", "/v1/test", "GET", 2000,4)]
        [InlineData("{'__default__':{'timeout-ms':2000,'attempts':4},'/v1/test':{'timeout-ms':1500,'attempts':3},'/v1/test@post':{'timeout-ms':1000,'attempts':2}}", "/v1/test", "POST", 1000,2)]
        [InlineData("{'__default__':{'timeout-ms':2000,'attempts':4},'/v1/test':{'timeout-ms':1000,'attempts':2}}", "/v1/test", "POST", 1000,2)]
        public void TestClientQosSettings(string json, string handle, string method, int timeout, int retries)
        {
            var settings = JsonConvert.DeserializeObject<ClientQosSettings>(json);
            var httpMethod = new HttpMethod(method);
            var handleSettings = settings.Get(httpMethod, handle);
            
            Assert.Equal(timeout, handleSettings.TimeoutMs);
            Assert.Equal(retries, handleSettings.Attempts);

        }

    }
}