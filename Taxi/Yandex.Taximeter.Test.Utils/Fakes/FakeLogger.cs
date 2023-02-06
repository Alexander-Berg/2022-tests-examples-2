using System;
using Microsoft.Extensions.Logging;

namespace Yandex.Taximeter.Test.Utils.Fakes
{
    /// <summary>
    /// Logger that does nothing
    /// </summary>
    public class FakeLogger : ILogger
    {
        public void Log<TState>(LogLevel logLevel, EventId eventId, TState state, Exception exception, Func<TState, Exception, string> formatter)
        {
        }

        public bool IsEnabled(LogLevel logLevel)
        {
            return true;
        }

        public IDisposable BeginScope<TState>(TState state)
        {
            return null;
        }
    }

    public class FakeLogger<T> :FakeLogger, ILogger<T>
    {}
}