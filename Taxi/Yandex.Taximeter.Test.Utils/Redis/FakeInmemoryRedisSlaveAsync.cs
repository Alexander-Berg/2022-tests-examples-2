using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Threading.Tasks;
using Newtonsoft.Json.Linq;
using Yandex.Taximeter.Core.Redis;

namespace Yandex.Taximeter.Test.Utils.Redis
{
    public class FakeInmemoryRedisSlaveAsync : IRedisSlaveAsync
    {
        protected readonly IDictionary<string, IRedisValue> Data;

        public FakeInmemoryRedisSlaveAsync(IDictionary<string, IRedisValue> data)
        {
            Data = data;
        }

        public RedisInsights<TItem> Insights<TItem>()
            => new RedisInsights<TItem>(
                new ReadOnlyDictionary<string, IRedisValue>(Data));

        public RedisInsights Insights()
            => new RedisInsights(new ReadOnlyDictionary<string, IRedisValue>(Data));

        public string GetClientInfo(string key) => "Fake In-memory client";

        public int GetClientIndex(string key) => 0;
        public int GetClientIndex<T>(T key) => 0;

        public virtual Task<bool> ContainsKeyAsync(string db, string key)
            => ContainsKeyAsync(Key(db, key));

        public virtual Task<bool> ContainsKeyAsync(string key)
        {
            var result = Data.ContainsKey(key);
            return Task.FromResult(result);
        }

        public virtual Task<IDictionary<string, double>> GetAllWithScoresFromSortedSetAsync(string setId)
        {
            var sortedSet = GetData<RedisSortedSet>(setId);
            if (sortedSet != null)
            {
                return Task.FromResult(sortedSet.Values);
            }
            return Task.FromResult<IDictionary<string, double>>(new Dictionary<string, double>());
        }

        public virtual Task<IDictionary<string, double>> GetRangeByRankFromSortedSetAsync(string setId, int fromRank, int toRank, bool ascending)
        {
            var set = GetAllWithScoresFromSortedSetAsync(setId).Result;
            if (fromRank < 0)
                fromRank = set.Count + fromRank;
            if (toRank < 0)
                toRank = set.Count + toRank;
            
            var range = (ascending ? set.OrderBy(x => x.Value) : set.OrderByDescending(x => x.Value)) 
                .Skip(fromRank).Take(toRank - fromRank)
                .ToDictionary(x => x.Key,x => x.Value);
            return Task.FromResult<IDictionary<string, double>>(range);
        }

        public Task<IDictionary<string, double>> GetRangeByScoreFromSortedSetAsync(string setId, double fromScore, double toScore, long limit)
        {
            var set = GetAllWithScoresFromSortedSetAsync(setId).Result;
            var result = set
                .Where(x => x.Value >= fromScore && x.Value <= toScore);
            if (limit >= 0)
            {
                result = result.OrderBy(x=>x.Value).Take((int) limit);
            }
            return Task.FromResult<IDictionary<string, double>>(result.ToDictionary(x => x.Key, x => x.Value));
        }

        public Task<IDictionary<string, double>> GetRevRangeByScoreFromSortedSetAsync(string setId, double fromScore, double toScore, long limit)
        {
            var set = GetAllWithScoresFromSortedSetAsync(setId).Result;
            var result = set
                .Where(x => x.Value >= fromScore && x.Value <= toScore);
            if (limit >= 0)
            {
                result = result.OrderByDescending(x => x.Value).Take((int)limit);
            }
            return Task.FromResult<IDictionary<string, double>>(result.ToDictionary(x => x.Key, x => x.Value));
        }

        public virtual Task<long> GetItemIndexInSortedSetDescAsync(string setId, string value)
        {
            var set = GetAllWithScoresFromSortedSetAsync(setId).Result;
            var index = set
                .OrderBy(x => x.Value)
                .Select(x => x.Key)
                .ToList()
                .IndexOf(value);
            return Task.FromResult<long>(index);
        }

        public virtual Task<long> GetSortedSetCountAsync(string setId)
        {
            var result = GetAllWithScoresFromSortedSetAsync(setId).Result.Count;
            return Task.FromResult<long>(result);
        }

        public virtual Task<double?> GetItemScoreInSortedSetAsync(string setId, string value)
        {
            var set = GetAllWithScoresFromSortedSetAsync(setId).Result;
            return Task.FromResult(set.ContainsKey(value) 
                ? (double?)set[value] 
                : null);
        }

