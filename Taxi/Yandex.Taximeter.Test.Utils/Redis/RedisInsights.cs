using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;

namespace Yandex.Taximeter.Test.Utils.Redis
{
    public class RedisInsights
    {
        protected readonly IReadOnlyDictionary<string, IRedisValue> RedisData;

        public RedisInsights(ReadOnlyDictionary<string, IRedisValue> redisData)
        {
            RedisData = redisData;
        }

        public IEnumerable<KeyValuePair<string, HashSet<string>>> Sets()
            => RedisData
                .Where(x => x.Value is RedisSet)
                .Select(x => new KeyValuePair<string, HashSet<string>>(x.Key, ((RedisSet) x.Value).Values));
    }

    public class RedisInsights<TItem> : RedisInsights
    {
        public RedisInsights(ReadOnlyDictionary<string, IRedisValue> redisData)
            :base(redisData)
        {
        }

        public IEnumerable<KeyValuePair<string, IDictionary<string, TItem>>> Hashes()
            => RedisData
                .Where(x => x.Value is RedisHash)
                .Where(x => ((RedisHash) x.Value).Values.Values.FirstOrDefault().Value is TItem)
                .Select(x => new KeyValuePair<string, IDictionary<string, TItem>>(
                    x.Key, ToTypeSafeDictionary((RedisHash) x.Value)));

        public IDictionary<string, TItem> Values()
            => RedisData
                .Where(x => x.Value is SerializedRedisItem)
                .Where(x => ((SerializedRedisItem)x.Value).Value is TItem)
                .ToDictionary(x => x.Key, x => (TItem)((SerializedRedisItem)x.Value).Value);

        public IDictionary<string, TItem> FirstHash() => Hashes().First().Value;

        public IDictionary<string, TItem> Hash(string key)
        {
            var hash = RedisData[key] as RedisHash;
            if(hash == null)
                return new Dictionary<string, TItem>();
            return ToTypeSafeDictionary(hash);
        }

        private static IDictionary<string, TItem> ToTypeSafeDictionary(RedisHash redisHash)
            => redisHash.Values.ToDictionary(y => y.Key, y => y.Value.ConvertValue<TItem>());

        public IList<TItem> List(string key)
        {
            var list = RedisData[key] as RedisList;
            if (list == null)
                throw new InvalidOperationException();
            return ToTypeSafeList(list);
        }

        public bool HasList(string key)
        {
            if (!RedisData.ContainsKey(key))
                return false;
            var list = RedisData[key] as RedisList;
            return list != null;
        }

        private static IList<TItem> ToTypeSafeList(RedisList redisList)
            => redisList.Values
                .Select(x => x.ConvertValue<TItem>())
                .ToList();
    }
}