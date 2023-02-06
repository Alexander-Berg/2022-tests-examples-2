using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Yandex.Taximeter.Core.Services.MessageDispatching;

namespace Yandex.Taximeter.Test.Utils.Fakes
{
    public class FakeMessageDispatcher : IMessageDispatcher
    {
        private readonly List<object> _dispatchedMessages = new List<object>();

        public Task DispatchAsync<T>(T message)
        {
            _dispatchedMessages.Add(message);
            return Task.CompletedTask;
        }

        public IEnumerable<T> DispatchedMessages<T>()
            => _dispatchedMessages.OfType<T>();
    }
}