        public virtual Task<long> GetStringCountAsync(string db, string key)
            => GetStringCountAsync(Key(db, key));

        public virtual Task<long> GetStringCountAsync(string key)
        {
            var serialized = GetValueAsync(key).Result;
            if (serialized != null)
            {
                return Task.FromResult<long>(serialized.Length);
            }
            return Task.FromResult(0L);
        }

        public virtual Task<IDictionary<string, T>> GetAllAsync<T>(IEnumerable<string> keys)
        {
            var result = new Dictionary<string, T>();
            foreach (var key in keys)
            {
                result[key] = GetAsync<T>(key).Result;
            }
            return Task.FromResult<IDictionary<string, T>>(result);
        }

        public virtual Task<T> GetAsync<T>(string key)
        {
            var serialized = GetData<SerializedRedisItem>(key);
            if (serialized != null)
            {
                var deserialized = serialized.ConvertValue<T>();
                return Task.FromResult(deserialized);
            }
            return Task.FromResult(default(T));
        }

        public virtual Task<T> GetAsync<T>(string db, string key)
            => GetAsync<T>(Key(db, key));

        public Task<byte[]> GetBlobAsync(string key)
            => GetAsync<byte[]>(key);

        public Task<string> GetFromClientAsync(string key, int clientIndex)
        {
            throw new NotImplementedException();
        }

        public virtual Task<IDictionary<string, string>> GetValueAllAsync(IEnumerable<string> keys)
            => GetAllAsync<string>(keys);

        public virtual Task<string> GetValueAsync(string db, string key)
            => GetValueAsync(Key(db, key));

        public virtual Task<string> GetValueAsync(string key)
            => GetAsync<string>(key);

        public virtual Task<bool> SetContainsItemAsync(string db, string key, string value)
            => SetContainsItemAsync(Key(db, key), value);

        public virtual Task<bool> SetContainsItemAsync(string key, string value)
        {
            var set = GetData<RedisSet>(key);
            return Task.FromResult(set != null && set.Values.Contains(value));
        }

        public virtual Task<HashSet<string>> GetAllItemsFromSetAsync(string db, string key)
            => GetAllItemsFromSetAsync(Key(db, key));

        public virtual Task<HashSet<string>> GetAllItemsFromSetAsync(string key)
        {
            var set = GetData<RedisSet>(key)?.Values ?? new HashSet<string>();
            return Task.FromResult(new HashSet<string>(set));
        }

        public virtual Task<long> GetSetCountAsync(string db, string key)
            => GetSetCountAsync(Key(db, key));

        public virtual Task<long> GetSetCountAsync(string key)
            => Task.FromResult<long>(GetAllItemsFromSetAsync(key).Result.Count);

        public virtual Task<string> GetItemFromListAsync(string db, string key, int listIndex)
            => GetItemFromListAsync(Key(db, key), listIndex);

        public virtual Task<string> GetItemFromListAsync(string key, int listIndex)
        {
            var set = GetAllItemsFromListAsync(key).Result;
            var element = set[listIndex];
            return Task.FromResult(element);
        }

        public Task<T> GetItemFromListAsync<T>(string db, string key, int listIndex)
            => GetItemFromListAsync<T>(Key(db, key), listIndex);

        public async Task<T> GetItemFromListAsync<T>(string key, int listIndex)
        {
            var set = await GetAllItemsFromListAsync<T>(key);
            return set[listIndex];
        }

        public virtual Task<List<T>> GetAllItemsFromListAsync<T>(string db, string key)
            => GetAllItemsFromListAsync<T>(Key(db, key));

        public virtual Task<List<T>> GetAllItemsFromListAsync<T>(string key)
        {
            var redisList = GetData<RedisList>(key);
            if (redisList == null)
            {
                return Task.FromResult(new List<T>());
            }
            var list = redisList.Values
                .Select(x => x.ConvertValue<T>())
                .ToList();
            return Task.FromResult(list);
        }

        public virtual Task<List<string>> GetAllItemsFromListAsync(string db, string key)
            => GetAllItemsFromListAsync(Key(db, key));

        public virtual Task<List<string>> GetAllItemsFromListAsync(string key)
            => GetAllItemsFromListAsync<string>(key);

