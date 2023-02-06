using System;
using System.Threading.Tasks;
using Yandex.Taximeter.Core.Redis;

namespace Yandex.Taximeter.Test.Utils.Redis
{
    public class FakeRedisLockFactory : IRedisLockFactory
    {
        public virtual Task<TResult> ExecuteSynchronized<TResult>(Func<Task<TResult>> func,
            string lockKey,
            TimeSpan lockTtl,
            TimeSpan? lockTimeout = null,
            bool withLog = false)
            => func();

        public virtual Task ExecuteSynchronized(Func<Task> action,
            string lockKey,
            TimeSpan lockTtl,
            TimeSpan? lockTimeout = null,
            bool withLog = false)
            => action();

        public virtual async Task<bool> TryExecuteSynchronized(
            Func<Task> action, string lockKey, TimeSpan lockTtl,
            TimeSpan? lockTimeout = null, bool withLog = false)
        {
            await action();
            return true;
        }
        
        public virtual RedisLock CreateLock(string lockKey, string lockId = null, bool withLog = false)
        {
            throw new NotImplementedException();
        }

        public virtual RedisLock CreateLockWithMachineId(string lockKey, bool withLog = true)
        {
            throw new NotImplementedException();
        }
    }
}