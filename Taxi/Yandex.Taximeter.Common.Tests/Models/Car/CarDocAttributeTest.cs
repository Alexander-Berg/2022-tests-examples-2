using Xunit;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Car;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Models.Car
{
    public class CarDocAttributeTest
    {
        [Fact]
        public void JsonAttributesEqualBson_CarDoc()
        {
            typeof(CarDoc).CheckJsonAttributeIsNotForgotten();
        }
    }
}
