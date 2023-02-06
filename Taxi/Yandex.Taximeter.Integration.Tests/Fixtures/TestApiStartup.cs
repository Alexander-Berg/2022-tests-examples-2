using Autofac;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Yandex.Taximeter.Core.Redis;

namespace Yandex.Taximeter.Integration.Tests.Fixtures
{
    public class TestApiStartup : Api.Startup
    {
        public TestApiStartup(IConfiguration configuration)
            : base(configuration)
        {
        }

        protected override void ConfigureServices(IServiceCollection services, ContainerBuilder builder)
        {
            base.ConfigureServices(services, builder);
            builder.RegisterInstance(BaseFixture.StaticRedisManagerMock.RedisManager.Object)
                .As<IRedisManagerAsync>()
                .SingleInstance();
        }
    }
}