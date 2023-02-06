using System;
using Autofac;
using Autofac.Extensions.DependencyInjection;
using Microsoft.Extensions.Caching.Memory;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Moq;
using Yandex.Taximeter.Core.Clients;
using Yandex.Taximeter.Core.Clients.Personal;
using Yandex.Taximeter.Core.Configuration;
using Yandex.Taximeter.Core.Extensions;
using Yandex.Taximeter.Core.Graphite;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Redis;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Services.Communications;
using Yandex.Taximeter.Core.Services.ClientNotify;
using Yandex.Taximeter.Core.Services.NewQualityControl;
using Yandex.Taximeter.Core.Services.Settings;
using Yandex.Taximeter.Core.Services.Tvm;
using Yandex.Taximeter.Test.Utils.Fakes;

namespace Yandex.Taximeter.Integration.Tests.Fixtures
{
    public class FatFixture : BaseFixture, IDisposable
    {
        public IServiceProvider ServiceProvider { get; private set; }

        public FatFixture()
        {
            StaticHelper.ServiceName = "developers";
            var configuration = StartupHelper.BuildAppConfiguration(new ConfigurationBuilder());

            var services = new ServiceCollection();
            services.ConfigureTaximeter(configuration);

            services.AddOptions();

            var builder = new ContainerBuilder();

            builder.RegisterType<LoggerFactory>().As<ILoggerFactory>().SingleInstance();
            builder.RegisterGeneric(typeof(Logger<>)).As(typeof(ILogger<>)).SingleInstance();
            builder.RegisterType<MongoClientFactory>().As<IMongoClientFactory>().SingleInstance();
            builder.RegisterType<QcGateway>().As<IQcGateway>().SingleInstance();
            builder.RegisterType<QcPoolsGateway>().As<QcPoolsGateway>().SingleInstance();
            builder.RegisterType<TrackerGateway>().As<ITrackerGateway>().SingleInstance();
            builder.RegisterType<CommunicationsGateway>().As<ICommunicationsGateway>().SingleInstance();
            builder.RegisterType<ClientNotifyGateway>().As<IClientNotifyGateway>().SingleInstance();
            builder.RegisterType<GeotracksGateway>().As<IGeotracksGateway>().SingleInstance();
            builder.RegisterType<StackExchangeRedisManager>().As(typeof(IRedisManagerAsync)).SingleInstance();
            builder.RegisterType<TaxiClient>().As<ITaxiClient>().SingleInstance();
            builder.RegisterType<MdsQcClient>().As<IMdsQcClient>().SingleInstance();
            builder.RegisterType<MdsClient>().As<IMdsClient>().SingleInstance();
            builder.RegisterType<TvmService>().As<ITvmService>().SingleInstance();
            builder.RegisterType<PersonalDataEmailsGateway>().As<IPersonalDataEmailsGateway>().SingleInstance();
            builder.RegisterType<PersonalDataPhonesGateway>().As<IPersonalDataPhonesGateway>().SingleInstance();
            builder.RegisterType<PersonalDataLicensesGateway>().As<IPersonalDataLicensesGateway>().SingleInstance();
            builder.RegisterType<PersonalDataIdentificationsGateway>().As<IPersonalDataIdentificationsGateway>().SingleInstance();
            builder.RegisterType<ConfigApiGlobalSettingsRepository>().As<IGlobalSettingsRepository>().SingleInstance();
            builder.RegisterType<FakeGlobalSettingsService>().As<IGlobalSettingsService>().OnActivated(x =>
                {
                    x.Instance.GlobalSettings = x.Context.Resolve<IGlobalSettingsRepository>().GetAsync().Result;
                }).SingleInstance();
            
            // Some mocks here
            builder
                .RegisterInstance(Mock.Of<IMemoryCache>())
                .As<IMemoryCache>()
                .SingleInstance();
            builder
                .RegisterInstance(Mock.Of<ICityRepository>())
                .As<ICityRepository>()
                .SingleInstance();
            builder
                .RegisterInstance(Mock.Of<IParkRepository>())
                .As<IParkRepository>()
                .SingleInstance();
            builder
                .RegisterInstance(Mock.Of<IGraphiteService>())
                .As<IGraphiteService>()
                .SingleInstance();
            
            builder.Populate(services);

            var container = builder.Build();

            ServiceProvider = container.Resolve<IServiceProvider>();

            var lf = ServiceProvider.GetService<ILoggerFactory>();
            lf.ConfigureNLog(configuration);
        }

        public void Dispose()
        {
            ServiceProvider = null;
        }
    }
}
