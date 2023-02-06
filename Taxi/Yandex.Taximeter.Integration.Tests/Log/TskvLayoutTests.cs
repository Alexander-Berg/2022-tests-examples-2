using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using NLog;
using NLog.Config;
using NLog.Extensions.Logging;
using NLog.Targets;
using Xunit;
using Yandex.Taximeter.Core.Log;
using Yandex.Taximeter.Core.Services.Version;
using ILogger = Microsoft.Extensions.Logging.ILogger;
using LogLevel = NLog.LogLevel;

namespace Yandex.Taximeter.Integration.Tests.Log
{
    public class TskvLayoutTests
    {
        private readonly MemoryTarget _logTarget;
        private readonly ILogger _logger;

        public TskvLayoutTests()
        {
            const string targetName ="test-target";
            var config = new LoggingConfiguration();
            _logTarget = new MemoryTarget();
            config.AddTarget(targetName, _logTarget);
            _logTarget.Layout = new TskvLayout();
            config.LoggingRules.Add(new LoggingRule("*", LogLevel.Debug, _logTarget));
            LogManager.Configuration = config;
            _logger = new NLogLoggerProvider(null).CreateLogger(targetName);
        }

        [Fact]
        public void GetFormattedMessage_EmptyScope_BuildsValidLogString()
        {
            _logger.LogInformation("msg1");

            var pattern =
                "tskv\ttimestamp=\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}.\\d{4}\tlog_module=test-target\tlog_level=INFO\tlog_message=msg1";
            var logRecord = _logTarget.Logs.Single();
            
            Regex.IsMatch(logRecord, pattern).Should().BeTrue();
        }

        [Fact]
        public void GetFormattedMessage_FullScope_BuildsValidLogString()
        {
            using(_logger.BeginScope(new
            {
                action_result_time = 0.025,
                controller_action_time=7.4668,
                request_id="0HL7GG835KODH",
                request_method = "GET",
                request_path = "/driver/polling/order?md5_requestcar=&md5_setcar=98203985d2bb408dafc02addbcfac142_3055378975999999999&md5_cancelrequest=87ade3aa4e0b4748bfb344948d2c54a9&proxy_block_id=default&device_id=346058060384649&session=663ec37a6fbc4fc0a75c5d35b2b95542&db=b8252ce37d8a49dabe7623c327644184",
                taximeter_version= new TaximeterVersion(8, 36, 290),
                timing_sequence="driver_authentication_time,set_language_and_cookie_time"
            }))
                _logger.LogInformation("TIMINGS");

            var startPattern = "^tskv\ttimestamp=\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}.\\d{4}";
            var endMsg = "\tlog_module=test-target" +
                         "\tlog_level=INFO" +
                         "\tmeta_action_result_time=0.025" +
                         "\tmeta_controller_action_time=7.4668" +
                         "\tmeta_request_id=0HL7GG835KODH" +
                         "\tmeta_request_method=GET" +
                         "\tmeta_request_path=/driver/polling/order?md5_requestcar=&md5_setcar=98203985d2bb408dafc02addbcfac142_3055378975999999999&md5_cancelrequest=87ade3aa4e0b4748bfb344948d2c54a9&proxy_block_id=default&device_id=346058060384649&session=663ec37a6fbc4fc0a75c5d35b2b95542&db=b8252ce37d8a49dabe7623c327644184" +
                         "\tmeta_taximeter_version=8.36 (290)" +
                         "\tmeta_timing_sequence=driver_authentication_time,set_language_and_cookie_time" +
                         "\tlog_message=TIMINGS";
            var logRecord = _logTarget.Logs.Single();

            Regex.IsMatch(logRecord, startPattern).Should().BeTrue();
            logRecord.Should().EndWith(endMsg);
        }

        [Fact]
        public void GetFormattedMessage_FieldsWithSpecialCharacters_BuildsValidLogString()
        {
            using (_logger.BeginScope(new Dictionary<string, string>
            {
                {"field=1\n1", "value\r\nwith=escaped\x11\x08"}
            }))
                _logger.LogInformation("msg");

            var endMsg = "\tmeta_field\\=1\\n1=value\\r\\nwith=escaped\\x11\\x08" +
                         "\tlog_message=msg";
            var logRecord = _logTarget.Logs.Single();

            logRecord.Should().EndWith(endMsg);
        }
    }
}