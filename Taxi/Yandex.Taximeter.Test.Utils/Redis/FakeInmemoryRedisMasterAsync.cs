using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Yandex.Taximeter.Core.Redis;

namespace Yandex.Taximeter.Test.Utils.Redis
{
    public class FakeInmemoryRedisMasterAsync : FakeInmemoryRedisSlaveAsync, IRedisMasterAsync
    {
        public FakeInmemoryRedisMasterAsync(IDictionary<string, IRedisValue> data) : base(data)
        {
        }

        public virtual Task<bool> RemoveItemFromSortedSetAsync(string setId, string value)
        {
            var set = GetData<RedisSortedSet>(setId);
            if (set == null)
            {
                return Task.FromResult(false);
            }
            return Task.FromResult(set.Values.Remove(value));
        }

        public virtual Task<long> RemoveItemsFromSortedSetAsync(string setId, IEnumerable<string> values)
        {
            var set = GetData<RedisSortedSet>(setId);
            var count = 0L;
            if (set == null)
            {
                return Task.FromResult(count);
            }
            foreach (var value in values)
            {
                if (set.Values.Remove(value))
                {
                    count++;
                }
            }
            return Task.FromResult(count);
        }

        public virtual Task<bool> AddItemToSortedSetAsync(string setId, string value, double score)
        {
            var set = GetData<RedisSortedSet>(setId);
            if (set == null)
            {
                set = new RedisSortedSet();
                Data[setId] = set;
            }
            set.Values[value] = score;
            return Task.FromResult(true);
        }

        public virtual Task<double> IncrementItemInSortedSetAsync(string setId, string value, double score)
        {
            throw new NotImplementedException();
        }

        public virtual Task<long> AppendToValueAsync(string db, string key, string value)
        {
            throw new NotImplementedException();
        }

        public virtual Task<long> AppendToValueAsync(string key, string value)
        {
            throw new NotImplementedException();
        }

        public virtual Task<bool> SetAsync<T>(string key, T value)
        {
            Data[key] = new SerializedRedisItem(value);
            return Task.FromResult(true);
        }

        public Task<bool> SetBlobAsync(string key, byte[] data)
            => SetAsync(key, data);

        public virtual Task<bool> SetAsync<T>(string key, T value, TimeSpan timeout)
        {
            Data[key] = new SerializedRedisItem(value, timeout);
            return Task.FromResult(true);
        }

        public virtual Task<bool> SetWithRetryAsync<T>(string db, string key, T value)
            => SetAsync(Key(db, key), value);

        public virtual Task<bool> SetWithRetryAsync<T>(string db, string key, T value, TimeSpan timeout)
            => SetAsync(Key(db, key), value, timeout);

        public virtual Task<bool> SetAsync<T>(string db, string key, T value)
            => SetAsync(Key(db, key), value);

        public virtual Task<bool> SetAsync<T>(string db, string key, T value, TimeSpan timeout)
            => SetAsync(Key(db, key), value, timeout);

        public Task<bool> SetIfNotExistAsync<T>(string key, T value)
        {
            if (Data.ContainsKey(key)) return Task.FromResult(false);
            Data[key] = new SerializedRedisItem(value);
            return Task.FromResult(true);
        }

        public Task<bool> SetIfNotExistAsync<T>(string key, T value, TimeSpan timeout)
        {
            if (Data.ContainsKey(key)) return Task.FromResult(false);
            Data[key] = new SerializedRedisItem(value, timeout);
            return Task.FromResult(true);
        }

        public Task<bool> SetIfNotExistAsync<T>(string db, string key, T value)
           => SetIfNotExistAsync(Key(db, key), value);

        public Task<bool> SetIfNotExistAsync<T>(string db, string key, T value, TimeSpan timeout)
            => SetIfNotExistAsync(Key(db, key), value, timeout);

        public Task<bool> SetToClientAsync(string key, int clientIndex, string value, TimeSpan ttl)
        {
            throw new NotImplementedException();
        }

        public virtual Task<bool> ExpireAsync(string key, DateTime expireAt)
            => ExpireAsync(key, expireAt - DateTime.Now);

        public virtual Task<bool> ExpireAsync(string db, string key, DateTime expireAt)
            => ExpireAsync(Key(db, key), expireAt);

        public virtual Task<bool> ExpireAsync(string db, string key, TimeSpan timeout)
            => ExpireAsync(Key(db, key), timeout);

