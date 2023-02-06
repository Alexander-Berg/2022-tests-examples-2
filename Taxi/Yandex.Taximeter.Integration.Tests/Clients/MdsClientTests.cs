using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Moq;
using Xunit;
using Yandex.Taximeter.Core.Clients;
using Yandex.Taximeter.Core.Configuration.Options;
using Yandex.Taximeter.Core.Graphite;
using Yandex.Taximeter.Integration.Tests.Fixtures;

namespace Yandex.Taximeter.Integration.Tests.Clients
{
    public class MdsClientTests : IClassFixture<FatFixture>
    {
        private readonly FatFixture _fixture;

        public MdsClientTests(FatFixture fixture)
        {
            _fixture = fixture;
        }

        private Random _random = new Random();

        public static byte[] Rotate(Stream source, int angle)
        {
            //Open the source image and create the bitmap for the rotatated image
            using (Bitmap sourceImage = new Bitmap(source))
            using (Bitmap rotateImage = new Bitmap(sourceImage.Width, sourceImage.Height))
            {
                //Set the resolution for the rotation image
                rotateImage.SetResolution(sourceImage.HorizontalResolution, sourceImage.VerticalResolution);
                //Create a graphics object
                using (Graphics gdi = Graphics.FromImage(rotateImage))
                {
                    //Rotate the image
                    gdi.TranslateTransform((float)sourceImage.Width / 2, (float)sourceImage.Height / 2);
                    gdi.RotateTransform(angle);
                    gdi.TranslateTransform(-(float)sourceImage.Width / 2, -(float)sourceImage.Height / 2);
                    gdi.DrawImage(sourceImage, new System.Drawing.Point(0, 0));
                }

                var ep = new EncoderParameters(1);
                ep.Param[0] = new EncoderParameter(System.Drawing.Imaging.Encoder.Quality, 80L);
                ImageCodecInfo imageCodecInfo = null;
                foreach (ImageCodecInfo item in ImageCodecInfo.GetImageEncoders())
                {
                    if (item.MimeType == "image/jpeg")
                    {
                        imageCodecInfo = item;
                        break;
                    }
                }

                sourceImage.Dispose();

                using (MemoryStream ms = new MemoryStream())
                {
                    rotateImage.Save(ms, imageCodecInfo, ep);
                    return ms.ToArray();
                }
            }
        }

        [Fact]
        public async Task TestMdsClientUpload()
        {
            IMdsClient mdsClient = new MdsClient(
                _fixture.ServiceProvider.GetService<IOptions<MdsOptions>>(),
                _fixture.ServiceProvider.GetService<ILogger<MdsClient>>(),
                Mock.Of<IGraphiteService>());
            var testString = "TestMDSupload";
            
            using (var stream = MakeStreamFromString(testString))
            {
                var suffix = _random.Next(int.MaxValue);
                var key = await mdsClient.UploadAsync($"test_only_{suffix}.txt", stream);
                var result = await mdsClient.GetAsync(key);

                var dowloadedString = Encoding.UTF8.GetString(result);
                dowloadedString.Should().Be(testString);

                await mdsClient.DeleteAsync(key);
            }
        }

        [Fact(Skip = "FIXIT")]
        public async Task TestMdsClientRealFileAsBytes()
        {
            IMdsClient mdsClient = new MdsClient(
                _fixture.ServiceProvider.GetService<IOptions<MdsOptions>>(),
                _fixture.ServiceProvider.GetService<ILogger<MdsClient>>(),
                Mock.Of<IGraphiteService>());
            var fileName = @"C:\Users\azinoviev\pike.jpg";
            var outFileName = @"C:\Users\azinoviev\pike_out.jpg";
            var suffix = _random.Next(int.MaxValue);

            var bytes = File.ReadAllBytes(fileName);
            var key = await mdsClient.UploadAsync($"test_only_pike_{suffix}.txt", bytes);
            var result = await mdsClient.GetAsync(key);

            result.Length.Should().Be(bytes.Length);
            File.WriteAllBytes(outFileName, result);

            await mdsClient.DeleteAsync(key);
        }

        [Fact(Skip = "FIXIT")]
        public async Task TestMdsClientRealFileAsStream()
        {
            IMdsClient mdsClient = new MdsClient(
                _fixture.ServiceProvider.GetService<IOptions<MdsOptions>>(),
                _fixture.ServiceProvider.GetService<ILogger<MdsClient>>(),
                Mock.Of<IGraphiteService>()
            );
            var fileName = @"C:\Users\aprudnikov\pike.jpg";
            var outFileName = @"C:\Users\aprudnikov\pike_out_stream.jpg";
            var suffix = _random.Next(int.MaxValue);

            using (var stream = new MemoryStream(File.ReadAllBytes(fileName)))
            {
                var key = await mdsClient.UploadAsync($"test_only_pike_{suffix}.txt", stream);
                var result = await mdsClient.GetAsync(key);

                result.Length.Should().Be((int)stream.Length);
                File.WriteAllBytes(outFileName, result);

                await mdsClient.DeleteAsync(key);
            }
        }

        private MemoryStream MakeStreamFromString(string data)
        {
            var stream = new MemoryStream();
            var writer = new StreamWriter(stream);
            writer.Write(data);
            writer.Flush();
            stream.Position = 0;
            return stream;
        }
    }
}
