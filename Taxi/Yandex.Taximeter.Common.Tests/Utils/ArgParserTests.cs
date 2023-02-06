using System;
using System.Collections.Generic;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Services.Sql;
using Yandex.Taximeter.Core.Utils;

namespace Yandex.Taximeter.Common.Tests.UtilsTests
{
    public class ArgParserTests
    {
        [Fact]
        public void TestArgParser_ParseSingleArgs()
        {
            string stringValue = null;
            int intValue = 0;
            double doubleValue = 0d;
            var dryRun = false;
            DateTime dateValue = DateTime.MinValue;
            SqlDatabase table = SqlDatabase.orders;
            var parser = new ArgParser();
            parser.Add("dry-run", s => dryRun = s);
            parser.Add("string", s => stringValue = s);
            parser.Add("int", s => intValue = s);
            parser.Add("double", (double s) => doubleValue = s);
            parser.Add("date", s => dateValue = s);
            parser.Add<SqlDatabase>("table", s => table = s);
            parser.Parse(new[] {"--dry-run", "--string", "hello", "--int", "11", "--double", "1.23", "--date", "2018-04-11", "--table", "transactions"});
            stringValue.Should().Be("hello");
            intValue.Should().Be(11);
            doubleValue.Should().Be(1.23);
            dryRun.Should().BeTrue();
            dateValue.Should().Be(new DateTime(2018, 04, 11));
            table.Should().Be(SqlDatabase.transactions);
        }
        
        [Fact]
        public void TestArgParser_ParseCollection_Add()
        {
            var strings = new List<string>();
            var parser = new ArgParser();
            parser.Add("string", s => strings.Add(s));
            parser.Parse(new[] { "--string", "hello", "--string", "world" });
            strings.Should().Equal("hello", "world");
        }
        
        [Fact]
        public void TestArgParser_ParseCollection_Assign()
        {
            var strings = new List<string>();
            var parser = new ArgParser();
            parser.Add("string", s => strings = s);
            parser.Parse(new[] { "--string", "hello", "world" });
            strings.Should().Equal("hello", "world");
        }
       
        [Fact]
        public void TestArgParser_ParseRemainder()
        {
            var strings = new List<string>();
            var parser = new ArgParser();
            parser.AddRemainder(s => strings = s);
            parser.Parse(new[] { "hello", "world" });
            strings.Should().Equal("hello", "world");
        }
        
        [Fact]
        public void TestArgParser_ParseAllTogether()
        {
            var strings = new List<string>();
            var remainder = new List<string>();
            int intValue = 0;
            var parser = new ArgParser();
            parser.Add("string", s => strings = s);
            parser.Add("int", s => intValue = s);
            parser.AddRemainder(s => remainder = s);
            parser.Parse(new[] { "--string", "hello", "world", "--int", "11", "some", "values" });
            intValue.Should().Be(11);
            strings.Should().Equal("hello", "world");
            remainder.Should().Equal("some", "values");
        }
    }
}