using System;
using FluentAssertions;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Xunit;
using Yandex.Taximeter.Core.Helper;

public class JsonSerializerTests
{
    [Fact]
    public void TestDateSerialization()
    {
        var obj = new
        {
            date = new DateTime(636537722389904334)
        };
        var json = JsonConvert.SerializeObject(obj, StaticHelper.JsonSerializerSettings);
        json.Should().Be(@"{""date"":""2018-02-09T11:23:58.990433Z""}");
    }    
}