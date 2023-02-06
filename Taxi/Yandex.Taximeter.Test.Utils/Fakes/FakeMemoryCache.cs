using System;
using System.Collections.Generic;
using Microsoft.Extensions.Caching.Memory;
using Microsoft.Extensions.Primitives;

namespace Yandex.Taximeter.Test.Utils.Fakes
{
    public class FakeMemoryCache : IMemoryCache
    {
        private readonly Dictionary<object, ICacheEntry> _values = new Dictionary<object, ICacheEntry>();

        public bool TryGetValue(object key, out object value)
        {
            ICacheEntry entry;
            var result = _values.TryGetValue(key, out entry);
            value = entry?.Value;
            return result;
        }

        public ICacheEntry CreateEntry(object key)
        {
            return new FakeCacheEntry(this) {Key = key};
        }

        public void Remove(object key)
        {
            _values.Remove(key);
        }

        public void ClearAll() => _values.Clear();

        public void Dispose()
        {
        }
        
        private class FakeCacheEntry : ICacheEntry
        {
            private readonly FakeMemoryCache _memoryCache;

            public FakeCacheEntry(FakeMemoryCache cache)
            {
                _memoryCache = cache;
            }

            public object Key { get; set; }
            public object Value { get; set; }
            public DateTimeOffset? AbsoluteExpiration { get; set; }
            public TimeSpan? AbsoluteExpirationRelativeToNow { get; set; }
            public TimeSpan? SlidingExpiration { get; set; }
            public IList<IChangeToken> ExpirationTokens { get; }
            public IList<PostEvictionCallbackRegistration> PostEvictionCallbacks { get; }
            public CacheItemPriority Priority { get; set; }
            public long? Size { get; set; }

            public void Dispose()
            {
                if (Value != null && Key != null)
                {
                    _memoryCache._values[Key] = this;
                }
            }
        }
    }
}