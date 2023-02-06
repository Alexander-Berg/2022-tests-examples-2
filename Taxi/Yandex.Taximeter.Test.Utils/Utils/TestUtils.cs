using System;
using System.Globalization;
using System.Xml;
using FluentAssertions;
using Newtonsoft.Json;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Services.Driver;
using Formatting = Newtonsoft.Json.Formatting;

namespace Yandex.Taximeter.Test.Utils.Utils
{
    public static class TestUtils
    {
        public static string NewId() => Guid.NewGuid().ToString();

        public static DriverId NewDriverId() => new DriverId(NewId(), NewId());

        public static string NewEmail() => NewId() + "@yandex-fake.ru";

        public static DateTime Yesterday(string time) =>
            DateTime.Today.AddDays(-1) + TimeSpan.ParseExact(time, "hh\\:mm", CultureInfo.InvariantCulture);

        public static void CheckXmlSerialization<T>(string expectedXml, T obj)
        {
            var doc = new XmlDocument();
            doc.LoadXml(expectedXml);
            expectedXml = doc.OuterXml;
            var actualXml = StaticHelper.ToXml(obj);
            actualXml.Should().BeEquivalentTo(expectedXml);
        }

        public static void CheckJsonSerialization<T>(string expectedJson, T obj)
        {
            var jObj = JsonConvert.DeserializeObject(expectedJson, StaticHelper.JsonSerializerSettings);
            expectedJson = JsonConvert.SerializeObject(jObj, Formatting.None, StaticHelper.JsonSerializerSettings);

            var actualJson = JsonConvert.SerializeObject(obj, Formatting.None, StaticHelper.JsonSerializerSettings);

            actualJson.Should().BeEquivalentTo(expectedJson);
        }

        public static void CheckJsonSerialization<T>(T obj, params JsonConverter[] converters)
        {
            var serialized = JsonConvert.SerializeObject(obj, converters);
            var deserialized = JsonConvert.DeserializeObject<T>(serialized, converters);
            CustomAssert.PropertiesEqual(obj, deserialized);
        }
    }
}