        public virtual Task<List<string>> GetRangeFromListAsync(string db, string key, int start, int end)
            => GetRangeFromListAsync(Key(db, key), start, end);

        public virtual Task<List<string>> GetRangeFromListAsync(string key, int start, int end)
        {
            var list = GetAllItemsFromListAsync(key).Result;
            if (start < 0)
                start = list.Count - start;
            if (end < 0)
                end = list.Count - end;
            var range = list.Skip(start).Take(end - start).ToList();
            return Task.FromResult(range);
        }

        public virtual Task<long> GetListCountAsync(string db, string key)
            => GetListCountAsync(Key(db, key));

        public virtual Task<long> GetListCountAsync(string key)
        {
            var list = GetAllItemsFromListAsync(key).Result;
            return Task.FromResult<long>(list.Count);
        }

        public virtual Task<List<string>> GetHashKeysAsync(string db, string hashId)
            => GetHashKeysAsync(Key(db, hashId));

        public virtual Task<List<string>> GetHashKeysAsync(string hashId)
        {
            var redisHash = GetData<RedisHash>(hashId);
            var keys = redisHash == null ? new List<string>() : redisHash.Values.Keys.ToList();
            return Task.FromResult(keys);
        }

        public virtual Task<T> GetHashAsync<T>(string db, string hashId, string key)
            => GetHashAsync<T>(Key(db, hashId), key);

        public virtual Task<T> GetHashAsync<T>(string hashId, string key)
        {
            var redisHash = GetData<RedisHash>(hashId);
            if (redisHash != null && redisHash.Values.Any())
            {
                if (redisHash.Values.ContainsKey(key))
                    return Task.FromResult(redisHash.Values[key].ConvertValue<T>());
                return Task.FromResult(default(T));
            }
            return Task.FromResult(default(T));
        }

        public virtual Task<string> GetHashAsync(string db, string hashId, string key)
            => GetHashAsync(Key(db, hashId), key);

        public virtual Task<string> GetHashAsync(string hashId, string key)
            => GetHashAsync<string>(hashId, key);

        public async Task<byte[]> GetHashBlobAsync(string hashId, string key)
            => await GetHashAsync<byte[]>(hashId, key) ?? Array.Empty<byte>();

        public async Task<T> GetHashPropertiesAsync<T>(string db, string hashId)
        {
            return await GetHashPropertiesAsync<T>(Key(db, hashId));
        }

        public async Task<T> GetHashPropertiesAsync<T>(string hashId)
        {
            var jObject = await GetJsonFromHashAsync(hashId);
            return jObject == null ? default(T) : jObject.ToObject<T>();
        }

        public async Task<JObject> GetJsonFromHashAsync(string db, string hashId)
            => await GetJsonFromHashAsync(Key(db, hashId));

        public Task<JObject> GetJsonFromHashAsync(string hashId)
        {
            var redisHash = GetData<RedisHash>(hashId);
            if (redisHash != null && redisHash.Values.Any())
            {
                var jObj = new JObject();
                foreach (var entry in redisHash.Values)
                {
                    jObj[entry.Key] = entry.Value.ConvertValue<JToken>();
                }
                return Task.FromResult(jObj);
            }
            return Task.FromResult((JObject)null);
        }

        public async Task<JObject> GetJsonFromHashAsync(string db, string hashId, string[] keys)
            => await GetJsonFromHashAsync(Key(db, hashId), keys);


        public Task<JObject> GetJsonFromHashAsync(string hashId, string[] keys)
        {
            var redisHash = GetData<RedisHash>(hashId);
            var validKeys = new HashSet<string>(keys);
            if (redisHash != null && redisHash.Values.Any())
            {
                var jObj = new JObject();
                foreach (var entry in redisHash.Values)
                {
                    if (validKeys.Contains(entry.Key))
                    {
                        jObj[entry.Key] = entry.Value.ConvertValue<JToken>();
                    }
                }
                return Task.FromResult(jObj);
            }
            return Task.FromResult((JObject)null);
        }

        public virtual Task<Dictionary<string, T>> GetAllEntriesFromHashAsync<T>(string db, string hashId)
            => GetAllEntriesFromHashAsync<T>(Key(db, hashId));