        public virtual Task<bool> ExpireAsync(string key, TimeSpan timeout)
        {
            var data = GetData<IRedisValue>(key);
            if (data != null)
            {
                data.Expire(timeout);
                return Task.FromResult(true);
            }
            return Task.FromResult(false);
        }

        public virtual Task AddRangeToSetAsync(string db, string key, IList<string> values)
            => AddRangeToSetAsync(Key(db, key), values);

        public virtual Task AddRangeToSetAsync(string key, IList<string> values)
        {
            foreach (var value in values)
            {
                AddItemToSetAsync(key, value);
            }
            return Task.CompletedTask;
        }

        public virtual Task<bool> AddItemToSetAsync(string db, string key, string value)
            => AddItemToSetAsync(Key(db, key), value);

        public virtual Task<bool> AddItemToSetAsync(string key, string value)
        {
            var set = GetOrCreateData<RedisSet>(key);
            var result = set.Values.Add(value);
            return Task.FromResult(result);
        }

        public virtual Task<bool> RemoveItemFromSetAsync(string db, string key, string value)
            =>RemoveItemFromSetAsync(Key(db, key), value);

        public virtual Task<bool> RemoveItemFromSetAsync(string key, string value)
        {
            var set = GetData<RedisSet>(key);
            if (set != null)
            {
                var result = set.Values.Remove(value);
                if(!set.Values.Any())
                    Data.Remove(key);
                return Task.FromResult(result);
            }
            return Task.FromResult(false);
        }

        public Task<bool> MoveItemToSetAsync(string fromKey, string toKey, string value)
        {
            var fromSet = GetData<RedisSet>(fromKey);
            if (fromSet == null || !fromSet.Values.Remove(value))
            {
                return Task.FromResult(false);
            }
            var toSet = GetData<RedisSet>(toKey);
            if (toSet == null)
            {
                toSet = new RedisSet();
                Data[toKey] = toSet;
            }
            toSet.Values.Add(value);
            return Task.FromResult(true);
        }

        public Task RemoveRangeFromSetAsync(string key, IEnumerable<string> values)
        {
            foreach (var value in values)
                RemoveItemFromSetAsync(key, value);
            return Task.CompletedTask;
        }

        public Task RemoveRangeFromSetAsync(string db, string key, IEnumerable<string> values)
            => RemoveRangeFromSetAsync(Key(db, key), values);

        public virtual Task SetItemInListAsync(string db, string key, int index, string value)
            => SetItemInListAsync(Key(db, key), index, value);

        public virtual Task SetItemInListAsync(string key, int index, string value)
        {
            var list = GetData<RedisList>(key);
            if (list != null)
            {
                list.Values[index] = new SerializedRedisItem(value);
            }
            return Task.CompletedTask;
        }

        public virtual Task AddItemToListAsync<T>(string db, string key, T value)
            => AddItemToListAsync(Key(db, key), value);

        public virtual Task AddItemToListAsync<T>(string key, T value)
        {
            var list = GetOrCreateData<RedisList>(key);
            list.Values.Add(new SerializedRedisItem(value));
            return Task.CompletedTask;
        }

        public virtual Task AddItemToListAsync(string db, string key, string value)
            => AddItemToListAsync(Key(db, key), value);

        public virtual Task AddItemToListAsync(string key, string value)
            => AddItemToListAsync<string>(key, value);

        public virtual Task EnqueueItemOnListAsync<T>(string db, string key, T value)
            => EnqueueItemOnListAsync(Key(db, key), value);

        public virtual Task EnqueueItemOnListAsync<T>(string key, T value)
        {
            var list = GetOrCreateData<RedisList>(key);
            list.Values.Insert(0, new SerializedRedisItem(value));
            return Task.CompletedTask;
        }

        public virtual Task EnqueueItemOnListAsync(string db, string key, string value)
            => EnqueueItemOnListAsync<string>(Key(db, key), value);

        public virtual Task EnqueueItemOnListAsync(string key, string value)
            => EnqueueItemOnListAsync<string>(key, value);

        public virtual Task<string> RemoveStartFromListAsync(string db, string key)
            => RemoveStartFromListAsync(Key(db, key));

