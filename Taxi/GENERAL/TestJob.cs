using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.Loader;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Yandex.Taximeter.Core.Graphite;
using Yandex.Taximeter.Core.Jobs;
using Yandex.Taximeter.Core.Redis;

namespace Yandex.Taximeter.JobRunner.Job
{
    public class TestJob : BaseJob
    {
        public TestJob(ILogger<TestJob> logger, IRedisManagerAsync redisManager, IGraphiteService graphiteService) : base("test", logger, redisManager, graphiteService)
        {

        }

        private static readonly string[] _switches = new[]
        {
            "System.GC.Concurrent",
            "System.GC.Server",
            "System.GC.RetainVM",
            "System.Globalization.Invariant"
        };
        
#pragma warning disable CS1998 // Async method lacks 'await' operators and will run synchronously
        public override async Task RunAsync(string[] args, TextWriter output, CancellationToken ct)
#pragma warning restore CS1998 // Async method lacks 'await' operators and will run synchronously
        {
            Logger.LogInformation($"{Name} job invoked with args: '{string.Join("', '", args)}'");
            output.WriteLine($"{Name} job invoked with args: '{string.Join("', '", args)}'");
            var sb = new StringBuilder();
            sb.AppendLine("---Runtime information---");
            sb.AppendLine($"TargetFrameworkName = '{AppContext.TargetFrameworkName}'");
            sb.AppendLine($"BaseDirectory = '{AppContext.BaseDirectory}'");
            sb.AppendLine($"IsServerGC = {System.Runtime.GCSettings.IsServerGC}");

            foreach (var sw in _switches)
            {
                sb.AppendLine(
                    AppContext.TryGetSwitch(sw, out var enabled) 
                        ? $"{sw} = {enabled}" : 
                        $"{sw} = (null)");
            }
            Logger.LogInformation(sb.ToString());
            output.WriteLine(sb.ToString());
        }
    }
}
