using System;
using System.Collections.Generic;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.Extensions.DependencyInjection;
using Xunit;
using Yandex.Taximeter.Core.Redis;
using Yandex.Taximeter.Core.Redis.Services;
using Yandex.Taximeter.Integration.Tests.Fixtures;

namespace Yandex.Taximeter.Integration.Tests.Redis
{
    public class RedisCacheTests:IClassFixture<FatFixture>
    {
        private readonly FatFixture _fixture;

        private readonly RedisCache _cache;

        private readonly IRedisCloudAsync _tempCloud;
        
        public RedisCacheTests(FatFixture fixture)
        {
            _fixture = fixture;
            var redisManager = _fixture.ServiceProvider.GetService<IRedisManagerAsync>();
            _tempCloud = redisManager.TempCloud;
            _cache= new RedisCache(_tempCloud, null, TimeSpan.FromMinutes(5), TimeSpan.FromMinutes(1));
        }

        private static string GenerateCacheKey() => $"Cache:TEST:{Guid.NewGuid():N}";
        
        [Fact]
        public async Task CacheSetValueTest()
        {
            var cacheKey = GenerateCacheKey();
            var values = new Dictionary<string, string>
            {
                ["Field1"] = "value1",
                ["Field2"] = "value2"
            };
            
            await _cache.SetCacheEntryAsync(cacheKey, values);
            var ttlValue = await _tempCloud.Master.GetAsync<DateTime>($"{{{cacheKey}}}:TTL");
            ttlValue.Should().BeAfter(DateTime.UtcNow);
            
            var hashValues = await _tempCloud.Master.GetAllEntriesFromHashAsync(cacheKey);
            hashValues.Should().BeEquivalentTo(values);
            
            var hardTtl = await _tempCloud.Master.GetTimeToLiveAsync(cacheKey);
            hardTtl.Should().NotBeNull();
            var hardTtl2 = await _tempCloud.Master.GetTimeToLiveAsync($"{{{cacheKey}}}:TTL");
            hardTtl2.Should().NotBeNull();
           
        }

        [Fact]
        public async Task CacheGetValueTest_AllFields()
        {
            var cacheKey = GenerateCacheKey();
            var values = new Dictionary<string, string>
            {
                ["Field1"] = "value1",
                ["Field2"] = "value2"
            };
            await _cache.SetCacheEntryAsync(cacheKey, values);
            var cachedValues = await _cache.GetCacheEntryAsync(cacheKey);
            cachedValues.Should().NotBeNull();
            cachedValues.Data.Should().BeEquivalentTo(values);
        }
        
        [Fact]
        public async Task CacheGetValueTest_Overwrite()
        {
            var cacheKey = GenerateCacheKey();
            var values = new Dictionary<string, string>
            {
                ["Field1"] = "value1",
                ["Field2"] = "value2"
            };
            await _cache.SetCacheEntryAsync(cacheKey, values);
            
            values.Remove("Field1");
            values["Field3"] = "value3";
            await _cache.SetCacheEntryAsync(cacheKey, values);
            
            var cachedValues = await _cache.GetCacheEntryAsync(cacheKey);
            cachedValues.Should().NotBeNull();
            cachedValues.Data.Should().BeEquivalentTo(values);
        }
        
        [Fact]
        public async Task CacheGetValueTest_Subset()
        {
            var cacheKey = GenerateCacheKey();

            var values = new Dictionary<string, string>
            {
                ["Field1"] = "value1",
                ["Field2"] = "value2",
                ["Field3"] = "value3"
            };
            await _cache.SetCacheEntryAsync(cacheKey, values);
            
            values.Remove("Field2");
            var cachedValues = await _cache.GetCacheEntryAsync(cacheKey, "Field1", "Field3");
            cachedValues.Data.Should().BeEquivalentTo(values);
        }
        
          
        [Fact]
        public async Task CacheGetValueTest_MissingField()
        {
            var cacheKey = GenerateCacheKey();

            var values = new Dictionary<string, string>
            {
                ["Field1"] = "value1",
                ["Field2"] = "value2",
                ["Field3"] = "value3"
            };
            await _cache.SetCacheEntryAsync(cacheKey, values);
            
            var cachedValues = await _cache.GetCacheEntryAsync(cacheKey, "Field1", "Field2", "Field3", "Field4");
            cachedValues.Data.Should().BeEquivalentTo(values);
        }
        
        [Fact]
        public async Task CacheGetOrCreateTest()
        {
            var cacheKey = GenerateCacheKey();

            IDictionary<string, string> values = new Dictionary<string, string>
            {
                ["Field1"] = "value1",
                ["Field2"] = "value2",
                ["Field3"] = "value3"
            };
            var cacheValues = await _cache.CacheGetOrCreateEnsureAsync(cacheKey, ()=> Task.FromResult(values));
            cacheValues.Should().BeEquivalentTo(values);
            
            cacheValues = await _cache.CacheGetOrCreateEnsureAsync(cacheKey, ()=>
            {
                throw new Exception("Factory should not be called here!");
            }, "Field1", "Field3");
            values.Remove("Field2");
            cacheValues.Should().BeEquivalentTo(values);
        }

    }
}