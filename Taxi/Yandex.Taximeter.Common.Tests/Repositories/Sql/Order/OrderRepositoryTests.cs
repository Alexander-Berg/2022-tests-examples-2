using System.Linq;
using FluentAssertions;
using Moq;
using Xunit;
using Yandex.Taximeter.Core.Models.Orders;
using Yandex.Taximeter.Core.Repositories.Redis;
using Yandex.Taximeter.Core.Repositories.Sql.Order;
using Yandex.Taximeter.Core.Services;
using Yandex.Taximeter.Core.Services.Settings;
using Yandex.Taximeter.Core.Services.Sql;
using Yandex.Taximeter.Test.Utils.Fakes;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Repositories.Sql.Order
{
    public class OrderRepositoryTests
    {
        private readonly FakeParkSqlTableMapService _parkSqlTableMapService = new FakeParkSqlTableMapService();
        private readonly FakeSqlConnectionFactory _sqlConnectionFactory = new FakeSqlConnectionFactory();
        private readonly OrderRepository _orderRepository;

        public OrderRepositoryTests()
        {
            _orderRepository = new OrderRepository(
                new FakeLogger<OrderRepository>(),
                Mock.Of<IOrderSqlQueueService>(),
                Mock.Of<IOrderSqlErrorRepository>(),
                _sqlConnectionFactory,
                _parkSqlTableMapService,
                Mock.Of<IGlobalSettingsService>());
        }

        [Fact]
        public async void ListFromMultipleParksAsync_SinglePark_QueriesFromSinglePark()
        {
            var db = TestUtils.NewId();
            var orderIds = new[]
            {
                new OrderId(db, TestUtils.NewId()), 
                new OrderId(db, TestUtils.NewId()), 
                new OrderId(db, TestUtils.NewId())
            };
            
            var sqlConnection = _sqlConnectionFactory.SetupConnection(SqlDatabase.orders, SqlReplica.Slave, 0);

            sqlConnection.SetupResult(
                OrderDictionary(orderIds[0]),
                OrderDictionary(orderIds[1]));

            //Act
            var results = await _orderRepository.ListFromMultipleParksAsync(
                orderIds,
                SqlReplica.Slave, 1, new[] {OrderSqlColumns.ID});

            //Assert
            results.Count.Should().Be(2, "DB returned only 2 out of 3 orders");
            results[orderIds[0]].Should().BeEquivalentTo(OrderDictionary(orderIds[0]));
            results[orderIds[1]].Should().BeEquivalentTo(OrderDictionary(orderIds[1]));
        }

        [Fact]
        public async void ListFromMultipleParksAsync_SinglePark_BuildsValidQuery()
        {
            var db = TestUtils.NewId();
            var orderIds = new[]
            {
                new OrderId(db, TestUtils.NewId()), 
                new OrderId(db, TestUtils.NewId()), 
                new OrderId(db, TestUtils.NewId())
            };
            SetTableMapping(db, "table1", 0);
            
            var sqlConnection = _sqlConnectionFactory.SetupConnection(SqlDatabase.orders, SqlReplica.Slave, 0);
            sqlConnection.SetupResult(
                OrderDictionary(orderIds[0]),
                OrderDictionary(orderIds[2]));
            
            //Act
            var results = await _orderRepository.ListFromMultipleParksAsync(
                orderIds,
                SqlReplica.Slave, 1, new[] {OrderSqlColumns.PARK_ID, OrderSqlColumns.ID});
            
            //Verify
            results.Count.Should().Be(2, "DB returned only 2 out of 3 orders");
            sqlConnection.Queries[0].Should()
                .Be("SELECT park_id,id FROM \"table1\" WHERE park_id=@park_id0 AND id=ANY(@id0)");
            sqlConnection.Parameters[0]["park_id0"].Should().Be(db);
            sqlConnection.Parameters[0]["id0"].As<string[]>().Should()
                .BeEquivalentTo(orderIds.Select(x => x.Order));
        }
        

        [Fact]
        public async void ListFromMultipleParksAsync_MultipleParks_BuildsValidQueries()
        {
            var orderIds = new[]
            {
                new OrderId(TestUtils.NewId(), TestUtils.NewId()),
                new OrderId(TestUtils.NewId(), TestUtils.NewId()),
                new OrderId(TestUtils.NewId(), TestUtils.NewId()),
            };
            SetTableMapping(orderIds[0].Db, "table1", 0);
            SetTableMapping(orderIds[1].Db, "table2", 0);
            SetTableMapping(orderIds[2].Db, "table3", 1);

            var sqlConnection1 = _sqlConnectionFactory.SetupConnection(SqlDatabase.orders, SqlReplica.Slave, 0);
            var sqlConnection2 = _sqlConnectionFactory.SetupConnection(SqlDatabase.orders, SqlReplica.Slave, 1);
            
            //Act
            await _orderRepository.ListFromMultipleParksAsync(orderIds, SqlReplica.Slave, 1,
                new[] {OrderSqlColumns.ID});
            
            //Verify
            sqlConnection1.Queries[0].Should().Be(
                "SELECT id,park_id FROM \"table1\" WHERE park_id=@park_id0 AND id=@id0" +
                " UNION ALL " +
                "SELECT id,park_id FROM \"table2\" WHERE park_id=@park_id1 AND id=@id1");

            sqlConnection1.Parameters[0]["park_id0"].Should().Be(orderIds[0].Db);
            sqlConnection1.Parameters[0]["id0"].Should().Be(orderIds[0].Order);
            sqlConnection1.Parameters[0]["park_id1"].Should().Be(orderIds[1].Db);
            sqlConnection1.Parameters[0]["id1"].Should().Be(orderIds[1].Order);
            
            
            sqlConnection2.Queries[0].Should().Be(
                "SELECT id,park_id FROM \"table3\" WHERE park_id=@park_id0 AND id=@id0");

            sqlConnection2.Parameters[0]["park_id0"].Should().Be(orderIds[2].Db);
            sqlConnection2.Parameters[0]["id0"].Should()
                .Be(orderIds[2].Order);
        }

        private void SetTableMapping(string db, string tableName, int shardNum)
        {
            _parkSqlTableMapService.Mapping[(db, SqlDatabase.orders)] =
                new SqlTableMappingEntry(tableName, shardNum);
        }

  
        private OrderDictionary OrderDictionary(OrderId orderId)
            => new OrderDictionary
            {
                {OrderSqlColumns.PARK_ID, orderId.Db},
                {OrderSqlColumns.ID, orderId.Order}
            };
    }
}
