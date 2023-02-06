using System.Linq;
using System.Xml.Linq;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Services.Driver.Import;

namespace Yandex.Taximeter.Common.Tests.Services.Driver.Import
{
    public class DriversBulkImportParserTests
    {
        [Fact]
        public void Cars_ContainsCarElements_ReturnsCarParsers()
        {
            var doc = XDocument.Parse(
                "<response><Cars>" +
                "<Car/><Car/><Car/>" +
                "</Cars></response>");
            var parser = new DriversBulkImportParser(doc);
            parser.Cars.Count().Should().Be(3);
        }

        [Theory]
        [InlineData("<response><Cars></Cars></response>")]
        [InlineData("<response></response>")]
        public void Cars_NullOrEmptyXml_ReturnsEmptyList(string xml)
        {
            var doc = XDocument.Parse(xml);
            var parser = new DriversBulkImportParser(doc);
            parser.Cars.Should().BeEmpty();
        }

        [Fact]
        public void Drivers_ContainsDriverElements_ReturnsDriverParsers()
        {
            var doc = XDocument.Parse(
                "<response><Drivers>" +
                "<Driver/><Driver/><Driver/>" +
                "</Drivers></response>");
            var parser = new DriversBulkImportParser(doc);
            parser.Drivers.Count().Should().Be(3);
        }

        [Theory]
        [InlineData("<response><Drivers></Drivers></response>")]
        [InlineData("<response></response>")]
        public void Drivers_NullOrEmptyXml_ReturnsEmptyList(string xml)
        {
            var doc = XDocument.Parse(xml);
            var parser = new DriversBulkImportParser(doc);
            parser.Drivers.Should().BeEmpty();
        }
    }
}