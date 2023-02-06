using Microsoft.Extensions.Logging;

namespace Yandex.Taximeter.Test.Utils.Fakes
{
    /// <summary>
    /// Constructs fake loggers that do nothing
    /// </summary>
    public class FakeLoggerFactory : ILoggerFactory
    {
        public void Dispose()
        {
        }

        public virtual ILogger CreateLogger(string categoryName)
        {
            return new FakeLogger();
        }

        public void AddProvider(ILoggerProvider provider)
        {
        }

        public LogLevel MinimumLevel { get; set; }
    }
}