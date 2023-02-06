using System.Runtime.Serialization;
using FluentAssertions;
using Newtonsoft.Json;
using Xunit;
using Yandex.Taximeter.Core.Services.QualityControl;

namespace Yandex.Taximeter.Common.Tests.Services.JsonConverters
{
    public class QcStatusResultJsonConverterTests
    {
        [DataContract]
        private class TestData
        {
            [DataMember(Name="result")]
            [JsonConverter(typeof(QcStatusResultConverter))]
            public QcStatusResult Result { get; set; }
        }

        [Theory]
        [InlineData(QcStatusResult.Success, "{\"result\":\"success\"}")]
        [InlineData(QcStatusResult.Blacklist, "{\"result\":\"blacklist\"}")]
        [InlineData(QcStatusResult.TempBlock, "{\"result\":\"block\"}")]
        public void TestSerialize(QcStatusResult result, string expectedData)
        {
            var actualResult = JsonConvert.SerializeObject(new TestData {Result = result});
            actualResult.Should().Be(expectedData);
        }
        
        [Theory]
        [InlineData(QcStatusResult.Success, "{\"result\":\"success\"}")]
        [InlineData(QcStatusResult.Success, "{\"result\":\"ok\"}")]
        [InlineData(QcStatusResult.Blacklist, "{\"result\":\"blacklist\"}")]
        [InlineData(QcStatusResult.TempBlock, "{\"result\":\"block\"}")]
        public void TestDeSerialize(QcStatusResult expectedResult, string data)
        {
            var actualResult = JsonConvert.DeserializeObject<TestData>(data);
            actualResult.Result.Should().Be(expectedResult);
        }
    }
}
