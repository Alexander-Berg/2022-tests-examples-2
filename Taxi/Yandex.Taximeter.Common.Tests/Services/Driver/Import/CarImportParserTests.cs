using System.Collections.Generic;
using System.Linq;
using System.Xml.Linq;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Exceptions;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Car;
using Yandex.Taximeter.Core.Repositories.MongoDB.Dtos.Car;
using Yandex.Taximeter.Core.Services.Driver.Import;

namespace Yandex.Taximeter.Common.Tests.Services.Driver.Import
{
    public class CarImportParserTests : IClassFixture<CommonFixture>
    {
        [Fact]
        public void Parse_ValidInput()
        {
            var xml = XDocument.Load(@"Services/Driver/Import/ValidCar.xml");
            var parser = new CarImportParser(xml.Root);

            //Assert
            parser.ParseUuid().Should().Be("a164df5cf63449ddad0b72026385d73e");
            parser.ParseDb().Should().Be("27b40f222a4945758eafca9b402a7e21");
            parser.ParseDateLastUpdate().Should().Be("17.04.2015T11:37:44");

            var parsedCar = parser.Parse(false);
            parsedCar.Category.Should().Be(new CarCategory
            {
                Econom = true
            });
            parsedCar.Permit().Should().Be("MCK 052850");
            parsedCar.Brand.Should().Be("RENAULT");
            parsedCar.Model.Should().Be("LOGAN");
            parsedCar.Year.Should().Be(2014);
            parsedCar.Color.Should().Be("Желтый");
            parsedCar.Number.Should().Be("МЕ70977");
            parsedCar.Callsign.Should().Be("939");

            parsedCar.Service.Should().Be(new CarService
            {
                Conditioner = true,
                Smoking = true,
                Animals = true,
                PrintBill = true
            });

            parsedCar.Chairs.Count.Should().Be(2);
            parsedCar.Chairs[0].Brand.Should().Be("Yandex");
            parsedCar.Chairs[0].Isofix.Should().BeTrue();
            parsedCar.Chairs[0].Categories.Should().BeEquivalentTo(new List<int> {1, 2, 3});

            parsedCar.Chairs[1].Brand.Should().Be("Yandex");
            parsedCar.Chairs[1].Categories.Should().BeEquivalentTo(new List<int> {0});
        }

        [Theory]
        [InlineData("Сиреневый")]
        [InlineData("бело-желто-красный")]
        public void Parse_InvalidColor(string invalidColor)
        {
            var xml = XDocument.Load(@"Services/Driver/Import/ValidCar.xml");
            // ReSharper disable PossibleNullReferenceException
            Assert.NotNull(xml.Element("Car"));
            Assert.NotNull(xml.Element("Car").Element("Color"));
            xml.Element("Car").Element("Color").Value = invalidColor;
            // ReSharper enable PossibleNullReferenceException
            Assert.Throws<ParsingException>(() =>
            {
                var parser = new CarImportParser(xml.Root);
                parser.Parse(false);
            });
        }

        // TODO: Remove after strict validation of case will be added
        // Currently we need save registry fix to not break driver imports too much
        public static IEnumerable<object[]> ValidLowerCaseColors()
        {
            return CarSelector.AllColors.Keys
                .Select(x => x.ToLower())
                .Select(x => new object[] {x});
        }

        [Theory]
        [MemberData(nameof(ValidLowerCaseColors))]
        public void Parse_LowerCaseColor(string lowercaseColor)
        {
            var xml = XDocument.Load(@"Services/Driver/Import/ValidCar.xml");
            // ReSharper disable PossibleNullReferenceException
            Assert.NotNull(xml.Element("Car"));
            Assert.NotNull(xml.Element("Car").Element("Color"));
            xml.Element("Car").Element("Color").Value = lowercaseColor;
            // ReSharper enable PossibleNullReferenceException
            var parser = new CarImportParser(xml.Root);
            parser.Parse(false);
        }
    }
}