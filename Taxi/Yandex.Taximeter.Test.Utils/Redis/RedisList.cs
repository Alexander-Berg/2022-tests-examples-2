using System;
using System.Collections.Generic;

namespace Yandex.Taximeter.Test.Utils.Redis
{
    internal class RedisList : IRedisValue
    {
        public RedisList()
        {
            Values = new List<SerializedRedisItem>();
        }

        public RedisList(List<SerializedRedisItem> list)
        {
            Values = list;
        }

        public IList<SerializedRedisItem> Values { get; }
        public DateTime? ExpireDate { get; private set; }
        public void Expire(TimeSpan timeout)
        {
            ExpireDate = DateTime.Now + timeout;
        }
    }
}