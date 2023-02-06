using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using FluentAssertions;
using Moq;
using NLog;
using NLog.Extensions.Logging;
using Xunit;

namespace Yandex.Taximeter.Common.Tests.Logging
{
    public class AsyncScopeTests
    {
        [Fact]
        public void SimpleTest()
        {
            var logger = new NLogLoggerProvider(null).CreateLogger(GetType().Name);
            using (logger.BeginScope(new {db = "scope1"}))
            {
                GetScopeString().Should().Be("db=scope1");
                using (logger.BeginScope(new {driver = "scope2"}))
                {
                    GetScopeString().Should().Be("db=scope1\tdriver=scope2");
                    using (logger.BeginScope(new {db = "scope1"}))
                    {
                        GetScopeString().Should().Be("db=scope1\tdriver=scope2");
                    }
                }
                GetScopeString().Should().Be("db=scope1");
                
                using (logger.BeginScope(new { db = "scope2" }))
                {
                    GetScopeString().Should().Be("db=scope1,scope2");

                    using (logger.BeginScope(new {db = "scope1"}))
                    {
                        GetScopeString().Should().Be("db=scope1,scope2");
                    }
                }
                using (logger.BeginScope(new { db = "scope1" }))
                {
                    GetScopeString().Should().Be("db=scope1");
                }
            }
        }

        private string GetScopeString()
        {
            var scopeData = NLogLogger.AsyncScope.GetCurrentScope();
            var builder = new StringBuilder();
            foreach (var prop in scopeData)
            {
                if (builder.Length > 0)
                {
                    builder.Append("\t");
                }
                builder.Append(prop.Key);
                builder.Append('=');
                builder.Append(prop.Value);
            }
            return builder.ToString();
        }

        [Fact]
        public async Task TestWithTasks()
        {
            var logger = new NLogLoggerProvider(null).CreateLogger(GetType().Name);
            using (logger.BeginScope(new { db = "scope1" }))
            {
                await Task.Delay(10);
                GetScopeString().Should().Be("db=scope1");
                
                Func<Task> task1 = async () =>
                {
                    await Task.Delay(10);
                    using (logger.BeginScope(new {driver = "scope2"}))
                    {
                        GetScopeString().Should().Be("db=scope1\tdriver=scope2");
                    }
                };

                Func<Task> task2 = async () =>
                {
                    await Task.Delay(11);
                    using (logger.BeginScope(new { driver = "scope3" }))
                    {
                        GetScopeString().Should().Be("db=scope1\tdriver=scope3");
                    }
                };

                await Task.WhenAll(task1(), task2());

                GetScopeString().Should().Be("db=scope1");
            }
        }
    }
}