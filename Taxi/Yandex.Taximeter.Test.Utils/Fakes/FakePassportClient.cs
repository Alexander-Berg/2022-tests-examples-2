using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.Extensions.Options;
using Yandex.Taximeter.Core.Clients.Passport;
using Yandex.Taximeter.Core.Configuration.Options;
using Yandex.Taximeter.Core.Dto;

namespace Yandex.Taximeter.Test.Utils.Fakes
{
    public class FakePassportClientFactory : IPassportClientFactory
    {
        private readonly FakePassportClient _passportClient;

        public FakePassportClientFactory(FakePassportClient passportClient)
        {
            _passportClient = passportClient;
        }

        public IPassportClient Create(IOptions<PassportOptions> options)
        {
            return _passportClient;
        }

        public IPassportClient Yandex => _passportClient;
        public IPassportClient YandexTeam => _passportClient;

        public IPassportClient GetForHost(string host)
        {
            return _passportClient;
        }
    }

    public class FakePassportClient : IPassportClient
    {
        public IList<PassportInfoDto> PassportInfos { get; } = new List<PassportInfoDto>();

        public void AddPassportInfo(PassportInfoDto dto)
        {
            PassportInfos.Add(dto);
        }

        public string GetLoginUrl(string returnUrl)
        {
            throw new NotImplementedException();
        }

        public string GetLogoutUrl(string yandexUidCookie)
        {
            throw new NotImplementedException();
        }

        public Task<PassportInfoDto> SessionIdAsync(string sessionId, string userIp, PassportFields additionalFields, string sslSessionId = null)
        {
            throw new NotImplementedException();
        }

        public Task<PassportInfoDto> UserInfoAsync(string login, string userIp, PassportFields additionalFields)
        {
            var info = PassportInfos.FirstOrDefault(x => x.Login == login);
            return Task.FromResult(info);
        }

        public bool IsValidFor(string host)
        {
            return true;
        }

        public Task<PassportInfoDto> OAuthAsync(string oauthToken, string userIp, PassportFields additionalFields)
        {
            throw new NotImplementedException();
        }

        public Task<PassportInfoDto> UserTicketAsync(string userTicket, PassportFields additionalFields)
        {
            throw new NotImplementedException();
        }
    }
}