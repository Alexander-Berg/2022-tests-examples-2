using System;
using System.Collections.Generic;
using System.Linq.Expressions;
using Moq;
using Yandex.Taximeter.Core.Redis;

namespace Yandex.Taximeter.Test.Utils.Redis
{
    public class RedisManagerMock
    {
        public Mock<IRedisManagerAsync> RedisManager { get; }
        public Mock<IRedisCloudAsync> DataCloud { get;private set; }
        public Mock<FakeInmemoryRedisMasterAsync> DataCloudMaster { get; private set; }
        public Mock<FakeInmemoryRedisSlaveAsync> DataCloudSlave { get; private set;}
        public Mock<FakeInmemoryRedisShardingAsync> DataCloudSharding { get; private set;}
        public Mock<IRedisCloudAsync> LogCloud { get;private set; }
        public Mock<FakeInmemoryRedisMasterAsync> LogCloudMaster { get;private set; }
        public Mock<FakeInmemoryRedisSlaveAsync> LogCloudSlave { get;private set; }
        public Mock<FakeInmemoryRedisShardingAsync> LogCloudSharding { get; private set;}
        public Mock<IRedisCloudAsync> TempCloud { get;private set; }
        public Mock<FakeInmemoryRedisMasterAsync> TempCloudMaster { get;private set; }
        public Mock<FakeInmemoryRedisSlaveAsync> TempCloudSlave { get;private set; }
        public Mock<FakeInmemoryRedisShardingAsync> TempCloudSharding { get;private set; }
        public Mock<FakeRedisLockFactory> Lock { get; private set; }

        public RedisManagerMock()
        {
            RedisManager = new Mock<IRedisManagerAsync>();

            CreateCloud<IRedisCloudAsync>(
                manager => manager.DataCloud,
                cloud => DataCloud = cloud,
                master => DataCloudMaster = master,
                slave => DataCloudSlave = slave,
                sharding => DataCloudSharding = sharding);
            CreateCloud<IRedisCloudAsync>(
                manager => manager.LogCloud,
                cloud => LogCloud = cloud,
                master => LogCloudMaster = master,
                slave => LogCloudSlave = slave,
                sharding => LogCloudSharding = sharding);
            CreateCloud<IRedisCloudAsync>(
                manager => manager.TempCloud,
                cloud => TempCloud = cloud,
                master => TempCloudMaster = master,
                slave => TempCloudSlave = slave,
                sharding => TempCloudSharding = sharding);

            Lock = new Mock<FakeRedisLockFactory> {CallBase = true};
            RedisManager.SetupGet(x => x.Lock).Returns(Lock.Object);
        }

        private void CreateCloud<TCloud>(
            Expression<Func<IRedisManagerAsync, IRedisCloudAsync>> getCloud,
            Action<Mock<TCloud>> setCloud,
            Action<Mock<FakeInmemoryRedisMasterAsync>> setMaster,
            Action<Mock<FakeInmemoryRedisSlaveAsync>> setSlave,
            Action<Mock<FakeInmemoryRedisShardingAsync>> setSharding)
            where TCloud : class, IRedisCloudAsync
        {
            var cloud = new Mock<TCloud>();
            var cloudData = new Dictionary<string, IRedisValue>();
            var cloudMaster = new Mock<FakeInmemoryRedisMasterAsync>(cloudData) {CallBase = true};
            var cloudSlave = new Mock<FakeInmemoryRedisSlaveAsync>(cloudData) {CallBase = true};
            var cloudSharding = new Mock<FakeInmemoryRedisShardingAsync>(cloudData) {CallBase = true};
            cloud.SetupGet(x => x.Master).Returns(cloudMaster.Object);
            cloud.SetupGet(x => x.Slave).Returns(cloudSlave.Object);
            cloud.SetupGet(x => x.Sharding).Returns(cloudSharding.Object);
            cloud.SetupGet(x => x.Clients.Count).Returns(1);
            RedisManager.SetupGet(getCloud).Returns(cloud.Object);
            setCloud(cloud);
            setMaster(cloudMaster);
            setSlave(cloudSlave);
            setSharding(cloudSharding);
        }

        /// <returns>Использовать с осторожностью, т.к. несколько вызовов метода может привести к гонкам при параллельном запуске тестов</returns>
        public RedisManagerMock InjectIntoStatic()
        {
            Core.Redis.RedisManager.Inject(RedisManager.Object);
            return this;
        }
    }
}