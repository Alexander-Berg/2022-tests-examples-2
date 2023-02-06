using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Yandex.Taximeter.Core.Redis.Services;

namespace Yandex.Taximeter.Test.Utils.Fakes
{
    public class FakeQueueService<T> : IQueueService<T>
        where T: class
    {
        private Queue<T> _queue = new Queue<T>();

        public string Name => GetType().Name;

        public Task<long> CountAsync()
        {
            return Task.FromResult<long>(_queue.Count);
        }

        public Task<T> GetNextAsync()
        {
            return Task.FromResult(_queue.Any() ? _queue.Dequeue() : null);
        }

        public Task AddAsync(T item)
        {
            _queue.Enqueue(item);
            return Task.CompletedTask;
        }
    }
}