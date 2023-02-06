using FluentAssertions;
using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;
using Xunit;
using Yandex.Taximeter.Core.Extensions;

namespace Yandex.Taximeter.Common.Tests.Extensions
{
    public class MongoExtensionTests
    {
        #region Classes
        [BsonIgnoreExtraElements]
        private class TestDoc
        {
            [BsonElement("string")]
            public string StringField { get; set; }

            [BsonElement("int")]
            public int IntField { get; set; }

            [BsonElement("bool")]
            public bool BooleanField { get; set; }
            
            [BsonElement("nested")]
            public TestNestedDoc NestedField { get; set; }
        }

        [BsonIgnoreExtraElements]
        private class TestDoc2 : TestDoc
        {
            [BsonElement("data")]
            public string DataField { get; set; }
        }

        [BsonIgnoreExtraElements]
        private class TestNestedDoc
        {
            [BsonElement("value")]
            public string Value { get; set; }
            
            [BsonElement("enabled")]
            public bool Enabled { get; set; }
        }


        [BsonIgnoreExtraElements]
        private class TestDto1
        {
            [BsonElement("string")]
            public string StringField { get; set; }

            [BsonElement("int")]
            public int IntField { get; set; }
        }
        
        [BsonIgnoreExtraElements]
        private class TestNestedDto
        {
            [BsonElement("enabled")]
            public bool Enabled { get; set; }
        }
        
        [BsonIgnoreExtraElements]
        private class TestDto2
        {
            [BsonElement("string")]
            public string StringField { get; set; }

            [BsonElement("int")]
            public int IntField { get; set; }
            
            [BsonElement("nested")]
            public TestNestedDto NestedField { get; set; }
        }
        
        [BsonIgnoreExtraElements]
        private class TestDto3
        {
            [BsonElement("string")]
            public string StringField { get; set; }

            [BsonElement("int")]
            public long LongField { get; set; }
        }
        #endregion

        [Fact]
        public void TestServerProjection_Simple()
        {
            var projection = MongoExtensions.BuildServerProjectionBson<TestDoc, TestDoc>();
            projection.Should().BeNull();

            projection = MongoExtensions.BuildServerProjectionBson<TestDoc, TestDoc2>();
            projection.Should().BeNull();
        }
        
        [Fact]
        public void TestServerProjection_Subset()
        {
            var projection = MongoExtensions.BuildServerProjectionBson<TestDoc, TestDto1>();
            projection.Should().NotBeNull();
            projection.Should().BeEquivalentTo(new BsonDocument()
            {
                ["string"] = 1,
                ["int"] = 1
            });
        }
        
        [Fact]
        public void TestServerProjection_OtherType()
        {
            var projection = MongoExtensions.BuildServerProjectionBson<TestDoc, TestDto3>();
            projection.Should().NotBeNull();
            projection.Should().BeEquivalentTo(new BsonDocument()
            {
                ["string"] = 1,
                ["int"] = 1
            });
        }
        
        [Fact]
        public void TestServerProjection_Superset()
        {
            var projection = MongoExtensions.BuildServerProjectionBson<TestDoc2, TestDoc>();
            projection.Should().NotBeNull();
            projection.Should().BeEquivalentTo(new BsonDocument()
            {
                ["string"] = 1,
                ["int"] = 1,
                ["bool"] = 1,
                ["nested"] = 1
            });
        }
        
        [Fact]
        public void TestServerProjection_Nested_Subset()
        {
            var projection = MongoExtensions.BuildServerProjectionBson<TestDoc, TestDto2>();
            projection.Should().NotBeNull();
            projection.Should().BeEquivalentTo(new BsonDocument()
            {
                ["string"] = 1,
                ["int"] = 1,
                ["nested.enabled"] = 1
            });
        }
    }
}