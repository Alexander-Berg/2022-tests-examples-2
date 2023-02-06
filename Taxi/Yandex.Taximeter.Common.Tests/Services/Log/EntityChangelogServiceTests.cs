using System;
using Moq;
using Xunit;
using Yandex.Taximeter.Core.Clients.Personal;
using Yandex.Taximeter.Core.Repositories.Sql;
using Yandex.Taximeter.Core.Repositories.Sql.Entities;
using Yandex.Taximeter.Core.Services.Driver;
using Yandex.Taximeter.Core.Services.Log;
using Yandex.Taximeter.Test.Utils.Fakes;

namespace Yandex.Taximeter.Common.Tests.Services.Log
{
    public sealed class EntityChangelogServiceTests
    {
        private Mock<IEntityChangelogRepository> _mock;
        private EntityChangelogService _entityChangelogService;

        public EntityChangelogServiceTests()
        {
            _mock = new Mock<IEntityChangelogRepository>();
            _entityChangelogService = new EntityChangelogService(_mock.Object, Mock.Of<IPersonalDataGateways>(), new FakeLoggerFactory());
        }

        [Fact]
        public async void CommitTransactionAsync_TestNullPointers()
        {
            Object arg1 = null; // Need to make parameters typed to avoid ambiguocity
            await _entityChangelogService.CommitTransactionAsync("FakeID", arg1, null, "FakeParkID");
            _mock.Verify(rc => rc.AddAsync(It.IsAny<string>(), It.IsAny<EntityChangelog>()), Times.Never());
        }

        [Fact]
        public async void CommitTransactionAsync_TestEqual()
        {
            var arg1 = new MyStruct("val1", "Val2");
            var arg2 = new MyStruct("val1", "Val2");
            await _entityChangelogService.CommitTransactionAsync("FakeID", arg1, arg2, "FakeParkID");
            _mock.Verify(rc => rc.AddAsync(It.IsAny<string>(), It.IsAny<EntityChangelog>()), Times.Never());
        }

        [Fact]
        public async void CommitTransactionAsync_TestNotEqual1()
        {
            var arg1 = new MyStruct("val1", "Val2");
            var arg2 = new MyStruct("val1", "Val4");
            await _entityChangelogService.CommitTransactionAsync("FakeID", arg1, arg2, "FakeParkID");
            _mock.Verify(rc => rc.AddAsync(It.IsAny<string>(), It.Is<EntityChangelog>(val => val.counts == 1)), Times.Once());
        }

        [Fact]
        public async void CommitTransactionAsync_TestNotEqual2()
        {
            var arg1 = new MyStruct("val1", "Val2");
            var arg2 = new MyStruct("val3", "Val4");
            await _entityChangelogService.CommitTransactionAsync("FakeID", arg1, arg2, "FakeParkID");
            _mock.Verify(rc => rc.AddAsync(It.IsAny<string>(), It.Is<EntityChangelog>(val => val.counts == 2)), Times.Once());
        }

        #region Embedded types
        public class MyStruct
        {
            public MyStruct(string v1, string v2)
            {
                Value1 = v1;
                Value2 = v2;
            }

            public string Value1 { get; set; }
            public string Value2 { get; set; }
        }

        #endregion Embedded types
    }
}
