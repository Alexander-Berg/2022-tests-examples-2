using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.InteropServices;
using Yandex.Taximeter.Test.Utils.Redis;
using static System.String;

namespace Yandex.Taximeter.Common.Tests
{
    public class CommonFixture : IDisposable
    {
        public IServiceProvider ServiceProvider { get; private set; }

        /// <remarks>Этот RedisManager инъектируется во все static-классы один раз за прогон всех тестов</remarks>
        public RedisManagerMock StaticRedisManagerMock { get; private set; }

        public CommonFixture()
        {
            // For ReSharper XUnit test runner: set working dir explicitly (and wait JetBrains fix this bloody bug)
            if (RuntimeInformation.OSDescription.ToLower().Contains("windows") ||
                RuntimeInformation.OSDescription.ToLower().Contains("darwin"))
            {
                var location = typeof(CommonFixture).GetTypeInfo().Assembly.Location;
                var dir = Path.GetDirectoryName(location);
                var dirParts = dir.Split(Path.DirectorySeparatorChar);

                // Remove "bin\\Debug\\netcoreapp1.0" part from path
                var projectDir = Join(Path.DirectorySeparatorChar.ToString(), dirParts.Take(dirParts.Length - 3));
                Directory.SetCurrentDirectory(projectDir);
            }

            StaticRedisManagerMock = new RedisManagerMock().InjectIntoStatic();
        }

        public void Dispose()
        {
            ServiceProvider = null;
        }
    }
}