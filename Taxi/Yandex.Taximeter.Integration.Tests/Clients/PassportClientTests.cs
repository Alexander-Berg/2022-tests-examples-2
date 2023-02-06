using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.Extensions.DependencyInjection;
using Xunit;
using Yandex.Taximeter.Core.Clients.Passport;
using Yandex.Taximeter.Integration.Tests.Fixtures;

namespace Yandex.Taximeter.Integration.Tests.Clients
{
    public class PassportClientTests : IClassFixture<FullFixture>
    {
        private readonly FullFixture _fixture;
        private readonly IPassportClient _passportClient;

        public PassportClientTests(FullFixture fixture)
        {
            _fixture = fixture;
            var factory = _fixture.ServiceProvider.GetService<IPassportClientFactory>();
            _passportClient = factory.YandexTeam;
        }

        [Fact]
        public async Task GetInfo()
        {
            var myIp = await GetMyIP(AddressFamily.InterNetwork);
            var passportInfo = await _passportClient.SessionIdAsync(
                "3:1460721600.5.0.1460721600000:K2UDaa3NAWkIBAAAuAYCKg:8c.1|4002748489.0.2|146949.574403.P3ExLsuSNqL3XDQy1zoHjs0t7eg",
                myIp,
                PassportFields.DisplayName);

            passportInfo.Should().NotBeNull();
        }

        [Fact]
        public async Task GetInfoByLogin()
        {
            var myIp = await GetMyIP(AddressFamily.InterNetwork);
            var passportInfo = await _passportClient.UserInfoAsync("azinoviev", myIp, PassportFields.DisplayName);

            passportInfo.Should().NotBeNull();
            passportInfo.Login.Should().BeEquivalentTo("azinoviev");
            passportInfo.Uid.Should().BeEquivalentTo("4002748489");
        }

        public async Task<string> GetMyIP(AddressFamily addressFamily = AddressFamily.InterNetworkV6)
        {
            var hostName = Dns.GetHostName();
            var ipEntry = await Dns.GetHostEntryAsync(hostName);
            var ipList = ipEntry.AddressList.Where(x => x.AddressFamily == addressFamily);
            var ip = ipList.First();
            return ip.ToString();
        }
    }
}