        public virtual Task<Dictionary<string, T>> GetAllEntriesFromHashAsync<T>(string hashId)
        {
            var redisHash = GetData<RedisHash>(hashId);
            var dictionary = redisHash != null
                ? redisHash.Values
                    .ToDictionary(x => x.Key, x => x.Value.ConvertValue<T>())
                : new Dictionary<string, T>();
            return Task.FromResult(dictionary);
        }

        public virtual Task<Dictionary<string, string>> GetAllEntriesFromHashAsync(string db, string hashId)
            => GetAllEntriesFromHashAsync(Key(db, hashId));

        public virtual Task<Dictionary<string, string>> GetAllEntriesFromHashAsync(string hashId)
            => GetAllEntriesFromHashAsync<string>(hashId);

        public virtual Task<Dictionary<string, T>> GetValuesFromHashAsync<T>(string db, string hashId, string[] keys)
            => GetValuesFromHashAsync<T>(Key(db, hashId), keys);

        public virtual Task<Dictionary<string, T>> GetValuesFromHashAsync<T>(string hashId, string[] keys)
        {
            var dict = GetAllEntriesFromHashAsync<T>(hashId).Result;
            var result = keys.ToDictionary(x => x,
                x => dict.ContainsKey(x) ? dict[x] : default(T));
            return Task.FromResult(result);
        }

        public virtual Task<Dictionary<string, string>> GetValuesFromHashAsync(string db, string hashId, string[] keys)
            => GetValuesFromHashAsync(Key(db, hashId), keys);

        public virtual Task<Dictionary<string, string>> GetValuesFromHashAsync(string hashId, string[] keys)
            => GetValuesFromHashAsync<string>(hashId, keys);

        public Task<(Dictionary<string, T> Items, string Cursor)> HashScanAsync<T>(string hashId, string match, string cursor, int count)
        {
            throw new NotImplementedException();
        }

        public Task<IDictionary<string, string>> DebugInfo(string key)
        {
            throw new NotImplementedException();
        }

        public virtual Task<long> GetHashCountAsync(string db, string hashId)
            => GetHashCountAsync(Key(db, hashId));

        public virtual Task<long> GetHashCountAsync(string hashId)
        {
            var dict = GetAllEntriesFromHashAsync<object>(hashId).Result;
            return Task.FromResult<long>(dict.Count);
        }

        public virtual Task<bool> HashContainsAsync(string db, string hashId, string key)
            => HashContainsAsync(Key(db, hashId), key);

        public virtual Task<bool> HashContainsAsync(string hashId, string key)
        {
            var dict = GetAllEntriesFromHashAsync<object>(hashId).Result;
            return Task.FromResult(dict.ContainsKey(key));
        }

        public virtual Task<List<ItemKeys>> KeysAsync(string key, long limit)
        {
            throw new NotImplementedException();
        }

        public Task<CacheEntry> GetCacheEntryAsync(string cacheKey, params string[] properties)
        {
            throw new NotImplementedException();
        }

        public virtual Task<IEnumerable<string>> SearchAsync(string key, long limit)
        {
            throw new System.NotImplementedException();
        }

        protected string Key(string db, string hash) => db + ':' + hash;

        protected TRedisValue GetData<TRedisValue>(string key)
            where TRedisValue : class
        {
            if (Data.ContainsKey(key))
            {
                var value = Data[key];
                if (value == null)
                    return null;
                if (value is TRedisValue)
                    return (TRedisValue) value;
                throw new Exception("Key holds value of invalid type");
            }
            return null;
        }

        public virtual Task SearchAndProcessAsync(string key, long limit, Func<string, Task> keyCallback)
        {
            throw new NotImplementedException();
        }
        
        
        public Task ScriptEvaluateAsync(string key, RedisLuaScript script, params object[] args)
        {
            throw new NotImplementedException();
        }

        public Task<T> ScriptEvaluateScalarAsync<T>(string key, RedisLuaScript script, params object[] args)
        {
            throw new NotImplementedException();
        }

        public Task<T[]> ScriptEvaluateArrayAsync<T>(string key, RedisLuaScript script, params object[] args)
        {
            throw new NotImplementedException();
        }

        public Task<IDictionary<string, T>> ScriptEvaluateDictionaryAsync<T>(string key, RedisLuaScript script, params object[] args)
        {
            throw new NotImplementedException();
        }
    }
}