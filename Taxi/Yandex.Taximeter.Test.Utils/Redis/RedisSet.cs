using System;
using System.Collections.Generic;

namespace Yandex.Taximeter.Test.Utils.Redis
{
    internal class RedisSet : IRedisValue
    {
        public RedisSet()
        {
            Values = new HashSet<string>();
        }

        public HashSet<string> Values { get; }
        public DateTime? ExpireDate { get; private set; }
        public void Expire(TimeSpan timeout)
        {
            ExpireDate = DateTime.Now + timeout;
        }
    }
}