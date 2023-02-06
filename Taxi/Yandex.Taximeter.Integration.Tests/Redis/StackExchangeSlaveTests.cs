using System;
using System.Collections.Generic;
using System.Linq;
using FluentAssertions;
using JetBrains.Annotations;
using Microsoft.Extensions.DependencyInjection;
using Xunit;
using Yandex.Taximeter.Core.Redis;
using Yandex.Taximeter.Integration.Tests.Fixtures;

namespace Yandex.Taximeter.Integration.Tests.Redis
{
    public class StackExchangeSlaveTests : IClassFixture<FatFixture>
    {
        private readonly IRedisManagerAsync _redisManager;

        public StackExchangeSlaveTests(FatFixture fixture)
        {
            _redisManager = fixture.ServiceProvider.GetService<IRedisManagerAsync>();
        }

        [Fact]
        public async void HashScanAsync_ZeroCursor_ScansAllEntries()
        {
            //Arrange redis hash
            const string key = "HashScanAsync_ZeroCursor_ScansAllEntries";
            await _redisManager.TempCloud.Master.RemoveAsync(key);
            var items = Enumerable.Range(0, 1000).ToDictionary(x => x.ToString(), x => new TestHashItem {Number = x});
            await _redisManager.TempCloud.Master.SetRangeHashAsync(key, items);

            //Scan all items from redis hash
            string cursor = "0";
            var scannedItems = new Dictionary<string, TestHashItem>();
            do
            {
                Dictionary<string, TestHashItem> scannedPage;
                (scannedPage, cursor) =
                    await _redisManager.TempCloud.Slave.HashScanAsync<TestHashItem>(key, null, cursor, 12);
                foreach (var kvp in scannedPage)
                {
                    if (scannedItems.ContainsKey(kvp.Key))
                    {
                        throw new InvalidOperationException("Duplicate key read: " + kvp.Key);
                    }
                    scannedItems.Add(kvp.Key, kvp.Value);
                }
            } while (cursor != "0");

            //Assert
            scannedItems.Should().BeEquivalentTo(items);
        }

        [Fact]
        public async void HashScanAsync_ModifiableHash_ScansAllEntries()
        {
            //Arrange redis hash
            const string key = "HashScanAsync_ModifiableHash_ScansAllEntries";
            await _redisManager.TempCloud.Master.RemoveAsync(key);
            var items = Enumerable.Range(0, 1000).ToDictionary(x => x.ToString(), x => new TestHashItem {Number = x});
            await _redisManager.TempCloud.Master.SetRangeHashAsync(key, items);

            //Scan all items from redis hash
            string cursor = "0";
            do
            {
                Dictionary<string, TestHashItem> scannedPage;
                (scannedPage, cursor) =
                    await _redisManager.TempCloud.Master.HashScanAsync<TestHashItem>(key, null, cursor, 12);
                await _redisManager.TempCloud.Master.RemoveHashAsync(key, scannedPage.Select(x => x.Key));
            } while (cursor != "0");

            var recordsLeft = await _redisManager.TempCloud.Master.GetAllEntriesFromHashAsync(key);
            recordsLeft.Should().BeEmpty();
        }

        private struct TestHashItem
        {
            [UsedImplicitly]
            public int Number { get; set; }
        }
    }
}