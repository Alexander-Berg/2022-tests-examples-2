using System;
using System.Collections.Generic;

namespace Yandex.Taximeter.Test.Utils.Redis
{
    internal class RedisSortedSet : IRedisValue
    {
        public RedisSortedSet()
        {
            Values = new Dictionary<string, double>();
        }

        public IDictionary<string, double> Values { get; }
        public DateTime? ExpireDate { get; private set; }
        public void Expire(TimeSpan timeout)
        {
            ExpireDate = DateTime.Now + timeout;
        }

    }
}