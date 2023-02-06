using Xunit;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Driver;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Models.Driver
{
    public class DriverDocAttributeTest
    {
        [Fact]
        public void JsonAttributesEqualBson_DriverDoc()
        {
            typeof(DriverDoc).CheckJsonAttributeIsNotForgotten();
        }
    }
}
