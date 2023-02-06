using System.IO;
using FluentAssertions;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Xunit;
using Yandex.Taximeter.Core.Utils;

public class JsonDiffTest
{
    [Fact]
    public void Test1()
    {
        var json1 = @"{
            'array': ['one', 'two', 'three']
        }";
        var json2 = @"{
            'array': ['two', 'three', 'one', 'four']
        }";
        var result = JsonUtils.CompareJson(JObject.Parse(json1), JObject.Parse(json2));
        result.Item3.Should().BeTrue();
    }
    
    [Fact]
    public void Test2()
    {
        var json1 = @"{
            'hello': 'world',
            'iam': 'muffin',
            'pew': {
                'pew' : 123,
                'tram': 234
            }
        }";
        var json2 = @"{
            'iam': 'muffin',
            'pew': {
                'tram': 234
            }
        }";
        var result = JsonUtils.CompareJson(JObject.Parse(json1), JObject.Parse(json2));
        result.Item1.ToString().Should().Be("hello; pew.pew; ");
        result.Item3.Should().BeFalse();
    }
    
    [Fact]
    public void Test3()
    {
        var json1 = @"{
            'obj_array': [
                {
                    'filed1': 'val1'
                },
                {
                    'field2': 'val2'
                }
            ]
        }";
        var json2 = @"{
            'obj_array': [
                {
                    'filed1': 'val1'
                },
                {
                    'field2': 'val2'
                }
            ]
        }";
        var result = JsonUtils.CompareJson(JObject.Parse(json1), JObject.Parse(json2));
        result.Item1.ToString().Should().Be("");
        result.Item2.ToString().Should().Be("");
        result.Item3.Should().BeTrue();
    }
    
    [Fact]
    public void Test4()
    {
        var json1 = @"{
            'params': {
                'arr': ['one', 'two', 'three', 'five']
             }
        }";
        var json2 = @"{
            'params': {
                'arr': ['two', 'one', 'four']
            }
        }";
        var result = JsonUtils.CompareJson(JObject.Parse(json1), JObject.Parse(json2));
        result.Item1.ToString().Should().Be("params.arr: three, five; ");
        result.Item3.Should().BeFalse();
    }

    
    [Fact]
    public void Test5()
    {
        var json1 = @"{
            'obj1': {
                'arr1': ['one', 'two']
             },
            'obj2': {
                'field1': 'val1',
                'field2': 'val2'
            }
        }";
        var json2 = @"{
            'obj1': {
                'arr1': ['two', 'one', 'four']
            },
            'obj2': {
                'field2': 'val4'
            }
        }";
        var result = JsonUtils.CompareJson(JObject.Parse(json1), JObject.Parse(json2));
        result.Item1.ToString().Should().Be("obj2.field1; ");
        result.Item2.ToString().Should().Be("obj2.field2 is val4 expected val2; ");
        result.Item3.Should().BeFalse();
    }
    
    [Fact]
    public void Test6()
    {
        var json1 = @"{
            'session': 'sdfnvdfv',
            'token': 'dfvsdfvsdfvsd'
        }";
        var json2 = @"{
            'session': 'qwirfqewf892',
            'token': '23gebahjsxc982'
        }";
        var result = JsonUtils.CompareJson(JObject.Parse(json1), JObject.Parse(json2));
        result.Item2.ToString().Should().Be("session; token; ");
        result.Item3.Should().BeFalse();
    }
    
}
