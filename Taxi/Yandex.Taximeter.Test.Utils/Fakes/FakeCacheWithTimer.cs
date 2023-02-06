using System;
using System.Threading.Tasks;
using Moq;
using Yandex.Taximeter.Core.Utils;

namespace Yandex.Taximeter.Test.Utils.Fakes
{
    public class FakeCacheWithTimer<TData> : ICacheWithTimer<TData> where TData : class
    {
        public Func<Task<TData>> Factory { get; set; }

        public TData FakeData { get; set; }

        public async ValueTask<TData> GetAsync() => FakeData ?? (FakeData = await Factory());

        public void StartUpdateCycle()
        {
        }

        public static (ICacheFactory, FakeCacheWithTimer<TData>) BuildWithFactory()
        {
            var cache = new FakeCacheWithTimer<TData>();
            var cacheFactory = new Mock<ICacheFactory>(MockBehavior.Strict);
            cacheFactory
                .Setup(x => x.CreateCacheWithTimer(It.IsAny<Func<Task<TData>>>(), It.IsAny<TimeSpan>()))
                .Callback((Func<Task<TData>> factory, TimeSpan ts) =>
                {
                    cache.Factory = factory;
                })
                .Returns(cache);
            return (cacheFactory.Object, cache);
        }
    }

}