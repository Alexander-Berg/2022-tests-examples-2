using FluentAssertions;
using Newtonsoft.Json;

namespace Yandex.Taximeter.Test.Utils.Utils
{
    public static class CustomAssert
    {
        public static void PropertiesEqual<T>(T expected, T actual)
        {
            var serializerSettings = new JsonSerializerSettings
            {
                DefaultValueHandling = DefaultValueHandling.Ignore,
                NullValueHandling = NullValueHandling.Ignore,
                Formatting = Formatting.Indented
            };
            var expectedSerialiezed = JsonConvert.SerializeObject(expected, serializerSettings);
            var actualSerialized = JsonConvert.SerializeObject(actual, serializerSettings);
            actualSerialized.Should().Be(expectedSerialiezed);
        }
    }
}
