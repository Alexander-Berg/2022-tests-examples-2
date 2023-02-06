using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Yandex.Taximeter.Core;

namespace Yandex.Taximeter.ScriptRunner.Scripts
{
    public class TestScript: CustomScriptBase
    {
        public TestScript(ILoggerFactory loggerFactory): base("test_script", loggerFactory)
        {
        }

#pragma warning disable 1998
        public override async Task RunAsync(string[] args, TextWriter output, CancellationToken ct)
#pragma warning restore 1998
        {
            Logger.LogInformation($"{Name} script invoked with args: '{string.Join("', '", args)}'");
            output.WriteLine($"{Name} script invoked with args: '{string.Join("', '", args)}'");
        }
    }
}
