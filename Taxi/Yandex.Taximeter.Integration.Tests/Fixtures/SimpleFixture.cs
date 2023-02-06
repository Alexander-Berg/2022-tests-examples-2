using System;
using Autofac;
using Autofac.Extensions.DependencyInjection;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Yandex.Taximeter.Core.Configuration;
using Yandex.Taximeter.Core.Repositories.MongoDB;

namespace Yandex.Taximeter.Integration.Tests.Fixtures
{
    public class SimpleFixture : BaseFixture, IDisposable
    {
        public IServiceProvider ServiceProvider { get; private set; }

        public SimpleFixture()
        {
            var configuration = StartupHelper.BuildAppConfiguration(new ConfigurationBuilder());

            var services = new ServiceCollection();
            services.ConfigureTaximeter(configuration);

            services.AddOptions();

            var builder = new ContainerBuilder();
            builder.RegisterType<MongoClientFactory>().As<IMongoClientFactory>().SingleInstance();

            builder.Populate(services);

            var container = builder.Build();

            ServiceProvider = container.Resolve<IServiceProvider>();
        }

        public void Dispose()
        {
            ServiceProvider = null;
        }
    }
}
