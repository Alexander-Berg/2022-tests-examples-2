using System;
using FluentAssertions;
using MongoDB.Bson.Serialization.Attributes;
using Newtonsoft.Json;

namespace Yandex.Taximeter.Test.Utils.Utils
{
    public static class TypeExtensions
    {
        public static void CheckJsonAttributeIsNotForgotten(this Type type)
        {
            foreach (var property in type.GetProperties())
            {
                var hasJsonPropertyAttribute = Attribute.IsDefined(property, typeof(JsonPropertyAttribute));
                var hasJsonIgnoreAttribute = Attribute.IsDefined(property, typeof(JsonIgnoreAttribute));

                var hasBsonAttribute = Attribute.IsDefined(property, typeof(BsonElementAttribute));
                var hasBsonId = Attribute.IsDefined(property, typeof(BsonIdAttribute));
                var hasBsonIgnoreAttribute = Attribute.IsDefined(property, typeof(BsonIgnoreAttribute));

                (hasJsonPropertyAttribute | hasJsonIgnoreAttribute).Should().Be(
                    hasBsonAttribute | hasBsonId | hasBsonIgnoreAttribute,
                    $"Property {type.Name}::{property.Name} has BsonElement, or BsonId, or BsonIgnore attribute" +
                    " but does not have JsonProperty nor JsonIgnore attribute or vice versa");

                if (hasJsonPropertyAttribute || hasBsonAttribute)
                    property.PropertyType.CheckJsonAttributeIsNotForgotten();
            }
        }
    }
}
