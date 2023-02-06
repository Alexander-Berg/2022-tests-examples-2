using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;

namespace Yandex.Taximeter.Test.Utils.Fakes
{
    public class FakeFormFile : IFormFile
    {
        private readonly MemoryStream _memoryStream;

        public FakeFormFile(Stream content)
        {
            _memoryStream = new MemoryStream();
            content.CopyTo(_memoryStream);
            _memoryStream.Position = 0;
            Length = content.Length;
        }

        public FakeFormFile()
        {
            _memoryStream = new MemoryStream();
            Length = 0;
        }

        public Stream OpenReadStream()
        {
            return _memoryStream;
        }

        public string ContentType { get; } = null;
        public string ContentDisposition { get; } = null;
        public IHeaderDictionary Headers { get; } = null;
        public long Length { get; }
        public string Name => FileName;
        public string FileName { get; } = Guid.NewGuid().ToString();

        public Task CopyToAsync(Stream target, CancellationToken cancellationToken = new CancellationToken())
        {
            return _memoryStream.CopyToAsync(target, 81920, cancellationToken);
        }

        public void CopyTo(Stream target)
        {
            _memoryStream.CopyTo(target);
        }

        public byte[] Content => _memoryStream.ToArray();
    }
}
