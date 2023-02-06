using System;
using System.Diagnostics;
using System.Xml.Linq;
using FluentAssertions;
using Moq;
using Xunit;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Models.Geography;
using Yandex.Taximeter.Core.Services.Settings;
using System.Globalization;
using System.Linq;
using Newtonsoft.Json;
using Yandex.Taximeter.Core.Models.Driver.Dashboard;
using Yandex.Taximeter.Core.Models.Orders;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Car;
using Yandex.Taximeter.Core.Services.Geometry;
using Yandex.Taximeter.Core.Services.Order.Dto;
using Yandex.Taximeter.Core.Services.Order.SetCar;
using Yandex.Taximeter.Core.Services.Order.SetCar.Model;
using Yandex.Taximeter.Test.Utils.Fakes;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Services.Order
{
    public class SetCarParserTests
    {
        private static readonly CultureInfo DefaultCulture = CultureInfo.GetCultureInfo("ru");

        private const string SOME_REGION = "some_region";
        private readonly SetCarParser _setCarParser;

        public SetCarParserTests()
        {
            var settingsService = new Mock<IGlobalSettingsService>();
            _setCarParser = new SetCarParser(
                settingsService.Object,
                Mock.Of<IParkRepository>(),
                new FakeLogger<SetCarParser>())
            {
                GeocoderRegionByCoordinates = (pt, level) => SOME_REGION
            };
        }

        [Fact]
        public void ParseCancelReasonInfo_ParseAll()
        {
            var xml = XElement.Parse("<SetCar><CancelReasonInfo><AllReasons>" +
                                     "<Reason id=\"COULD_NOT_SATISFY_CLIENT_COMMENT\">" +
                                     "Couldn\'t satisfy user\'s comment</Reason>" +
                                     "<Reason id=\"PROBLEMS_WITH_CAR\">Problems with car</Reason>" +
                                     "<Reason id=\"INADEQUATE_PASSENGER\">Passenger\'s behavior is terrible</Reason>" +
                                     "<Reason id=\"PASSENGER_WITH_CHILD\">Passenger with child</Reason>" +
                                     "<Reason id=\"NOT_SATISFIED_TARIFF_OR_ADDRESS\">Tariff or address is not good" +
                                     "</Reason>" +
                                     "<Reason id=\"CLIENT_DID_NOT_COME\">Client did not come</Reason>" +
                                     "<Reason id=\"OTHER\">Other</Reason></AllReasons>" +
                                     "<Statuses><Status name=\"waiting\">" +
                                     "<Reason>INADEQUATE_PASSENGER</Reason>" +
                                     "<Reason>PASSENGER_WITH_CHILD</Reason>" +
                                     "<Reason>NOT_SATISFIED_TARIFF_OR_ADDRESS</Reason>" +
                                     "<Reason>OTHER</Reason></Status>" +
                                     "<Status name=\"long_waiting\">" +
                                     "<Reason>INADEQUATE_PASSENGER</Reason>" +
                                     "<Reason>PASSENGER_WITH_CHILD</Reason>" +
                                     "<Reason>NOT_SATISFIED_TARIFF_OR_ADDRESS</Reason>" +
                                     "<Reason>CLIENT_DID_NOT_COME</Reason>" +
                                     "<Reason>OTHER</Reason></Status>" +
                                     "<Status name=\"driving\">" +
                                     "<Reason>COULD_NOT_SATISFY_CLIENT_COMMENT</Reason>" +
                                     "<Reason>PROBLEMS_WITH_CAR</Reason></Status>" +
                                     "</Statuses>" +
                                     "</CancelReasonInfo></SetCar>");

            var item = _setCarParser.ParseSetCarBase(xml, Provider.Яндекс);

            Debug.Assert(item.CancelReasonInfoObj != null);
            var jsonStr = JsonConvert.SerializeObject(item.CancelReasonInfoObj);
            jsonStr.Should().Be("{\"reasons\":[" +
                "{\"id\":\"COULD_NOT_SATISFY_CLIENT_COMMENT\",\"text\":\"Couldn't satisfy user's comment\"}," +
                "{\"id\":\"PROBLEMS_WITH_CAR\",\"text\":\"Problems with car\"}," +
                "{\"id\":\"INADEQUATE_PASSENGER\",\"text\":\"Passenger's behavior is terrible\"}," +
                "{\"id\":\"PASSENGER_WITH_CHILD\",\"text\":\"Passenger with child\"}," +
                "{\"id\":\"NOT_SATISFIED_TARIFF_OR_ADDRESS\",\"text\":\"Tariff or address is not good\"}," +
                "{\"id\":\"CLIENT_DID_NOT_COME\",\"text\":\"Client did not come\"}," +
                "{\"id\":\"OTHER\",\"text\":\"Other\"}]," +
                "\"reasons_by_status\":{" +
                  "\"waiting\":[\"INADEQUATE_PASSENGER\",\"PASSENGER_WITH_CHILD\"," +
                               "\"NOT_SATISFIED_TARIFF_OR_ADDRESS\",\"OTHER\"]," +
                  "\"long_waiting\":[\"INADEQUATE_PASSENGER\",\"PASSENGER_WITH_CHILD\"," +
                                    "\"NOT_SATISFIED_TARIFF_OR_ADDRESS\",\"CLIENT_DID_NOT_COME\",\"OTHER\"]," +
                  "\"driving\":[\"COULD_NOT_SATISFY_CLIENT_COMMENT\",\"PROBLEMS_WITH_CAR\"]" +
                  "}}");
        }

        [Fact]
        public void ParseCancelReasonInfo_ParseEmpty()
        {
            var xml = XElement.Parse("<SetCar><CancelReasonInfo><AllReasons>" +
                                     "</AllReasons>" +
                                     "</CancelReasonInfo></SetCar>");

            var item = _setCarParser.ParseSetCarBase(xml, Provider.Яндекс);

            Debug.Assert(item.CancelReasonInfoObj == null);
        }

        [Fact]
        public void ParseCancelReasonInfo_ParseReasons()
        {
            var xml = XElement.Parse("<SetCar><CancelReasonInfo><AllReasons>" +
                                     "<Reason id=\"COULD_NOT_SATISFY_CLIENT_COMMENT\">" +
                                     "Couldn\'t satisfy user\'s comment</Reason>" +
                                     "<Reason id=\"PROBLEMS_WITH_CAR\">Problems with car</Reason>" +
                                     "<Reason id=\"INADEQUATE_PASSENGER\">Passenger\'s behavior is terrible</Reason>" +
                                     "<Reason id=\"PASSENGER_WITH_CHILD\">Passenger with child</Reason>" +
                                     "<Reason id=\"NOT_SATISFIED_TARIFF_OR_ADDRESS\">Tariff or address is not good" +
                                     "</Reason>" +
                                     "<Reason id=\"CLIENT_DID_NOT_COME\">Client did not come</Reason>" +
                                     "<Reason id=\"OTHER\">Other</Reason></AllReasons>" +
                                     "</CancelReasonInfo></SetCar>");

            var item = _setCarParser.ParseSetCarBase(xml, Provider.Яндекс);

            Debug.Assert(item.CancelReasonInfoObj != null);
            var jsonStr = JsonConvert.SerializeObject(item.CancelReasonInfoObj);
            Debug.Print(jsonStr);
            jsonStr.Should().Be("{\"reasons\":[" +
                                "{\"id\":\"COULD_NOT_SATISFY_CLIENT_COMMENT\",\"text\":\"Couldn't satisfy user's comment\"}," +
                                "{\"id\":\"PROBLEMS_WITH_CAR\",\"text\":\"Problems with car\"}," +
                                "{\"id\":\"INADEQUATE_PASSENGER\",\"text\":\"Passenger's behavior is terrible\"}," +
                                "{\"id\":\"PASSENGER_WITH_CHILD\",\"text\":\"Passenger with child\"}," +
                                "{\"id\":\"NOT_SATISFIED_TARIFF_OR_ADDRESS\",\"text\":\"Tariff or address is not good\"}," +
                                "{\"id\":\"CLIENT_DID_NOT_COME\",\"text\":\"Client did not come\"}," +
                                "{\"id\":\"OTHER\",\"text\":\"Other\"}]}");
        }

        [Fact]
        public void ParseFixedPrice_NullElement_ReturnsNull()
        {
            var item = new SetCarItem();
            var result = _setCarParser.ParseFixedPrice(item, OrderStatus.none, null, XElement.Parse("<SetCar/>"));
            result.Should().BeFalse();
        }

        [Fact]
        public void ParseFixedPrice_Disabled_ReturnsNull()
        {
            var item = new SetCarItem();
            var xml = XElement.Parse("<SetCar><FixedPrice enabled=\"no\"></FixedPrice></SetCar>");
            var result = _setCarParser.ParseFixedPrice(item, OrderStatus.none, null, xml);
            result.Should().BeTrue();
            item.FixedPrice.Should().BeNull();
        }

        [Fact]
        public void ParseFixedPrice_Enabled_PriceNotSecified_ThrowsException()
        {
            var item = new SetCarItem();
            var xml = XElement.Parse("<SetCar><FixedPrice enabled=\"yes\"></FixedPrice></SetCar>");
            Assert.Throws<FormatException>(
                () => _setCarParser.ParseFixedPrice(item, OrderStatus.none, null, xml));
        }

        [Fact]
        public void ParseFixedPrice_Enabled_PriceSpecified_Parses()
        {
            var item = new SetCarItem();
            var xml = XElement.Parse(
                "<SetCar><FixedPrice enabled=\"yes\" max_distance=\"350\">200</FixedPrice></SetCar>");
            var result = _setCarParser.ParseFixedPrice(item, OrderStatus.none,
                new GlobalSettings {ShowFixedPrice = true}, xml);
            result.Should().BeTrue();
            item.FixedPrice.Price.Should().BeApproximately(200, 0.000001);
            item.FixedPrice.MaxDistance.Should().BeApproximately(350, 0.000001);
            item.FixedPrice.Show.Should().BeTrue();
        }

        [Theory]
        [InlineData("yes", true, true)]
        [InlineData("no", true, true)]
        [InlineData("yes", false, true)]
        [InlineData("no", false, false)]
        public void ParseFixedPrice_show_price_Parses(string xmlValue, bool showFixedPrice, bool expectedParsedValue)
        {
            var item = new SetCarItem();
            var xml = XElement.Parse(
                $"<SetCar><FixedPrice enabled=\"yes\" show_price=\"{xmlValue}\">200</FixedPrice></SetCar>");
            var result = _setCarParser.ParseFixedPrice(item, OrderStatus.none,
                new GlobalSettings {ShowFixedPrice = showFixedPrice}, xml);
            result.Should().BeTrue();
            item.FixedPrice.Show.Should().Be(expectedParsedValue);
        }

        [Fact]
        public void ParseFixedPrice_show_price_in_reveal_price_status()
        {
            var item = new SetCarItem();
            var xml = XElement.Parse(
                "<SetCar><FixedPrice enabled=\"yes\">200</FixedPrice></SetCar>");
            var result = _setCarParser.ParseFixedPrice(item, FixedPriceSettings.REVEAL_PRICE_STATUS,
                new GlobalSettings {ShowFixedPrice = true}, xml);
            result.Should().BeTrue();
            item.FixedPrice.Show.Should().BeTrue();
        }


        [Fact]
        public void ParseSourceAddress_NotEmptyElement_EmptyCoordinates_ParsesAddress()
        {
            var xml = XElement.Parse("<SetCar><Source>" +
                                     "<FullName>full_name</FullName>" +
                                     "<ShortName>short_name</ShortName>" +
                                     "<Country><Locality><Thoroughfare><Premise><PorchNumber>" +
                                     "3" +
                                     "</PorchNumber></Premise></Thoroughfare></Locality></Country>" +
                                     "</Source></SetCar>");

            var address = _setCarParser.ParseSourceAddress(xml, DefaultCulture);

            Debug.Assert(address != null);
            address.Street.Should().Be("short_name, подъезд 3");
            address.Region.Should().BeNull(); //Parsed only if point specified
            address.Lon.Should().Be(0);
            address.Lat.Should().Be(0);
            address.Porch.Should().Be("3");
        }

        [Fact]
        public void ParseSourceAddress_NotEmptyElement_DetailedInfo_ParsesAddress()
        {
            var xml = XElement.Parse("<SetCar><Source>" +
                                     "<FullName>full_name</FullName>" +
                                     "<ShortName>short_name</ShortName>" +
                                     "<Country><Locality><Thoroughfare><Premise><PorchNumber>" +
                                     "3" +
                                     "</PorchNumber></Premise></Thoroughfare></Locality></Country>" +
                                     "<ExtraData>" +
                                     "<Floor>5</Floor>" +
                                     "<Apartment>75</Apartment>" +
                                     "<Comment>Скажите консьержке, что вы курьер</Comment>" +
                                     "</ExtraData>" +
                                     "</Source></SetCar>");

            var address = _setCarParser.ParseSourceAddress(xml, DefaultCulture);

            Debug.Assert(address != null);
            address.Porch.Should().Be("3");
            address.Comment.Should().Be("Скажите консьержке, что вы курьер");
            address.ApartmentInfo.Should().Be("3 подъезд, 5 этаж, 75 квартира.");
        }

        [Fact]
        public void ParseSourceAddress_NotEmptyElement_PartlyDetailedInfo_ParsesAddress()
        {
            var xml = XElement.Parse("<SetCar><Source>" +
                                     "<FullName>full_name</FullName>" +
                                     "<ShortName>short_name</ShortName>" +
                                     "<ExtraData>" +
                                     "<Floor>5</Floor>" +
                                     "</ExtraData>" +
                                     "</Source></SetCar>");

            var address = _setCarParser.ParseSourceAddress(xml, DefaultCulture);

            Debug.Assert(address != null);
            address.Comment.Should().BeNullOrEmpty();
            address.ApartmentInfo.Should().Be("5 этаж.");
        }

        [Fact]
        public void ParseSourceAddress_NotEmptyElement_ExactPoint_ParsesAddress()
        {
            var xml = XElement.Parse("<SetCar><Source>" +
                                     "<FullName>full_name</FullName>" +
                                     "<ShortName>short_name</ShortName>" +
                                     "<Point exact=\"true\"><Lon>37.587874</Lon><Lat>55.73367</Lat></Point>" +
                                     "</Source></SetCar>");

            var address = _setCarParser.ParseSourceAddress(xml, DefaultCulture);

            Debug.Assert(address != null);
            address.Street.Should().Be("Рядом с: short_name");
            address.Region.Should().Be(SOME_REGION);
            Assert.True(Math.Abs(address.Lon - 37.587874) < 0.00001);
            Assert.True(Math.Abs(address.Lat - 55.73367) < 0.00001);
        }

        [Fact]
        public void ParseDestinations_EmptyElement_ReturnsEmptyArray()
        {
            var item = new SetCarItem();

            var xml = XElement.Parse("<SetCar><Destinations></Destinations></SetCar>");

            _setCarParser.ParseDestinations(item, xml, DefaultCulture);

            item.RoutePoints.Should().BeEmpty();
        }

        [Fact]
        public void ParseDestinations_NullElement_ReturnsFalse()
        {
            var item = new SetCarItem();

            var result = _setCarParser.ParseDestinations(item, XElement.Parse("<SetCar/>"), DefaultCulture);
            result.Should().BeFalse();
            item.multiplys.Should().BeNull();
            item.RoutePoints.Should().BeNull();
        }

        [Fact]
        public void ParseDestinations_NotEmptyElement_ParsesAddresses()
        {
            var item = new SetCarItem();

            var xml = XElement.Parse("<SetCar><Destinations>" +
                                     "<Destination order=\"1\" arrival_distance=\"300\">" +
                                     "<FullName>full_name_1</FullName>" +
                                     "<Point><Lon>37.641692</Lon><Lat>55.76996</Lat></Point>" +
                                     "</Destination>" +
                                     "<Destination order=\"2\">" +
                                     "<FullName>full_name_2</FullName>" +
                                     "<Point><Lon>37.5798068843</Lon><Lat>55.7498240826</Lat></Point>" +
                                     "</Destination>" +
                                     "</Destinations></SetCar>");

            _setCarParser.ParseDestinations(item, xml, DefaultCulture);

            item.RoutePoints.Length.Should().Be(1);
            item.RoutePoints[0].Street.Should().Be("full_name_1");
            item.RoutePoints[0].Order.Should().Be(1);
            item.RoutePoints[0].ArrivalDistance.Should().Be(300);
            item.AddressTo.Street.Should().Be("full_name_2");
            item.AddressTo.Order.Should().Be(2);
            item.AddressTo.ArrivalDistance.Should().Be(Address.DEFAULT_ARRIVAL_DISTANCE);
        }

        [Fact]
        public void ParseDestinations_HideUntilWaiting_ShowAddressIsFalse()
        {
            var item = new SetCarItem();

            var xml = XElement.Parse("<SetCar><Destinations hide_until_waiting=\"yes\">" +
                                     "<Destination order=\"1\" arrival_distance=\"300\">" +
                                     "<FullName>full_name_1</FullName>" +
                                     "<Point><Lon>37.641692</Lon><Lat>55.76996</Lat></Point>" +
                                     "</Destination>" +
                                     "</Destinations></SetCar>");

            _setCarParser.ParseDestinations(item, xml, DefaultCulture);

            item.AddressTo.Should().NotBeNull();
            item.show_address.Should().BeFalse();
        }

        [Fact]
        public void ParseDestinations_HideUntilWaiting_ShowAddressIsTrue()
        {
            var item = new SetCarItem();

            var xml = XElement.Parse("<SetCar><Destinations hide_until_waiting=\"no\">" +
                                     "<Destination order=\"1\" arrival_distance=\"300\">" +
                                     "<FullName>full_name_1</FullName>" +
                                     "<Point><Lon>37.641692</Lon><Lat>55.76996</Lat></Point>" +
                                     "</Destination>" +
                                     "</Destinations></SetCar>");

            _setCarParser.ParseDestinations(item, xml, DefaultCulture);

            item.AddressTo.Should().NotBeNull();
            item.show_address.Should().BeTrue();
        }

        [Fact]
        public void ParseDestinations_ShowAddressDoesNotChange()
        {
            var item = new SetCarItem
            {
                show_address = true
            };
            var xml = XElement.Parse("<SetCar><Destinations>" +
                                     "<Destination order=\"1\" arrival_distance=\"300\">" +
                                     "<FullName>full_name_1</FullName>" +
                                     "<Point><Lon>37.641692</Lon><Lat>55.76996</Lat></Point>" +
                                     "</Destination>" +
                                     "</Destinations></SetCar>");

            _setCarParser.ParseDestinations(item, xml, DefaultCulture);
            item.AddressTo.Should().NotBeNull();
            item.show_address.Should().BeTrue();
        }

        [Theory]
        [InlineData("<SetCar></SetCar>")]
        [InlineData("<SetCar><Requirements/><SoftRequirements/></SetCar>")]
        public void ParseRequirements_NullXml_ReturnsEmptyRequirement(string rawXml)
        {
            var xml = XElement.Parse(rawXml);

            var reqs = _setCarParser.ParseRequirements(xml);

            reqs.List.Should().BeEmpty();
            reqs.DontCall.Should().BeFalse();
            reqs.PayType.Should().BeNull();
            reqs.TariffDiscount.Should().BeNull();
            reqs.WaitPaymentComplete.Should().BeNull();
            reqs.WarnNoCard.Should().BeNull();
        }

        [Fact]
        public void ParseRequirements_FullXml_ParsesRequirements()
        {
            var xml = XElement.Parse(
                "<SetCar>" +
                "<Requirements>" +
                "<Require name=\"has_conditioner\">yes</Require>" +
                "<Require name=\"no_smoking\">yes</Require>" +
                "<Require name=\"child_chair\">1</Require>" +
                "<Require name=\"animal_transport\">yes</Require>" +
                "<Require name=\"universal\">yes</Require>" +
                "<Require name=\"wifi\">yes</Require>" +
                "<Require name=\"check\">yes</Require>" +
                "<Require name=\"card\">yes</Require>" +
                "<Require name=\"yamoney\">yes</Require>" +
                "<Require name=\"newspaper\">yes</Require>" +
                "<Require name=\"coupon\">50</Require>" +
                "<Require name=\"UNSUPPORTED_REQUIREMENT\">yes</Require>" +
                "<Require name=\"creditcard\" wait_payment_complete=\"yes\" warn_no_card=\"yes\">yes</Require>" +
                "<Require name=\"child_chair.booster\">2</Require>" +
                "<Require name=\"child_chair.chair\">3</Require>" +
                "<Require name=\"child_chair.infant\">4</Require>" +
                "<Require name=\"cargo_clean\">yes</Require>" +
                "<Require name=\"cargo_loaders\">2</Require>" +
                "<Require name=\"ski_transporting\">yes</Require>" +
                "</Requirements>" +
                "<SoftRequirements>" +
                "<Require name=\"dont_call\">yes</Require>" +
                "</SoftRequirements>" +
                "<PaymentMethod type=\"card\"/>" +
                "</SetCar>");

            var reqs = _setCarParser.ParseRequirements(xml);

            reqs.List.Any(x => x.Id == "child_chair").Should()
                .BeFalse("При наличии требований child_chair.*  обычный child_chair не должен попадать в список");
            reqs.List.Select(x => x.Id).Should().BeEquivalentTo(
                "conditioner", "no_smoking", "animal_transport", "universal", "wifi", "check",
                "card", "yamoney", "newspaper", "coupon", "creditcard", "child_chair.booster", "child_chair.chair",
                "child_chair.infant", "dont_call", "cargo_clean", "cargo_loaders", "ski_transporting");
            reqs.List.First(x => x.Id == "child_chair.booster").Amount.Should().Be(2);
            reqs.List.First(x => x.Id == "child_chair.chair").Amount.Should().Be(3);
            reqs.List.First(x => x.Id == "child_chair.infant").Amount.Should().Be(4);
            reqs.List.First(x => x.Id == "cargo_loaders").Amount.Should().Be(2);
            reqs.DontCall.Should().BeTrue();
            reqs.PayType.Should().Be(OrderPayType.Безналичные);
            reqs.TariffDiscount.Should().NotBeNull();
            reqs.WaitPaymentComplete.Should().BeTrue();
            reqs.WarnNoCard.Should().BeTrue();
        }

        [Fact]
        public void ParseRequirements_OnlyChildChair_ParsesRequirements()
        {
            var xml = XElement.Parse(
                "<SetCar>" +
                "<Requirements>" +
                "<Require name=\"child_chair\">yes</Require>" +
                "</Requirements>" +
                "</SetCar>");

            var reqs = _setCarParser.ParseRequirements(xml);
            reqs.List.Select(x => x.Id).Should().BeEquivalentTo("child_chair");
        }

        [Fact]
        public void ParseRequirements_IsEditable_ParsesRequirements()
        {
            var xml = XElement.Parse(@"
<SetCar>
    <Requirements>
        <Require is_editable=""yes"" max_amount=""1"" name=""third_passenger"" min_amount=""0"">0</Require>
        <Require is_editable=""yes"" max_amount=""3"" name=""luggage_count"" min_amount=""0"">2</Require>
        <Require name=""creditcard"">yes</Require>
    </Requirements>
</SetCar>");
            var reqs = _setCarParser.ParseRequirements(xml);
            JsonConvert.SerializeObject(reqs).Should().BeEquivalentTo(
                "{\"List\":[" +
                "{\"id\":\"third_passenger\",\"amount\":0,\"is_editable\":true,\"min_amount\":0,\"max_amount\":1}," +
                "{\"id\":\"luggage_count\",\"amount\":2,\"is_editable\":true,\"min_amount\":0,\"max_amount\":3}," +
                "{\"id\":\"creditcard\"}" +
                "],\"WaitPaymentComplete\":false,\"WarnNoCard\":false}");
        }


        [Fact]
        public void ParseRequirements_HourlyRental_ParsesRequirements()
        {
            var xml = XElement.Parse(@"
<SetCar>
    <Requirements>
        <Require name=""hourly_rental.2_hours"">yes</Require>
    </Requirements>
</SetCar>");
            var reqs = _setCarParser.ParseRequirements(xml);
            JsonConvert.SerializeObject(reqs).Should().BeEquivalentTo(
                "{\"List\":[" +
                "{\"id\":\"hourly_rental.2_hours\"}" +
                "]}");
        }

        [Fact]
        public void ParsePriceCorrections_NullElement_ReturnsFalse()
        {
            var xml = XElement.Parse(
                "<SetCar>" +
                "</SetCar>");

            var item = new SetCarItem();
            var result = _setCarParser.ParsePriceCorrections(item, xml);
            result.Should().BeFalse();
            item.multiplys.Should().BeNull();
        }

        [Fact]
        public void ParsePriceCorrections_NotEmpty_Parses()
        {
            var xml = XElement.Parse(
                "<SetCar>" +
                "<Cars>" +
                "<Car>" +
                "<SoftRequirements>" +
                "<PriceCorrections>" +
                "<Multiply item=\"price_per_km\" value=\"2.05\"></Multiply>" +
                "<Multiply item=\"price_per_minute\" value=\"3.06\"></Multiply>" +
                "<Multiply item=\"minimal_price\" value=\"4.07\"></Multiply>" +
                "<Surcharge value=\"30.0\"></Surcharge>" +
                "<Message value=\"+ 100\"></Message>" +
                "</PriceCorrections>" +
                "</SoftRequirements>" +
                "</Car>" +
                "</Cars>" +
                "</SetCar>");

            var item = new SetCarItem();
            var result = _setCarParser.ParsePriceCorrections(item, xml);
            result.Should().BeTrue();
            item.multiplys.Should().NotBeNull();
            item.multiplys.PricePerKm.Should().Be(2.05);
            item.multiplys.PricePerMinute.Should().Be(3.06);
            item.multiplys.MinimalPrice.Should().Be(4.07);
            item.multiplys.Surcharge.Should().Be(30.0);
            item.multiplys.SurgeText.Should().Be("+ 100");
        }

        [Fact]
        public void ParsePriceCorrections_Partial_Parses()
        {
            var xml = XElement.Parse(
                "<SetCar>" +
                "<Cars>" +
                "<Car>" +
                "<SoftRequirements>" +
                "<PriceCorrections>" +
                "<Multiply item=\"price_per_minute\" value=\"3.06\"></Multiply>" +
                "<Multiply item=\"minimal_price\" value=\"4.07\"></Multiply>" +
                "<Surcharge value=\"30.0\"></Surcharge>" +
                "</PriceCorrections>" +
                "</SoftRequirements>" +
                "</Car>" +
                "</Cars>" +
                "</SetCar>");

            var item = new SetCarItem();
            var result = _setCarParser.ParsePriceCorrections(item, xml);
            result.Should().BeFalse();
            item.multiplys.Should().BeNull();
        }

        [Fact]
        public void ParseTaximeterSettings_NullElement_ReturnsNull()
        {
            var item = new SetCarItem();
            var result = _setCarParser.ParseTaximeterSettings(item, XElement.Parse("<SetCar/>"));
            result.Should().BeFalse();
            item.TaximeterSettings.Should().BeNull();
        }

        [Fact]
        public void ParseTaximeterSettings_NullPropertyElements()
        {
            var item = new SetCarItem();
            var xml = XElement.Parse("<SetCar><TaximeterSettings></TaximeterSettings></SetCar>");
            _setCarParser.ParseTaximeterSettings(item, xml);
            item.TaximeterSettings.HideCostWidget.Should().BeFalse();
            item.TaximeterSettings.HideCostCounter.Should().BeFalse();
            item.TaximeterSettings.HideCostPlate.Should().BeFalse();
            item.TaximeterSettings.Voucher.Should().BeFalse();
            item.TaximeterSettings.DontCheckDistanceToSourcePoint.Should().BeFalse();
            item.TaximeterSettings.ShowingPaymentTypeFor.Should()
                .BeEquivalentTo(TaximeterSettings.DefaultShowingPaymentTypeFor);
            item.TaximeterSettings.ShowingSurgeFor.Should()
                .BeEquivalentTo(TaximeterSettings.DefaultShowingSurgeFor);
            item.TaximeterSettings.StatusChangeDelays.Should().BeEmpty();
            item.TaximeterSettings.ShowUserCost.Should().BeNull();
        }

        [Fact]
        public void ParseAutoConfirmationSettingsTest_Null()
        {
            var item = new SetCarItem();
            var xml = XElement.Parse("<SetCar><TaximeterSettings></TaximeterSettings></SetCar>");
            _setCarParser.ParseTaximeterSettings(item, xml);
            item.TaximeterSettings.AutoConfirmation.Should().BeNull();
        }

        [Fact]
        public void ParseAutoConfirmationSettingsTest_Full()
        {
            var item = new SetCarItem();
            var xml = XElement.Parse(
                "<SetCar><TaximeterSettings><AutoConfirmation set_status=\"transporting\" enabled=\"yes\" flow=\"code_dispatch\"/> </TaximeterSettings></SetCar>");
            _setCarParser.ParseTaximeterSettings(item, xml);
            item.TaximeterSettings.AutoConfirmation.Should().NotBeNull();
            item.TaximeterSettings.AutoConfirmation.Enabled.Should().Be(true);
            item.TaximeterSettings.AutoConfirmation.SetStatus.Should().Be(RequestConfirmStatus.Transporting);
            item.TaximeterSettings.AutoConfirmation.Flow.Should().Be("code_dispatch");

        }

        [Theory]
        [InlineData("yes", true)]
        [InlineData("no", false)]
        public void ParseTaximeterSettings_NotNullCostElements(string xmlValue, bool expectedParsedValue)
        {
            var item = new SetCarItem();
            var xml = XElement.Parse("<SetCar><TaximeterSettings>" +
                                     $"<CostWidget hide=\"{xmlValue}\"/>" +
                                     $"<CostCounter hide=\"{xmlValue}\"/>" +
                                     $"<CostPlate hide=\"{xmlValue}\"/>" +
                                     "</TaximeterSettings></SetCar>");
            _setCarParser.ParseTaximeterSettings(item, xml);
            item.TaximeterSettings.HideCostWidget.Should().Be(expectedParsedValue);
            item.TaximeterSettings.HideCostCounter.Should().Be(expectedParsedValue);
            item.TaximeterSettings.HideCostPlate.Should().Be(expectedParsedValue);
        }

        [Theory]
        [InlineData("yes", true)]
        [InlineData("no", false)]
        public void ParseTaximeterSettings_DontCheckDistanceToSourcePoint(string xmlValue, bool expectedParsedValue)
        {
            var item = new SetCarItem();
            var xml = XElement.Parse("<SetCar><TaximeterSettings>" +
                                     $"<DontCheckDistanceToSourcePoint enabled=\"{xmlValue}\"/>" +
                                     "</TaximeterSettings></SetCar>");
            _setCarParser.ParseTaximeterSettings(item, xml);
            item.TaximeterSettings.DontCheckDistanceToSourcePoint.Should().Be(expectedParsedValue);
        }

        [Theory]
        [InlineData("yes", true)]
        [InlineData("no", false)]
        public void ParseTaximeterSettings_HideUserCost(string xmlValue, bool expectedParsedValue)
        {
            var item = new SetCarItem();
            var xml = XElement.Parse("<SetCar><TaximeterSettings>" +
                                     $"<ShowUserCost enabled=\"{xmlValue}\"/>" +
                                     "</TaximeterSettings></SetCar>");
            _setCarParser.ParseTaximeterSettings(item, xml);
            item.TaximeterSettings.ShowUserCost.Should().Be(expectedParsedValue);
        }

        [Theory]
        [InlineData("yes", true)]
        [InlineData("no", false)]
        public void ParseTaximeterSettings_Voucher(string xmlValue, bool expectedParsedValue)
        {
            var item = new SetCarItem();
            var xml = XElement.Parse("<SetCar><TaximeterSettings>" +
                                     $"<Voucher accept=\"{xmlValue}\"/>" +
                                     "</TaximeterSettings></SetCar>");
            _setCarParser.ParseTaximeterSettings(item, xml);
            item.TaximeterSettings.Voucher.Should().Be(expectedParsedValue);
        }

        [Fact]
        public void ParseTaximeterSettings_NotNullShowingPaymentTypeFor()
        {
            var item = new SetCarItem();
            var xml = XElement.Parse("<SetCar><TaximeterSettings>" +
                                     "<ShowingPaymentTypeFor>" +
                                     "<Status>assigned</Status>" +
                                     "<Status>driving</Status><Status>waiting</Status>" +
                                     "<Status>transporting</Status><Status>complete</Status>" +
                                     "</ShowingPaymentTypeFor>" +
                                     "</TaximeterSettings></SetCar>");
            _setCarParser.ParseTaximeterSettings(item, xml);
            item.TaximeterSettings.ShowingPaymentTypeFor.Should().BeEquivalentTo(
                new[]
                {
                    RequestConfirmStatus.Assigned,
                    RequestConfirmStatus.Driving,
                    RequestConfirmStatus.Waiting,
                    RequestConfirmStatus.Transporting,
                    RequestConfirmStatus.Complete
                });
        }

        [Fact]
        public void ParseTaximeterSettings_NotNullShowingSurgeFor()
        {
            var item = new SetCarItem();
            var xml = XElement.Parse("<SetCar><TaximeterSettings>" +
                                     "<ShowingSurgeFor>" +
                                     "<Status>assigned</Status><Status>driving</Status><Status>waiting</Status>" +
                                     "</ShowingSurgeFor>" +
                                     "</TaximeterSettings></SetCar>");
            _setCarParser.ParseTaximeterSettings(item, xml);
            item.TaximeterSettings.ShowingSurgeFor.Should()
                .BeEquivalentTo(
                    new[]
                    {
                        RequestConfirmStatus.Assigned,
                        RequestConfirmStatus.Driving,
                        RequestConfirmStatus.Waiting
                    });
        }

        [Fact]
        public void ParseTaximeterSettings_NotNullStatusChangeDelays()
        {
            var item = new SetCarItem();
            var xml = XElement.Parse("<SetCar><TaximeterSettings>" +
                                     "<StatusChangeCooldowns>" +
                                     "<Cooldown status=\"driving\" value=\"10\"/>" +
                                     "<Cooldown status=\"waiting\" value=\"20\"/>" +
                                     "</StatusChangeCooldowns>" +
                                     "</TaximeterSettings></SetCar>");
            _setCarParser.ParseTaximeterSettings(item, xml);
            var parsed = item.TaximeterSettings.StatusChangeDelays;
            parsed.Count.Should().Be(2);
            parsed[((int) RequestConfirmStatus.Driving).ToString()].Should().Be(10);
            parsed[((int) RequestConfirmStatus.Waiting).ToString()].Should().Be(20);
        }

        [Fact]
        public void ParseYandexGeoareas_ZonesAttributeNull_ReturnsNull()
        {
            var element = XElement.Parse("<Tariff></Tariff>");
            var result = _setCarParser.ParseYandexGeoareas(element);
            result.Should().BeNull();
        }

        [Fact]
        public void ParseYandexGeoareas_ZonesAttributePresent_ParsesZones()
        {
            var element = XElement.Parse("<Tariff zones=\"id1,id2,id3\"></Tariff>");
            var result = _setCarParser.ParseYandexGeoareas(element);
            result.Should().BeEquivalentTo("id1", "id2", "id3");
        }

        [Fact]
        public void ParseRealSetCarBase_Yandex()
        {
            var xml = XElement.Parse(

            #region SetCar xml

                @"<Request direct_assignment=""yes"">
    <Orderid>faaa8333b9f849e284b718b717ad8ca2</Orderid>
    <OrderSource origin=""uber""/>
    <ConfirmationRestrictions autocancel_delay_seconds=""13"" max_seen_time=""2017-06-07T00:07:32.742091+0300""/>
    <TaximeterSettings>
        <CostCounter hide=""no""/>
        <CostWidget hide=""yes""/>
        <CostPlate hide=""no""/>
        <ShowingPaymentTypeFor>
            <Status>waiting</Status>
            <Status>transporting</Status>
            <Status>complete</Status>
        </ShowingPaymentTypeFor>
        <ShowingSurgeFor>
            <Status>assigned</Status>
            <Status>driving</Status>
            <Status>waiting</Status>
        </ShowingSurgeFor>
    </TaximeterSettings>
    <Cars>
        <Car>
            <Uuid>2013ed180de6480db22ac88dc118571f</Uuid>
            <Clid>1956794047</Clid>
            <DBId>d4794d9cd5ed479bb2ade14c60b88011</DBId>
            <Tariff zones=""052d1a4431b2487487dc95550bd3430a,0d92c61fbeaf44f9b71e978ca75e0a4d,4348f5f6e84d4fde8bcee46b77dd0b0d,48b2d2bbf6284a8fb2507eae80f076b7,5a3e5b1a934248ab8e512abf9aa54f57,70ef1ee0efd142a78db526e9f75defec,7c64e39b00c241a5ae015ce07bccdd79,8a97a2ca3ee3421aa96ca72afee7a35e,8f2b98a666b4437fbbaaeadab7f5566a,9ec8e6f1fd0c4581b869bfd3a568dc82,b17c2eabb7e34928a202edc7694ba98b,b2e5d0078bd246cfad1a8dec9ef28659,bca9b71aa10f4a5cb3fed9f2a24a8dd1,dbff41b3669d4a99b336f235972a8725,eb825a9f01754789b4435d1bf72bd033,f029e9f33b8945889dffc4295b6d6e27,fdb3759eabaf474faf2eada4a08ad5af"" is_synchronizable=""true"" format_version=""1.0"">surge--8bf281d6c7264890b395f4a5b969b3cc--minimal_0.83-distance_0.83-time_0.83-hidden_0</Tariff>
            <Category>econom</Category>
            <Logistic>
                <Shift id=""id""/>
            </Logistic>
        </Car>
    </Cars>
    <Source>
        <FullName>Россия, Москва, Авиамоторная улица, 44с11</FullName>
        <ShortName>Авиамоторная улица, 44с11</ShortName>
        <Point exact=""true"">
            <Lon>37.7205949519</Lon>
            <Lat>55.7394376953</Lat>
        </Point>
        <Airport>
            <Flight/>
            <Terminal/>
        </Airport>
        <Country>
            <CountryName>Россия</CountryName>
            <Locality>
                <LocalityName>Москва</LocalityName>
                <Thoroughfare>
                    <ThoroughfareName>Авиамоторная улица</ThoroughfareName>
                    <Premise>
                        <PremiseNumber>44с11</PremiseNumber>
                        <PorchNumber/>
                    </Premise>
                </Thoroughfare>
            </Locality>
        </Country>
    </Source>
    <Destinations hide_until_waiting=""yes"">
        <Destination order=""1"" arrival_distance=""0"">
            <FullName>Россия, Москва, Подъёмная улица, 12</FullName>
            <ShortName>Подъёмная улица, 12</ShortName>
            <Point>
                <Lon>37.707063</Lon>
                <Lat>55.741313</Lat>
            </Point>
            <Airport>
                <Flight/>
                <Terminal/>
            </Airport>
            <Country>
                <CountryName>Россия</CountryName>
                <Locality>
                    <LocalityName>Москва</LocalityName>
                    <Thoroughfare>
                        <ThoroughfareName>Подъёмная улица</ThoroughfareName>
                        <Premise>
                            <PremiseNumber>12</PremiseNumber>
                        </Premise>
                    </Thoroughfare>
                </Locality>
            </Country>
        </Destination>
    </Destinations>
    <BookingTime type=""notlater"">2017-06-07T00:12:00+0300</BookingTime>
    <Requirements>
        <Require name=""creditcard"">yes</Require>
    </Requirements>
    <PaymentMethod type=""card""/>
    <Comments>Тестовый заказ</Comments>
    <Subvention>
        <Rules>
            <Rule>
                <Type>guarantee</Type>
                <Params>
                    <Param name=""sum"" value=""200.0""/>
                </Params>
            </Rule>
        </Rules>
        <Combine>max</Combine>
    </Subvention>
    <Experiments>
        <Experiment>thin_wave_experiment</Experiment>
        <Experiment>autoreorder_android</Experiment>
        <Experiment>autoreorder_notifications</Experiment>
        <Experiment>exact5</Experiment>
        <Experiment>surgeprice</Experiment>
        <Experiment>payment_change</Experiment>
        <Experiment>new_stq</Experiment>
        <Experiment>direction_with_thin_wave</Experiment>
        <Experiment>hunger_time</Experiment>
        <Experiment>forced_surge</Experiment>
        <Experiment>direct_assignment</Experiment>
        <Experiment>show_air_dest_point</Experiment>
        <Experiment>surge_add_business</Experiment>
        <Experiment>surge_distance</Experiment>
        <Experiment>fixed_price</Experiment>
        <Experiment>route_adjust</Experiment>
        <Experiment>route_adjust_eta</Experiment>
        <Experiment>address_change_logging</Experiment>
        <Experiment>user_position_enabled</Experiment>
        <Experiment>light_fixprice_to_airport</Experiment>
        <Experiment>direct_assignment</Experiment>
    </Experiments>
    <FixedPrice max_distance=""500"" show_price=""yes"" enabled=""yes"">139</FixedPrice>
    <HiddenDiscount enabled=""yes""/>
    <Translations>
        <Translation key=""key1"">value1</Translation>
    </Translations>
    <Reposition mode=""name""/>
    <ClientGeoSharing enabled=""yes"" track_id=""tr_id""/>
</Request>"

            #endregion

            );
            var item = _setCarParser.ParseSetCarBase(xml, Provider.Яндекс);
            item.id.Should().BeEquivalentTo("faaa8333b9f849e284b718b717ad8ca2");
            item.driver_id.Should().BeEquivalentTo("2013ed180de6480db22ac88dc118571f");
            item.clid.Should().BeEquivalentTo("1956794047");
            item.experiments.Should().NotBeEmpty();
            item.description.Should().BeEquivalentTo("Тестовый заказ");
            item.OrderSource.Should().Be("uber");
            item.Translations["key1"].Should().Be("value1");
            item.Reposition.Should().Be(true);
            item.Logistic.Shift.Id.Should().Be("id");

            //TODO: более глубокий парсинг сеткара после рефакторинга domainhelper и прочего
        }

        [Fact]
        public void ParseYandexCategory()
        {
            var xml = XElement.Parse(
                @"<Request direct_assignment=""yes"">
                    <Cars>
                        <Car>
                            <Category>econom</Category>
                            <CategoryLocalized>Эконом</CategoryLocalized>
                        </Car>
                    </Cars>
                </Request>"
            );

            var item = new SetCarItem();
            _setCarParser.ParseYandexCategory(item, xml);

            item.category.Should().Be(CategoryFlags.Econom);
            item.CategoryLocalized.Should().Be("Эконом");
        }

        [Fact]
        public void ParseEmbeddedOrderTest()
        {
            var xml = XElement.Parse(

                #region SetCar xml

                @"<RequestedOrder id=""faaa8333b9f849e284b718b717ad8ca2"">
    <BookingTime type=""notlater"">2017-06-07T00:12:00+0300</BookingTime>
    <Requirements>
        <Require name=""creditcard"">yes</Require>
    </Requirements>
    <PaymentMethod type=""card""/>
    <Comments>Тестовый заказ</Comments>
    <FixedPrice max_distance=""500"" show_price=""yes"" enabled=""yes"">139</FixedPrice>
    <Passengers count=""2""/>
    <ShowCostPlate enabled=""yes""></ShowCostPlate>
    <Experiments>
        <Experiment>experiment_1</Experiment>
    </Experiments>
    <DriverExperiments>
        <Experiment>experiment_2</Experiment>
    </DriverExperiments>
    <Assigning type=""auto"" changed_pickups_order=""yes"" changed_pickups_order_show_ms=""12000""/>
    <ClientGeoSharing enabled=""yes"" track_id=""tr_id""/>
</RequestedOrder>"

                #endregion

            );
            var item = _setCarParser.ParseEmbeddedOrder(xml, OrderStatus.none,
                null, CultureInfo.InvariantCulture);
            item.id.Should().BeEquivalentTo("faaa8333b9f849e284b718b717ad8ca2");
            item.pay_type.Should().Be(OrderPayType.Безналичные);
            item.description.Should().BeEquivalentTo("Тестовый заказ");
            item.FixedPrice.Price.Should().Be(139);
            item.passager_count.Should().Be(2);
            item.ShowCostPlate.Should().BeTrue();
            item.experiments.Should().BeEquivalentTo("experiment_1");
            item.DriverExperiments.Should().BeEquivalentTo("experiment_2");
            item.ClientGeoSharingSettings.IsEnabled.Should().BeTrue();
            CustomAssert.PropertiesEqual(item.Assigning, new EmbeddedOrderAssigningSettings
            {
                ChangedPickupOrder = true,
                Type = EmbeddedOrderAssigningSettings.AssigningType.Auto,
                ChangedPickupOrderShowMs = 12000
            });
        }

        [Fact]
        public void ParseSubventions()
        {
            var element = XElement.Parse(@"<SetCar><Subvention>
    <Rules>
        <Rule>
            <Type>guarantee</Type>
            <Params>
                <Param name=""sum"" value=""140.0""/>
            </Params>
        </Rule>
    </Rules>
    <DisabledRules>
        <Rule>
            <Type>guarantee</Type>
            <Params>
                <Param name=""sum"" value=""140.0""/>
            </Params>
            <DeclineReasons>
                <DeclineReason reason=""too_low_value"" minimum=""78"" key=""ride_count"" value=""0""/>
            </DeclineReasons>
        </Rule>
    </DisabledRules>
    <Combine>max</Combine>
</Subvention></SetCar>");
            var result = _setCarParser.ParseSubventions(element);
            result.Should().NotBeNull();

            result.Rules.Length.Should().Be(1);
            result.Rules[0].Type.Should().BeEquivalentTo("guarantee");
            result.Rules[0].Sum.Should().Be(140.0m);

            result.DisabledRules.Length.Should().Be(1);
            result.DisabledRules[0].Type.Should().BeEquivalentTo("guarantee");
            result.DisabledRules[0].Sum.Should().Be(140.0m);
            result.DisabledRules[0].DeclineReasons.Length.Should().Be(1);
            result.DisabledRules[0].DeclineReasons[0].Should().Be(
                new SubventionDeclineReason {Key = "ride_count", Reason = "too_low_value"});
            result.DisabledRules[0].DeclineReasons[0].Parameters.Should().ContainKey("minimum");
            result.DisabledRules[0].DeclineReasons[0].Parameters.Should().ContainKey("value");

            var clientSubvention = result.ToClientSubvention(CultureInfo.CurrentCulture);
            clientSubvention.Should().NotBeNull();
            clientSubvention.Rules.Length.Should().Be(1);
            clientSubvention.DisabledRules.Length.Should().Be(1);
        }

        [Fact]
        public void ParseTranslations_ElementDoesNotExist_ReturnsNull()
        {
            _setCarParser.ParseTranslations(null).Should().BeNull();
        }

        [Fact]
        public void ParseTranslations_ElementHasTranslations_ReturnsDictionary()
        {
            var xml = XElement.Parse(@"
<Translations>
    <Translation key=""key1"">value1</Translation>
    <Translation key=""key2"">value2</Translation>
</Translations>");

            var result = _setCarParser.ParseTranslations(xml);

            result.Count.Should().Be(2);
            result["key1"].Should().Be("value1");
            result["key2"].Should().Be("value2");
        }

        [Fact]
        public void ParseRouteInfo_NullElement_ReturnsEmpty()
        {
            var routeInfo = _setCarParser.ParseRouteInfo(null);

            routeInfo.Equals(new RouteInfo()).Should().BeTrue();
        }

        [Fact]
        public void ParseRouteInfo_EmptyElement_ReturnsEmpty()
        {
            var xml = XElement.Parse("<RouteInfo></RouteInfo>");

            var routeInfo = _setCarParser.ParseRouteInfo(xml);

            routeInfo.Equals(new RouteInfo()).Should().BeTrue();
        }

        [Fact]
        public void ParseRouteInfo_PartiallyFilledElement_ReturnsPartiallyFilledInfo()
        {
            var xml = XElement.Parse(@"
<RouteInfo>
    <RouterTime>3600.5</RouterTime>
</RouteInfo>");

            var routeInfo = _setCarParser.ParseRouteInfo(xml);
            routeInfo.Time.Should().BeCloseTo(DateTime.UtcNow + TimeSpan.FromSeconds(3600.5), 500);
            routeInfo.Distance.Should().BeNull();
            routeInfo.Points.Should().BeNull();
        }

        [Fact]
        public void ParseRouteInfo_FullElement_ReturnsFullInfo()
        {
            var xml = XElement.Parse(@"
<RouteInfo>
    <Point><Lon>37</Lon><Lat>55</Lat></Point>
    <Point><Lon>38</Lon><Lat>56</Lat></Point>
    <RouterDistance>543.33</RouterDistance>
    <PrepaidMinutes>50</PrepaidMinutes>
    <PrepaidDistance>50</PrepaidDistance>
    <RouterTime>3600.5</RouterTime>
</RouteInfo>");

            var routeInfo = _setCarParser.ParseRouteInfo(xml);

            routeInfo.Time.Should().BeCloseTo(DateTime.UtcNow + TimeSpan.FromSeconds(3600.5), 500);
            routeInfo.Distance.Should().Be(543.33);
            routeInfo.Points
                .SequenceEqual(new[] {new GeoPoint(37, 55), new GeoPoint(38, 56)})
                .Should().BeTrue();
            routeInfo.PrepaidMinutes.Should().Be(50);
            routeInfo.PrepaidDistance.Should().Be(50);
        }

        [Fact]
        public void ParseRouteInfo_DistanceTypeOnlyElement_ReturnsDistanceType()
        {
            var xml = XElement.Parse(@"
<RouteInfo>
    <RouterDistance distance_type=""short""/>
</RouteInfo>");

            var routeInfo = _setCarParser.ParseRouteInfo(xml);
            routeInfo.Distance.Should().BeNull();
            routeInfo.DistanceType.Should().Be("short");
        }

        [Fact]
        public void ParseRouteInfo_FinalDestination()
        {
            var xml = XElement.Parse(@"
<RouteInfo>
    <FinalDestinationDistance>143.22</FinalDestinationDistance>
    <FinalDestinationTime>3600.5</FinalDestinationTime>
    <IsLongOrder>yes</IsLongOrder>
</RouteInfo>");

            var routeInfo = _setCarParser.ParseRouteInfo(xml);

            routeInfo.FinalDestinationTime.Should().BeCloseTo(DateTime.UtcNow + TimeSpan.FromSeconds(3600.5), 500);
            routeInfo.FinalDestinationDistance.Should().Be(143.22);
            routeInfo.IsLongOrder.Should().BeTrue();
        }

        [Fact]
        public void ParseRouteInfo_FinalDestination_Missing()
        {
            var xml = XElement.Parse(@"
<RouteInfo>
</RouteInfo>");

            var routeInfo = _setCarParser.ParseRouteInfo(xml);

            routeInfo.FinalDestinationTime.Should().BeNull();
            routeInfo.FinalDestinationDistance.Should().BeNull();
            routeInfo.IsLongOrder.Should().BeNull();
        }

        [Fact]
        public void RequirementCollectionTest_Simple()
        {
            var requirements = new RequirementCollection {OrderRequirements.card, OrderRequirements.coupon};

            requirements.Count.Should().Be(2);
            requirements["card"].Should().NotBeNull();
            requirements["card"].Amount.Should().BeNull();
            requirements["coupon"].Should().NotBeNull();
            requirements["coupon"].Amount.Should().BeNull();
            requirements["chuild_chair"].Should().BeNull();
            requirements.Flags.Should().Be(OrderRequirements.card | OrderRequirements.coupon);
        }

        [Fact]
        public void RequirementCollectionTest_DuplicateAmount_Sum()
        {
            var requirements = new RequirementCollection();
            requirements.Add(OrderRequirements.card);
            requirements.Add(OrderRequirements.child_chair);
            requirements.Add(OrderRequirements.child_chair, 1);
            requirements.Add(OrderRequirements.child_chair, 2);

            requirements.Count.Should().Be(2);
            requirements["card"].Should().NotBeNull();
            requirements["card"].Amount.Should().BeNull();
            requirements["child_chair"].Should().NotBeNull();
            requirements["child_chair"].Amount.Should().Be(3);

            requirements.Flags.Should().Be(OrderRequirements.card | OrderRequirements.child_chair);
        }

        [Fact]
        public void RequirementCollectionTest_AddRemove_Flags()
        {
            var requirements = new RequirementCollection();
            requirements.Add(OrderRequirements.card);
            requirements.Add(OrderRequirements.child_chair, 1);
            requirements.Add(OrderRequirements.child_chair, 2);
            requirements.Remove(OrderRequirements.child_chair);
            requirements.Remove(OrderRequirements.animal_transport);
            requirements.Add(OrderRequirements.coupon);

            requirements.Count.Should().Be(2);
            requirements["card"].Should().NotBeNull();
            requirements["coupon"].Should().NotBeNull();

            requirements.Flags.Should().Be(OrderRequirements.card | OrderRequirements.coupon);
        }

        [Fact]
        public void ParseClientGeoSharingSettings_Disabled()
        {
            var xml = XElement.Parse(@"<Order><ClientGeoSharing enabled=""no""/></Order>");
            var settings = _setCarParser.ParseClientGeoSharingSettings(xml);
            settings.IsEnabled.Should().Be(false);
            settings.TrackId.Should().BeNull();
        }

        [Fact]
        public void ParseClientGeoSharingSettings_Enabled()
        {
            var xml = XElement.Parse(@"<Order><ClientGeoSharing enabled=""yes"" track_id=""tr_id""/></Order>");
            var settings = _setCarParser.ParseClientGeoSharingSettings(xml);
            settings.IsEnabled.Should().Be(true);
            settings.TrackId.Should().Be("tr_id");
        }

        [Fact]
        public void ParseSetCarTariffsV2()
        {
            var xml = XElement.Parse(@"
<Request xmlns:xsi=""http://www.w3.org/2001/XMLSchema-instance"">
<PricingData>
    <Driver>
        <CategoryPricesId>price1</CategoryPricesId>
        <GeoareaId>geo1</GeoareaId>
        <GeoareaId>geo2</GeoareaId>
    </Driver>
    <User>
        <CategoryPricesId>price2</CategoryPricesId>
        <GeoareaId>geo3</GeoareaId>
        <GeoareaId>geo4</GeoareaId>
    </User>
</PricingData>
</Request>");

            var expected =
                "{\"driver\":{" +
                    "\"category_prices_id\":\"price1\"," +
                    "\"geoareas\":[\"geo1\",\"geo2\"]}," +
                "\"user\":{" +
                    "\"category_prices_id\":\"price2\"," +
                    "\"geoareas\":[\"geo3\",\"geo4\"]}}";

            var parsed = _setCarParser.ParseTariffsV2(xml);
            var setcarJson = JsonConvert.SerializeObject(parsed);
            setcarJson.Should().BeEquivalentTo(expected);
        }

        [Fact]
        public void ParseSetCarUi()
        {
            var xml = XElement.Parse(
                "<Request xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">" +
                    "<AcceptanceItems>" +
                        "<Item xsi:type=\"Default\">" +
                            "<HorizontalDividerType>Full</HorizontalDividerType>" +
                            "<Title>200 \u043c * 3 \u043c\u0438\u043d</Title>" +
                            "<Subtitle>short</Subtitle>" +
                        "</Item>" +
                        "<Item xsi:type=\"DoubleSection\">" +
                            "<HorizontalDividerType>Full</HorizontalDividerType>" +
                            "<VerticalDividerType>Full</VerticalDividerType>" +
                            "<Left xsi:type=\"IconDetail\">" +
                                "<HorizontalDividerType>Full</HorizontalDividerType>" +
                                "<Reverse>true</Reverse>" +
                                "<Title>2</Title>" +
                                "<Subtitle>Activity</Subtitle>" +
                            "</Left>" +
                            "<Right xsi:type=\"IconDetail\">" +
                                "<HorizontalDividerType>Full</HorizontalDividerType>" +
                                "<Reverse>true</Reverse>" +
                                "<Title>x1</Title>" +
                                "<Subtitle>Cost</Subtitle>" +
                            "</Right>" +
                        "</Item>" +
                        "<Item xsi:type=\"Default\">" +
                            "<HorizontalDividerType>Full</HorizontalDividerType>" +
                            "<Reverse>true</Reverse>" +
                            "<Title>Leo Tolstoy 16</Title>" +
                            "<Subtitle>From</Subtitle>" +
                        "</Item>" +
                        "<Item xsi:type=\"Default\">" +
                            "<ItemId>comment</ItemId>" +
                            "<HorizontalDividerType>Full</HorizontalDividerType>" +
                            "<Reverse>true</Reverse>" +
                            "<Title>ski, creditcard</Title>" +
                            "<Subtitle>Comment</Subtitle>" +
                        "</Item>" +
                    "</AcceptanceItems>" +
                "</Request>");
            var ui = _setCarParser.ParseUi(xml);
            ui?.AcceptanceItems.Should().NotBeNull();
            ui.AcceptanceItems.Length.Should().Be(4);

            ui.AcceptanceItems[0].Should().BeOfType<DriverDashboardDefaultItem>().Which.Title.Should()
                .Be("200 \u043c * 3 \u043c\u0438\u043d");

            var doubleSectionItem = ui.AcceptanceItems[1].Should().BeOfType<DriverDashboardDoubleSectionItem>().Which;
            doubleSectionItem.Left.Should().BeOfType<DriverDashboardIconDetailItem>().Which.Title.Should().Be("2");
            doubleSectionItem.Right.Should().BeOfType<DriverDashboardIconDetailItem>().Which.Title.Should().Be("x1");

            ui.AcceptanceItems[2].Should().BeOfType<DriverDashboardDefaultItem>().Which.Title.Should()
                .Be("Leo Tolstoy 16");

            ui.AcceptanceItems[3].Should().BeOfType<DriverDashboardDefaultItem>().Which.Title.Should()
                .Be("ski, creditcard");
        }

        [Fact]
        public void ParseSetCarUi_ItemId()
        {
            var xml = XElement.Parse(
                @"<Request xmlns:xsi=""http://www.w3.org/2001/XMLSchema-instance"">
    <AcceptanceItems>
        <Item xsi:type=""Default"">
            <HorizontalDividerType>Full</HorizontalDividerType>
            <Reverse>true</Reverse>
            <Title>Leo Tolstoy 16</Title>
            <Subtitle>From</Subtitle>
        </Item>
        <Item xsi:type=""Default"">
            <ItemId>comment</ItemId>
            <HorizontalDividerType>Full</HorizontalDividerType>
            <Reverse>true</Reverse>
            <Title>ski, creditcard</Title>
            <Subtitle>Comment</Subtitle>
        </Item>
    </AcceptanceItems>
</Request>");
            var ui = _setCarParser.ParseUi(xml);

            JsonConvert.SerializeObject(ui.AcceptanceItems).Should().BeEquivalentTo(
                "[" +
                    "{" +
                        "\"type\":\"default\"," +
                        "\"title\":\"Leo Tolstoy 16\"," +
                        "\"subtitle\":\"From\"," +
                        "\"reverse\":true," +
                        "\"horizontal_divider_type\":\"full\"" +
                    "},{" +
                        "\"type\":\"default\"," +
                        "\"title\":\"ski, creditcard\"," +
                        "\"subtitle\":\"Comment\"," +
                        "\"reverse\":true," +
                        "\"item_id\":\"comment\"," +
                        "\"horizontal_divider_type\":\"full\"" +
                    "}" +
                "]");
        }

        [Fact]
        public void ParseSetCarUiOfferParams()
        {
            var xml = XElement.Parse(
                @"<Request xmlns:xsi=""http://www.w3.org/2001/XMLSchema-instance"">
<OfferParams>
  <Title>isr_offer_button_title</Title>
  <Payload>
    <Title>isr_offer_screen_title</Title>
    <Tag>offer</Tag>
    <Type>constructor</Type>
    <Items>
      <Item xsi:type=""Default"">
        <HorizontalDividerType>Full</HorizontalDividerType>
        <RightIcon>Navigate</RightIcon>
        <Payload>
          <Title>isr_offer_document_button</Title>
          <Url>isr_offer_document_url</Url>
          <IsExternal>true</IsExternal>
          <Type>NavigateUrl</Type>
        </Payload>
        <Title>isr_offer_document_button</Title>
        <PrimaryMaxLines>1</PrimaryMaxLines>
        <SecondaryMaxLines>1</SecondaryMaxLines>
      </Item>
      <Item xsi:type=""Title"">
        <HorizontalDividerType>Full</HorizontalDividerType>
        <Title>isr_offer_order_details</Title>
      </Item>
      <Item xsi:type=""Default"">
        <HorizontalDividerType>Full</HorizontalDividerType>
        <Title>isr_offer_date</Title>
        <Subtitle>02.03</Subtitle>
        <PrimaryMaxLines>1</PrimaryMaxLines>
        <SecondaryMaxLines>1</SecondaryMaxLines>
      </Item>
      <Item xsi:type=""Default"">
        <HorizontalDividerType>Full</HorizontalDividerType>
        <Title>isr_offer_order_from</Title>
        <Subtitle>Leo Tolstoy 16</Subtitle>
        <PrimaryMaxLines>1</PrimaryMaxLines>
        <SecondaryMaxLines>3</SecondaryMaxLines>
      </Item>
      <Item xsi:type=""Default"">
        <HorizontalDividerType>Full</HorizontalDividerType>
        <Title>isr_offer_order_to</Title>
        <Subtitle>Israel, Vnukovo</Subtitle>
        <PrimaryMaxLines>1</PrimaryMaxLines>
        <SecondaryMaxLines>3</SecondaryMaxLines>
      </Item>
      <Item xsi:type=""Default"">
        <HorizontalDividerType>Full</HorizontalDividerType>
        <Title>isr_offer_price</Title>
        <Subtitle>432&#8381;</Subtitle>
        <PrimaryMaxLines>1</PrimaryMaxLines>
        <SecondaryMaxLines>1</SecondaryMaxLines>
      </Item>
      <Item xsi:type=""Default"">
        <HorizontalDividerType>Full</HorizontalDividerType>
        <Title>isr_offer_park</Title>
        <Subtitle>Lesch Ltd.</Subtitle>
        <PrimaryMaxLines>1</PrimaryMaxLines>
        <SecondaryMaxLines>1</SecondaryMaxLines>
      </Item>
      <Item xsi:type=""Default"">
        <HorizontalDividerType>Full</HorizontalDividerType>
        <Title>isr_offer_client_phone</Title>
        <Subtitle>+71111111111</Subtitle>
        <PrimaryMaxLines>1</PrimaryMaxLines>
        <SecondaryMaxLines>1</SecondaryMaxLines>
      </Item>
    </Items>
  </Payload>
</OfferParams></Request>");
            var ui = _setCarParser.ParseUi(xml);
            ui?.OfferParams.Should().NotBeNull();

            var expected = @"{
                  ""title"": ""isr_offer_button_title"",
                  ""payload"": {
                    ""tag"": ""offer"",
                    ""type"": ""constructor"",
                    ""title"": ""isr_offer_screen_title"",
                    ""items"": [
                      {
                        ""type"": ""default"",
                        ""title"": ""isr_offer_document_button"",
                        ""right_icon"": ""navigate"",
                        ""primary_max_lines"": 1,
                        ""secondary_max_lines"": 1,
                        ""payload"": {
                          ""type"": ""navigate_url"",
                          ""title"": ""isr_offer_document_button"",
                          ""url"": ""isr_offer_document_url"",
                          ""is_external"": ""true""
                        },
                        ""horizontal_divider_type"": ""full""
                      },
                      {
                        ""type"": ""title"",
                        ""title"": ""isr_offer_order_details"",
                        ""horizontal_divider_type"": ""full""
                      },
                      {
                        ""type"": ""default"",
                        ""title"": ""isr_offer_date"",
                        ""subtitle"": ""02.03"",
                        ""primary_max_lines"": 1,
                        ""secondary_max_lines"": 1,
                        ""horizontal_divider_type"": ""full""
                      },
                      {
                        ""type"": ""default"",
                        ""title"": ""isr_offer_order_from"",
                        ""subtitle"": ""Leo Tolstoy 16"",
                        ""primary_max_lines"": 1,
                        ""secondary_max_lines"": 3,
                        ""horizontal_divider_type"": ""full""
                      },
                      {
                        ""type"": ""default"",
                        ""title"": ""isr_offer_order_to"",
                        ""subtitle"": ""Israel, Vnukovo"",
                        ""primary_max_lines"": 1,
                        ""secondary_max_lines"": 3,
                        ""horizontal_divider_type"": ""full""
                      },
                      {
                        ""type"": ""default"",
                        ""title"": ""isr_offer_price"",
                        ""subtitle"": ""432₽"",
                        ""primary_max_lines"": 1,
                        ""secondary_max_lines"": 1,
                        ""horizontal_divider_type"": ""full""
                      },
                      {
                        ""type"": ""default"",
                        ""title"": ""isr_offer_park"",
                        ""subtitle"": ""Lesch Ltd."",
                        ""primary_max_lines"": 1,
                        ""secondary_max_lines"": 1,
                        ""horizontal_divider_type"": ""full""
                      },
                      {
                        ""type"": ""default"",
                        ""title"": ""isr_offer_client_phone"",
                        ""subtitle"": ""+71111111111"",
                        ""primary_max_lines"": 1,
                        ""secondary_max_lines"": 1,
                        ""horizontal_divider_type"": ""full""
                      }
                    ]
                  }
                }";
            var expectedJson = JsonConvert.DeserializeObject(expected);
            JsonConvert.SerializeObject(ui.OfferParams).Should().BeEquivalentTo(
                JsonConvert.SerializeObject(expectedJson));
        }
    }
}
