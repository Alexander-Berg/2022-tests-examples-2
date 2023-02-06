using System.IO;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Http.Internal;

namespace Yandex.Taximeter.Test.Utils.Utils
{
    public static class AspNetUtils
    {
        public static IFormFile BuildFormFile(string fileName, byte[] fileContent)
        {
            var fakeFileStream = new MemoryStream();
            fakeFileStream.Write(fileContent, 0, fileContent.Length);
            fakeFileStream.Position = 0;
            return new FormFile(fakeFileStream, 0, fileContent.Length, "", fileName);
        }
    }
}