        public virtual Task<string> RemoveStartFromListAsync(string key)
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
                    return Task.FromResult(removedVal.ToString());
                }
            }
            return Task.FromResult(string.Empty);
        }

        public virtual Task<string> RemoveEndFromListAsync(string db, string key)
            => RemoveEndFromListAsync(Key(db, key));

        public virtual Task<string> RemoveEndFromListAsync(string key)
        {
            var list = GetData<RedisList>(key);
            if (list != null)
            {
                if (list.Values.Any())
                {
                    var idx = list.Values.Count - 1;
                    var removedVal = list.Values[idx];
                    list.Values.RemoveAt(idx);
                    if (!list.Values.Any())
                        Data.Remove(key);
                    return Task.FromResult(removedVal.ToString());
                }
            }
            return Task.FromResult(string.Empty);
        }

        public virtual Task<long> RemoveItemFromListAsync(string db, string key, string value)
            => RemoveItemFromListAsync(Key(db, key), value);

        public virtual Task<long> RemoveItemFromListAsync(string key, string value)
        {
            var list = GetData<RedisList>(key);
            if (list != null)
            {
                for(var i = 0; i < list.Values.Count; i++)
                    if (list.Values[i].Value.ToString().Equals(value))
                    {
                        list.Values.RemoveAt(i);
                        if (!list.Values.Any())
                            Data.Remove(key);
                        break;
                    }
                return Task.FromResult<long>(list.Values.Count);
            }
            return Task.FromResult(0L);
        }

        public Task<long> RemoveItemFromListAsync<T>(string db, string key, T value)
            => RemoveItemFromListAsync(Key(db, key), value);

        public Task<long> RemoveItemFromListAsync<T>(string key, T value)
        {
            var list = GetData<RedisList>(key);
            var removedCount = 0;
            if (list != null)
            {
                var idx = 0;
                var serializedValue = new SerializedRedisItem(value).ToString();
                while (idx < list.Values.Count)
                {
                    if (list.Values[idx].ToString().Equals(serializedValue, StringComparison.OrdinalIgnoreCase))
                    {
                        list.Values.RemoveAt(idx);
                        removedCount++;
                    }
                    else
                    {
                        idx++;
                    }
                }
            }
            return Task.FromResult((long) removedCount);
        }

        public virtual Task TrimListAsync(string db, string key, long start, long end)
            => TrimListAsync(Key(db, key), start, end);

        public virtual Task TrimListAsync(string key, long start, long end)
        {
            var list = GetData<RedisList>(key);
            if (list != null)
            {
                var newList = list.Values.Skip((int) start)
                    .Take((int)(end - start))
                    .ToList();
                if (newList.Any())
                    Data[key] = new RedisList(newList);
                else
                    Data.Remove(key);
            }
            return Task.CompletedTask;
        }

        public Task<string> MoveItemToListAsync(string db, string source, string destination)
            => MoveItemToListAsync(Key(db, source), Key(db, destination));

        public async Task<string> MoveItemToListAsync(string source, string destination)
        {
            var item = await RemoveEndFromListAsync(source);
            await EnqueueItemOnListAsync(destination, item);
            return item;
        }

        public Task<T> MoveItemToListAsync<T>(string db, string source, string destination)
            => MoveItemToListAsync<T>(Key(db, source), Key(db, destination));

        public async Task<T> MoveItemToListAsync<T>(string source, string destination)
        {
            var set = await GetAllItemsFromListAsync<T>(source);
            var lastItem = set.LastOrDefault();
            if (lastItem == null)
                return default(T);

            await RemoveItemFromListAsync(source, lastItem);
            await EnqueueItemOnListAsync(destination, lastItem);
            return lastItem;
        }

        public virtual Task RemoveAllAsync(IEnumerable<string> keys)
        {
            foreach (var key in keys)
                RemoveAsync(key);
            return Task.CompletedTask;
        }

        public virtual Task RemoveAllAsync_Server(IEnumerable<string> keys)
            => RemoveAllAsync_Server(keys);

        public virtual Task<bool> RemoveAsync(string db, string key)
            => RemoveAsync(Key(db, key));

        public virtual Task<bool> RemoveAsync(string key)
        {
            var contains = Data.ContainsKey(key);
            if (contains)
                Data.Remove(key);
            return Task.FromResult(contains);
        }

        public virtual Task SetHashPropertiesAsync<T>(string db, string hashId, T value)
        {
            throw new NotImplementedException();
        }

        public virtual Task SetHashPropertiesAsync<T>(string hashId, T value)
        {
            throw new NotImplementedException();
        }

        public virtual Task<T> GetSetHashAsync<T>(string db, string hashId, string key, T value)
        {
            return GetSetHashAsync(Key(db, hashId), key, value);
        }

        public virtual async Task<T> GetSetHashAsync<T>(string hashId, string key, T value)
        {
            var result = await GetHashAsync<T>(hashId, key);
            await SetHashAsync(hashId, key, value);
            return result;
        }

        public virtual Task<bool> SetHashAsync<T>(string db, string hashId, string key, T value)
            => SetHashAsync(Key(db, hashId), key, value);

        public virtual Task<bool> SetHashAsync<T>(string hashId, string key, T value)
        {
            var dict = GetOrCreateData<RedisHash>(hashId);
            var result = !dict.Values.ContainsKey(key);
            dict.Values[key] = new SerializedRedisItem(value);
            return Task.FromResult(result);
        }

        public virtual Task<bool> SetHashAsync(string db, string hashId, string key, string value)
            => SetHashAsync(Key(db, hashId), key, value);

        public virtual Task<bool> SetHashAsync(string hashId, string key, string value)
            => SetHashAsync<string>(hashId, key, value);


        public Task<bool> SetHashIfNotExistAsync<T>(string db, string hashId, string key, T value)
            => SetHashIfNotExistAsync(Key(db, hashId), key, value);


        public Task<bool> SetHashIfNotExistAsync<T>(string hashId, string key, T value)
        {
            var dict = GetOrCreateData<RedisHash>(hashId);
            var result = !dict.Values.ContainsKey(key);
            if (result)
            {
                dict.Values[key] = new SerializedRedisItem(value);
            }
            return Task.FromResult(result);
        }

        public Task<bool> SetHashIfNotExistAsync(string db, string hashId, string key, string value)
            => SetHashIfNotExistAsync(Key(db, hashId), key, value);


        public Task<bool> SetHashIfNotExistAsync(string hashId, string key, string value)
            => SetHashIfNotExistAsync<string>(hashId, key, value);

        public Task<bool> SetHashIfExistAsync<T>(string db, string hashId, string key, T value)
           => SetHashIfExistAsync(Key(db, hashId), key, value);


        public Task<bool> SetHashIfExistAsync<T>(string hashId, string key, T value)
        {
            var dict = GetOrCreateData<RedisHash>(hashId);
            var result = dict.Values.ContainsKey(key);
            if (result)
            {
                dict.Values[key] = new SerializedRedisItem(value);
            }
            return Task.FromResult(result);
        }

        public Task<bool> SetHashIfExistAsync(string db, string hashId, string key, string value)
            => SetHashIfExistAsync(Key(db, hashId), key, value);


        public Task<bool> SetHashIfExistAsync(string hashId, string key, string value)
            => SetHashIfExistAsync<string>(hashId, key, value);


        public Task<bool> SetHashBlobAsync(string hashId, string key, byte[] blobValue)
            => SetHashAsync(hashId, key, blobValue);

        public virtual Task SetRangeHashAsync<T>(string db, string hashId, IDictionary<string, T> values)
            => SetRangeHashAsync(Key(db, hashId), values);

        public virtual Task SetRangeHashAsync<T>(string hashId, IDictionary<string, T> values)
        {
            var dict = GetOrCreateData<RedisHash>(hashId);
            foreach (var pair in values)
            {
                dict.Values[pair.Key] = new SerializedRedisItem(pair.Value);
            }
            return Task.CompletedTask;
        }

        public Task ReplaceHashAsync<T>(string db, string hashId, IDictionary<string, T> values)
            => ReplaceHashAsync(Key(db, hashId), values);


        public Task ReplaceHashAsync<T>(string hashId, IDictionary<string, T> values)
        {
            var dict = new RedisHash();
            foreach (var pair in values)
            {
                dict.Values[pair.Key] = new SerializedRedisItem(pair.Value);
            }
            Data[hashId] = dict;
            return Task.CompletedTask;
        }

        public Task SetRangeHashBlobAsync(string hashId, IDictionary<string, byte[]> values)
            => SetRangeHashAsync(hashId, values);

        public Task ReplaceHashAsync<T>(string db, string hashId, IDictionary<string, T> values, TimeSpan? timeout = null)
        {
            throw new NotImplementedException();
        }

        public Task ReplaceHashAsync<T>(string hashId, IDictionary<string, T> values, TimeSpan? timeout = null)
        {
            throw new NotImplementedException();
        }

        public virtual Task<bool> RemoveHashAsync(string db, string hashId, string key)
            => RemoveHashAsync(Key(db, hashId), key);

        public virtual Task<bool> RemoveHashAsync(string hashId, string key)
        {
            var dict = GetData<RedisHash>(hashId);
            if (dict != null && key != null)
            {
                var contains = dict.Values.ContainsKey(key);
                if (contains)
                {
                    dict.Values.Remove(key);
                    if (!dict.Values.Any())
                    {
                        Data.Remove(hashId);
                    }
                    return Task.FromResult(true);
                }
            }
            return Task.FromResult(false);
        }

        public Task<bool> RemoveHashAsync(string db, string hashId, IEnumerable<string> keys)
            => RemoveHashAsync(Key(db, hashId), keys);

        public Task<bool> RemoveHashAsync(string hashId, IEnumerable<string> keys)
        {
            var result = false;
            foreach (var key in keys)
                result = result || RemoveHashAsync(hashId, key).Result;
            return Task.FromResult(result);
        }

        public virtual Task<long> IncrementValueInHashAsync(string db, string hashId, string key, int value)
            => IncrementValueInHashAsync(Key(db, hashId), key, value);

        public virtual Task<long> IncrementValueInHashAsync(string hashId, string key, int value)
            => DoIncrementValueInHashAsync(hashId, key, value,
                item => Convert.ToInt64(item.Value) + value);

        public virtual Task<double> IncrementValueInHashAsync(string db, string hashId, string key, double value)
            => IncrementValueInHashAsync(Key(db, hashId), key, value);

        public virtual Task<double> IncrementValueInHashAsync(string hashId, string key, double value)
            => DoIncrementValueInHashAsync(hashId, key, value,
                item => Convert.ToDouble(item.Value) + value);

        private Task<T> DoIncrementValueInHashAsync<T>(string hashId, string key, T value,
            Func<SerializedRedisItem, T> incrementFunc)
        {
            var dict = GetOrCreateData<RedisHash>(hashId);
            var newVal = dict.Values.ContainsKey(key)
                ? incrementFunc(dict.Values[key])
                : value;
            dict.Values[key] = new SerializedRedisItem(newVal);
            return Task.FromResult(newVal);
        }

        public virtual Task<long> IncrementAsync(string db, string key, uint amount)
            => IncrementAsync(Key(db, key), amount);

        public virtual Task<long> IncrementAsync(string key, uint amount)
            => IncrementAsync(key, (long)amount);

        public virtual Task<long> DecrementAsync(string db, string key, uint amount)
            => DecrementAsync(Key(db, key), amount);

        public virtual Task<long> DecrementAsync(string key, uint amount)
            => IncrementAsync(key, -amount);

        private Task<long> IncrementAsync(string key, long amount)
        {
            var item = GetData<SerializedRedisItem>(key);
            var newVal = item == null
                ? amount
                : Convert.ToInt64(item.Value) + amount;
            Data[key] = new SerializedRedisItem(newVal);
            return Task.FromResult(newVal);
        }

        public virtual Task<int> CheckedKeysAsync(bool remove)
        {
            throw new NotImplementedException();
        }

        public virtual Task<Dictionary<string, Dictionary<string, string>>> InfoAsync()
        {
            throw new NotImplementedException();
        }

        public Task SetCacheEntryAsync(string cacheKey, IDictionary<string, string> values, TimeSpan ttl)
        {
            throw new NotImplementedException();
        }

        public Task RemoveCacheEntriesAsync(params string[] cacheKeys)
        {
            throw new NotImplementedException();
        }


        public Task<bool> TryTakeCacheUpdateLockAsync(string cacheKey, TimeSpan ttl)
        {
            throw new NotImplementedException();
        }

        public virtual Task<TimeSpan?> GetTimeToLiveAsync(string db, string key)
        {
            throw new NotImplementedException();
        }

        public virtual Task<TimeSpan?> GetTimeToLiveAsync(string key)
        {
            throw new NotImplementedException();
        }

        public virtual Task<RedisEntryType> GetEntryTypeAsync(string key)
        {
            throw new NotImplementedException();
        }

        public virtual Task<bool> KeyRenameAsync(string key, string newkey)
        {
            throw new NotImplementedException();
        }

        public virtual Task SaveAsync()
        {
            throw new NotImplementedException();
        }

        public Task<bool> LockTakeAsync(string key, string lockId, TimeSpan lockTtl) => Task.FromResult(true);

        public Task<bool> LockRelaseAsync(string key, string lockId) => Task.FromResult(true);
        
        public Task<bool> ProlongLockAsync(string key, string lockId, TimeSpan prolongTime)
        {
            return Task.FromResult(true);
        }

        private T GetOrCreateData<T>(string hashId)
            where T : class, IRedisValue, new()
        {
            var dict = GetData<T>(hashId);
            if (dict == null)
            {
                dict = new T();
                Data[hashId] = dict;
            }
            return dict;
        }
    }
}