using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Yandex.Taximeter.Core.Redis;

namespace Yandex.Taximeter.Test.Utils.Redis
{
    public class FakeInmemoryRedisShardingAsync : FakeInmemoryRedisMasterAsync, IRedisShardingAsync
    {
        public FakeInmemoryRedisShardingAsync(IDictionary<string, IRedisValue> data) : base(data)
        {
        }

        public Task<string> RemoveStartFromListAsync(int clientIndex, string db, string key)
            => RemoveStartFromListAsync(db, key);

        public Task<string> RemoveStartFromListAsync(int clientIndex, string key)
            => RemoveStartFromListAsync(key);

        public Task<T> RemoveStartFromListAsync<T>(int clientIndex, string key)
        {
            var list = GetData<RedisList>(key);
            if (list != null)
            {
                if (list.Values.Any())
                {
                    var removedVal = list.Values[0];
                    list.Values.RemoveAt(0);
                    if (!list.Values.Any())
                        Data.Remove(key);
                    return Task.FromResult(removedVal.ConvertValue<T>());
                }
            }
            return Task.FromResult(default(T));
        }

        public Task<string> GetItemFromListAsync(int clientIndex, string key, int index)
        {
            throw new NotImplementedException();
        }

        public Task<T> GetItemFromListAsync<T>(int clientIndex, string key, int index)
        {
            throw new NotImplementedException();
        }

        public Task<List<string>> GetAllItemsFromListAsync(int poolIndex, string key)
            => GetAllItemsFromListAsync(key);

        public Task<string> MoveItemToListAsync(int poolIndex, string source, string destination)
        {
            throw new NotImplementedException();
        }

        public Task<T> MoveItemToListAsync<T>(int poolIndex, string source, string destination)
        {
            throw new NotImplementedException();
        }

        public Task<bool> KeyRenameAsync(int poolIndex, string key, string newkey)
        {
            throw new NotImplementedException();
        }

        public Task<bool> ExpireAsync(int poolIndex, string key, TimeSpan timeout)
        {
            throw new NotImplementedException();
        }
    }
}