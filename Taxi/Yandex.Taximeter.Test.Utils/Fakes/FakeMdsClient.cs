using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Yandex.Taximeter.Core.Clients;

namespace Yandex.Taximeter.Test.Utils.Fakes
{
    public class FakeMdsClient : IMdsClient
    {
        public IDictionary<string, byte[]> SavedFiles { get; } 
            = new Dictionary<string, byte[]>();
        public IList<string> SavedIds { get; } = new List<string>();

        public Task<string> UploadAsync(string id, byte[] data, TimeSpan? ttl)
        {
            if (ttl.HasValue)
                throw new NotImplementedException();
            
            return DoUpload(data);
        }

        public Task<byte[]> GetAsync(string key)
        {
            if (!SavedFiles.ContainsKey(key))
                return Task.FromResult<byte[]>(null);
            return Task.FromResult(SavedFiles[key]);
        }

        public Task DeleteAsync(string key)
        {
            SavedFiles.Remove(key);
            SavedIds.Remove(key);
            return Task.CompletedTask;
        }

        private Task<string> DoUpload(byte[] data)
        {
            var fileId = Guid.NewGuid().ToString();
            SavedFiles[fileId] = data;
            SavedIds.Add(fileId);
            return Task.FromResult(fileId);
        }

        public Uri GetUrl(string key)
        {
            return new Uri($"fakemds://{key}");
        }
    }
}
