using Autofac;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using Xunit;
using Yandex.Taximeter.Core.Services.Sms;
using Yandex.Taximeter.Core.Services.Sms.Providers;
using Yandex.Taximeter.Test.Utils;
using Yandex.Taximeter.Test.Utils.Fakes;

namespace Yandex.Taximeter.Common.Tests.Services.Sms
{
    public class SmsProviderTests: IClassFixture<CommonFixture>
    {
        public ISmsProviderFactory GetSmsProviderFactory()
        {
            var containerBuilder = new ContainerBuilder();
            containerBuilder.RegisterModule<SmsModule>();
            containerBuilder.RegisterType<FakeLoggerFactory>().As<ILoggerFactory>();
            var container = containerBuilder.Build();

            return container.Resolve<ISmsProviderFactory>();
        }

        [Fact]
        public void TestSimpleSmsProvider()
        {
            var provider = GetSmsProviderFactory().Get(new SmsConfig
            {
                provider = "iqsms.ru",
                login = "1111",
                password = "2222",
                enable = true,
                sender = "3333"
            });
            provider.Should().NotBeNull();
            provider.Should().BeOfType<IqSmsRu>();
        }

        [Fact]
        public void TestDefaultSmsProvider()
        {
            var provider = GetSmsProviderFactory().Get(new SmsConfig
            {
                provider = "some-unknown-provider",
                login = "1111",
                password = "2222",
                enable = true,
                sender = "3333",
                token = "4444"
            });
            provider.Should().NotBeNull();
            provider.Should().BeOfType<SmscRu>();
        }
    }
}
