using System;
using System.Xml.Linq;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Driver;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Park;
using Yandex.Taximeter.Core.Services.Domain;
using Yandex.Taximeter.Core.Services.Driver;
using Yandex.Taximeter.Core.Services.Driver.Import;

namespace Yandex.Taximeter.Common.Tests.Services.Driver.Import
{
    public class DriverImportParserTests : IClassFixture<CommonFixture>
    {
        private readonly XDocument _validDriverXml;

        public DriverImportParserTests()
        {
            _validDriverXml = XDocument.Load(@"Services/Driver/Import/ValidDriver.xml");
        }

        [Fact]
        public void Parse_ValidInput()
        {
            var parser = new DriverImportParser(_validDriverXml.Root);

            //Assert
            parser.ParseUuid().Should().Be("6b4cfb8ac93540bfba2ceda714380dd4");
            parser.ParseDb().Should().Be("27b40f222a4945758eafca9b402a7e21");
            parser.ParseDateLastUpdate().Should().Be("17.04.2015T11:37:44");

            var disabledInfo = parser.ParseDisabledInfo();
            disabledInfo.Disabled.Should().BeTrue();
            disabledInfo.Message.Should().Be("some msg");

            var driver = parser.Parse(parser.ParseUuid());
            driver.WorkStatus.Should().Be(DriverWorkStatus.Working);
            driver.FirstName.Should().Be("Александр");
            driver.LastName.Should().Be("Петров");
            driver.MiddleName.Should().Be("Сергеевич"); //TODO: надо исследовать. либо названия полей не отражают их суть, либо это баг
            driver.Phones.Should().BeEquivalentTo("+79100081445");
            driver.LicenseSeries.Should().Be("23");
            driver.LicenseNumber.Should().Be("43277");
            driver.LicenseIssueDate.Should().Be(new DateTime(2015, 4, 17));
            driver.LicenseExpireDate.Should().Be(new DateTime(2020, 4, 17));
            driver.LicenseExperienceSinceDate.Should().Be(new DateTime(1994, 1, 1));
            driver.RuleId.Should().Be(DriverWorkRuleService.DEFAULT_RULE_WORK_ID);
            driver.CarId.Should().Be("a164df5cf63449ddad0b72026385d73e");
            driver.Password.Should().Be("419320");
            driver.Balance.Should().Be(2000);
            driver.BalanceLimit.Should().Be(500);
            driver.Providers.Should().BeEquivalentTo(new[] { ParkProvider.Yandex });
            driver.HiringSource.Should().Be("scout");
            driver.HiringType.Should().Be(DriverHiringDetails.HIRING_TYPE_COMMERCIAL);
        }

        [Fact]
        public void BuildInsert_Fills_HiringDetails()
        {
            var parser = new DriverImportParser(_validDriverXml.Root);
            var driver = parser.Parse(parser.ParseUuid());

            var timeBeforeParse = DateTime.UtcNow;
            var driverDto = driver.BuildInsert();

            driverDto.HiringDetails.Should().NotBeNull();
            driverDto.HiringDetails.HiringType.Should().Be(DriverHiringDetails.HIRING_TYPE_COMMERCIAL);
            driverDto.HiringDetails.HiringDate.Should().BeAfter(timeBeforeParse);
        }
        
        [Fact]
        public void BuildInsert_Ignores_HiringDetails()
        {
            var parser = new DriverImportParser(_validDriverXml.Root);
            var driver = parser.Parse(parser.ParseUuid());
            driver.HiringType = null;
            var driverDto = driver.BuildInsert();

            driverDto.HiringDetails.Should().BeNull();
        }

        [Fact]
        public void Parse_IgnoreHiringSource()
        {
            var parser = new DriverImportParser(_validDriverXml.Root, true);
            
            var driver = parser.Parse(parser.ParseUuid());
            driver.HiringSource.Should().BeNullOrEmpty();
            driver.HiringType.Should().BeNullOrEmpty();
        }
    }
}
