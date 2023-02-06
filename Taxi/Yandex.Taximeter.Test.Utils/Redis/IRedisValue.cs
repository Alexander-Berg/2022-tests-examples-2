using System;

namespace Yandex.Taximeter.Test.Utils.Redis
{
    public interface IRedisValue
    {
        DateTime? ExpireDate { get; }

        void Expire(TimeSpan timeout);
    }
}