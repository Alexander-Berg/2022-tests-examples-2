using System;
using System.Collections.Generic;

namespace Yandex.Taximeter.Test.Utils.Redis
{
    internal class RedisHash : IRedisValue
    {
        public RedisHash()
        {
            Values = new Dictionary<string, SerializedRedisItem>();
        }

        public Dictionary<string, SerializedRedisItem> Values { get; }
        public DateTime? ExpireDate { get; private set; }
        public void Expire(TimeSpan timeout)
        {
            ExpireDate = DateTime.Now + timeout;
        }
    }
}