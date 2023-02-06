using System;
using System.IO;
using Autofac;
using Autofac.Extensions.DependencyInjection;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Yandex.Taximeter.Core;
using Yandex.Taximeter.Core.Clients;
using Yandex.Taximeter.Core.Configuration;
using Yandex.Taximeter.Core.Extensions;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Redis;
using Yandex.Taximeter.Core.Repositories;
using Yandex.Taximeter.Core.Services.NewQualityControl;
using Yandex.Taximeter.Core.Services.Subventions;

namespace Yandex.Taximeter.Integration.Tests.Fixtures
{
    public class FullFixture : BaseFixture, IDisposable
    {
        public TestServer ApiServer { get; }
        public TestServer AdminServer { get; }
        public IServiceProvider ServiceProvider { get; private set; }

        public FullFixture()
        {
            ApiServer = new TestServer(
                new WebHostBuilder()
                    .UseContentRoot(Directory.GetCurrentDirectory())
                    .UseStartup<TestApiStartup>());
            AdminServer = new TestServer(
                new WebHostBuilder()
                .UseContentRoot(Directory.GetCurrentDirectory())
                .UseStartup<TestAdminStartup>());

            var configuration = StartupHelper.BuildAppConfiguration(new ConfigurationBuilder());

            var services = new ServiceCollection();
            services.ConfigureTaximeter(configuration);

            services.AddOptions();
            services.AddMemoryCache();

            var builder = new ContainerBuilder();
            builder.RegisterType<LoggerFactory>().As<ILoggerFactory>().SingleInstance();
            builder.RegisterGeneric(typeof(Logger<>)).As(typeof(ILogger<>)).SingleInstance();
            builder.RegisterType<TaxiClient>().As<ITaxiClient>().SingleInstance();

            // Modules
            builder.RegisterModule(new SubventionsModule());
            builder.RegisterModule(new CommonModule());
            builder.RegisterModule(new RepositoryModule());
            builder.RegisterModule(new NewQualityControlModule());
            builder.RegisterInstance(StaticRedisManagerMock.RedisManager.Object)
                .As<IRedisManagerAsync>()
                .SingleInstance();
            builder.RegisterType<StackExchangeRedisManager>().SingleInstance();

            builder.Populate(services);

            var container = builder.Build();
            StaticHelper.InjectAll(container);

            ServiceProvider = container.Resolve<IServiceProvider>();

            var lf = ServiceProvider.GetService<ILoggerFactory>();
            lf.ConfigureNLog(configuration);
        }

        public void Dispose()
        {
            ApiServer?.Dispose();
            ServiceProvider = null;
        }
    }
}
