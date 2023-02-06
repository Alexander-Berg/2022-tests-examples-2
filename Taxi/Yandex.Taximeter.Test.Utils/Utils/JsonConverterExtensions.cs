using System.IO;
using Newtonsoft.Json;

namespace Yandex.Taximeter.Test.Utils.Utils
{
    public static class JsonConverterExtensions
    {
        public static object ReadJson(this JsonConverter converter, string json)
        {
            using (var textReader = new StringReader(json))
            using (var reader = new JsonTextReader(textReader))
            {
                reader.Read();
                return converter.ReadJson(reader, typeof(int), null, new JsonSerializer());
            }
        }

        public static string WriteJson(this JsonConverter converter, object obj)
        {
            using (var textWriter = new StringWriter())
            using (var writer = new JsonTextWriter(textWriter))
            {
                converter.WriteJson(writer, obj, new JsonSerializer());
                writer.Flush();
                return textWriter.ToString();
            }
        }
    }
}