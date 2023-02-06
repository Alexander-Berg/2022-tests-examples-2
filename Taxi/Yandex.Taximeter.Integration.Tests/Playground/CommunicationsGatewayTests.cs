using System.Threading.Tasks;
using Microsoft.Extensions.DependencyInjection;
using Xunit;
using Yandex.Taximeter.Core.Services.Communications;
using Yandex.Taximeter.Core.Services.Driver;
using Yandex.Taximeter.Core.Services.Push;
using Yandex.Taximeter.Core.Services.Push.Messages;
using Yandex.Taximeter.Integration.Tests.Fixtures;

namespace Yandex.Taximeter.Integration.Tests.Playground
{
    public class CommunicationsGatewayTests : IClassFixture<FatFixture>
    {
        private readonly ICommunicationsGateway _communicationsGateway;

        public CommunicationsGatewayTests(FatFixture fixture)
        {
            _communicationsGateway = fixture.ServiceProvider.GetService<ICommunicationsGateway>();
        }

        [Fact]
        public async Task Test1()
        {
            var driver = new DriverId("7ad36bc7560449998acbe2c57a75c293", "98eb55c39e3c42bb8de00fe0dce933c3");

            var s = new PushAlert("Test");
            await _communicationsGateway.SendDriverPushAsync(driver, "id", PushMessageAction.MessageNew,
                s, "Alert:1");
        }
    }
}
