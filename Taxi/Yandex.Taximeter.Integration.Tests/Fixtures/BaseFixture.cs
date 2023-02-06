using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Text;
using Yandex.Taximeter.Test.Utils.Redis;
using static System.String;

namespace Yandex.Taximeter.Integration.Tests.Fixtures
{
    public class BaseFixture
    {
        /// <remarks>Этот RedisManager инъектируется во все static-классы один раз за прогон тестов</remarks>
        public static RedisManagerMock StaticRedisManagerMock { get; private set; }

        static BaseFixture()
        {
            StaticRedisManagerMock = new RedisManagerMock().InjectIntoStatic();
        }

        public BaseFixture()
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance); // For CRC32

            // For ReSharper XUnit test runner: set working dir explicitly (and wait JetBrains fix this bloody bug)
            if (RuntimeInformation.OSDescription.ToLower().Contains("windows") ||
                RuntimeInformation.OSDescription.ToLower().Contains("darwin"))
            {
                var location = typeof(BaseFixture).GetTypeInfo().Assembly.Location;
                var dir = Path.GetDirectoryName(location);
                var dirParts = dir.Split(Path.DirectorySeparatorChar);

                // Remove "bin\\Debug\\netcoreapp1.0" part from path
                var projectDir = Join(Path.DirectorySeparatorChar.ToString(), dirParts.Take(dirParts.Length - 3));
                Directory.SetCurrentDirectory(projectDir);
            }
        }
    }
}
