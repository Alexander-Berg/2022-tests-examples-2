using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using Xunit;
using Yandex.Taximeter.Core.Clients;
using Yandex.Taximeter.Core.Redis;
using Yandex.Taximeter.Core.Redis.Services.CRUD.Providers;
using Yandex.Taximeter.Core.Services.QualityControl.Pools;
using Yandex.Taximeter.Integration.Tests.Fixtures;

namespace Yandex.Taximeter.Integration.Tests.Playground
{
    /// <summary>
    /// Playground for experiments with MDS S3
    /// </summary>
    public class MdsS3ClientTests : IClassFixture<FatFixture>
    {
        private readonly IMdsQcClient _mdsS3Client;
        private readonly IMdsClient _mdsOldClient;
        private readonly IRedisManagerAsync _redisManager;
        private readonly ILogger _logger;
        
        public MdsS3ClientTests(FatFixture fixture)
        {
            _mdsS3Client = fixture.ServiceProvider.GetService<IMdsQcClient>();
            _mdsOldClient = fixture.ServiceProvider.GetService<IMdsClient>();
            _redisManager = fixture.ServiceProvider.GetService<IRedisManagerAsync>();
            _logger = fixture.ServiceProvider.GetService<ILogger<MdsS3ClientTests>>();
        }

        private async Task<string> GetHashDump(string hashKey)
        {
            var provider = RedisHashProvider<string>.CreateMasterSlave(_redisManager.DataCloud, hashKey);
            IEnumerable<KeyValuePair<string, string>> hashData = new Dictionary<string, string>();
            using (var iterator = provider.Scan(1000).GetEnumerator())
            {
                while (await iterator.MoveNext())
                    hashData = hashData.Union(iterator.Current);
            }

            return JsonConvert.SerializeObject(hashData);
        }
        
        [Fact]
        public async Task ReadStructure()
        {
            var results = await _mdsS3Client.Scan(null).ToList();

            var prefixes = results.SelectMany(x => x.Prefixes).ToList();
            var objects = results.SelectMany(x => x.Objects).ToList();

            foreach (var prefix in prefixes)
                _logger.LogInformation($"Prefix: {prefix}");

            foreach (var obj in objects)
                _logger.LogInformation($"Object: key={obj.Path}, size={obj.Size}");

            foreach (var prefix in prefixes)
            {
                _logger.LogInformation($"Scan prefix {prefix}");

                results = await _mdsS3Client.Scan(prefix).ToList();
                foreach (var innerPrefix in results.SelectMany(x => x.Prefixes))
                    _logger.LogInformation($"Inner prefix: {innerPrefix}");
                
                foreach (var obj in results.SelectMany(x => x.Objects))
                    _logger.LogInformation($"Inner object: key={obj.Path}, size={obj.Size}");
            }
            
            Assert.True(results.Count > 0);
        }

        [Fact]
        public async Task WriteJson()
        {
            var hashKey = (await _redisManager.DataCloud.Slave.SearchAsync($"DKK:{new string('?', 32)}:*:ITEMS"))
                .FirstOrDefault();

            Assert.NotNull(hashKey);

            var dumpValue = await GetHashDump(hashKey);
            var path = "dump/test.json";
            try
            {
                var uploadHeader = await _mdsS3Client.UploadString(path, dumpValue);
                var (downloadHeader, value) = await _mdsS3Client.DownloadString(path);
                
                Assert.Equal(dumpValue, value);
                Assert.Equal(JsonConvert.SerializeObject(uploadHeader),
                    JsonConvert.SerializeObject(downloadHeader));
                
                var results = await _mdsS3Client.Scan(null).ToList();
                Assert.True(results.SelectMany(x => x.Prefixes).Contains("dump/"));
            }
            finally
            {
                await _mdsS3Client.Delete(path);
            }
        }

        [Fact]
        public async Task WriteBinary()
        {
            var hashKey = (await _redisManager.DataCloud.Slave.SearchAsync($"DKK:{new string('?', 32)}:*:ITEMS"))
                .FirstOrDefault();
            Assert.NotNull(hashKey);

            var items = await _redisManager.DataCloud.Slave.GetAllEntriesFromHashAsync<DkkPoolItem>(hashKey);
            var photoKey = items.FirstOrDefault(x => x.Value?.OriginalFiles.IsNullOrEmpty() == false)
                .Value.OriginalFiles.Values.FirstOrDefault();
            
            Assert.False(string.IsNullOrEmpty(photoKey));

            var dumpData = await _mdsOldClient.GetAsync(photoKey);
            var path = "dump/test.jpg";
            try
            {
                var uploadHeader = await _mdsS3Client.UploadBytes(path, dumpData, "image/jpeg");
                var (downloadHeader, value, contentType) = await _mdsS3Client.DownloadBytes(path);

                Assert.True(dumpData.SequenceEqual(value));
                Assert.Equal("image/jpeg", contentType);
                Assert.Equal(JsonConvert.SerializeObject(uploadHeader),
                    JsonConvert.SerializeObject(downloadHeader));

                var results = await _mdsS3Client.Scan(null).ToList();
                Assert.True(results.SelectMany(x => x.Prefixes).Contains("dump/"));
            }
            finally
            {
                await _mdsS3Client.Delete(path);
            }
        }
    }
}
