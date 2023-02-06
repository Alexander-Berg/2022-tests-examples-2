using System;
using System.Security.Cryptography;
using System.Text;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Extensions;

public class Sha256Test
{
    [Fact]
    public void TestSha()
    {
        using (var sha = new SHA256Managed())
        {
            var textData = Encoding.UTF8.GetBytes("+skibidivapapa");
            var hexHash = sha.ComputeHash(textData).ToHex();
            hexHash.Should().Be("f76f6355c7575ffd6c54c7fdeb3f7fbe0531f0a2206e86caafd9e3c8c489c87b");
        }

        "+skibidivapapa".sha256().Should().Be("f76f6355c7575ffd6c54c7fdeb3f7fbe0531f0a2206e86caafd9e3c8c489c87b");
        
        using (var sha = new SHA256Managed())
        {
            var textData = Encoding.UTF8.GetBytes("+skibidivapapatrympyrym");
            var hexHash = sha.ComputeHash(textData).ToHex();
            hexHash.Should().Be("811e1beca89153462529bc59e05fd0f4c34fe8cdf891127b6c16252d3f4b9052");
        }
        
        "+skibidivapapatrympyrym".sha256().Should().Be("811e1beca89153462529bc59e05fd0f4c34fe8cdf891127b6c16252d3f4b9052");
        
    }    
}

