using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Linq;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Extensions;
using Yandex.Taximeter.Core.Services;
// ReSharper disable AssignNullToNotNullAttribute

namespace Yandex.Taximeter.Common.Tests.Services
{
    public class ImageResizerTests
    {
        private static readonly Color TestColor = Color.White;
        private static readonly ImageFormat TestFormat = ImageFormat.Png;

        private readonly ImageResizer _resizer = new ImageResizer(TestFormat);

        [Theory]
        [InlineData(10, 20, 20, 40)] //upscale
        [InlineData(10, 20, 5, 10)] //downscale
        public void ResizeToHeight_ValidArgs_Resizes(int width, int height, int newWidth, int newHeight)
        {
            using (var img = CreateBitmap(width, height, TestColor))
            using (var resizedStream = _resizer.ResizeToHeight(img, newHeight))
            using (var resizedImg = Image.FromStream(resizedStream))
            {
                AssertImage(resizedImg, new Size(newWidth, newHeight), TestColor);
            }
        }

        [Theory]
        [InlineData(10, 20, 20, 40)] //upscale
        [InlineData(10, 20, 5, 10)] //downscale
        public void ResizeToWidth_ValidArgs_Resizes(int width, int height, int newWidth, int newHeight)
        {
            using (var img = CreateBitmap(width, height, TestColor))
            using (var resizedStream = _resizer.ResizeToWidth(img, newWidth))
            using (var resizedImg = Image.FromStream(resizedStream))
            {
                AssertImage(resizedImg, new Size(newWidth, newHeight), TestColor);
            }
        }

        [Theory]
        [InlineData(20, 20, 10, 10, 10)] //downscale square image
        [InlineData(10, 20, /*dim*/10, /*new size*/5, 10)] //downscale to height
        [InlineData(20, 10, /*dim*/10, /*new size*/10, 5)] //downscale to width
        public void ResizeToMaxDimension_ValidArgs_Resizes(
            int width, int height, int maxDimension, int newWidth, int newHeight)
        {
            using (var img = CreateBitmap(width, height, TestColor))
            using (var resizedStream = _resizer.ResizeToMaxDimension(img, maxDimension))
            using (var resizedImg = Image.FromStream(resizedStream))
            {
                AssertImage(resizedImg, new Size(newWidth, newHeight), TestColor);
            }
        }

        [Theory]
        [InlineData(20, 40, /*bounds*/10, 15, /*new size*/10, 20)] //downscale to width bound
        [InlineData(20, 40, /*bounds*/5, 20, /*new size*/10, 20)] //downscale to height bound
        public void DownscaleIfLarger_ImageLargerThanBounds_Downscales(
            int width, int height, int boundWidth, int boundHeigh, int newWidth, int newHeight)
        {
            var minBounds = new Size(boundWidth, boundHeigh);
            using (var img = CreateBitmap(width, height, TestColor))
            using (var resizedStream = _resizer.DownscaleIfLarger(img, minBounds))
            using (var resizedImg = Image.FromStream(resizedStream))
            {
                AssertImage(resizedImg, new Size(newWidth, newHeight), TestColor);
            }
        }

        [Theory]
        [InlineData(10, 20, 11, 21)]
        [InlineData(10, 20, 11, 15)]
        [InlineData(10, 20, 9, 22)]
        public void DownscaleIfLarger_ImageSmallerThanBounds_ReturnsNull(
            int width, int heigh, int boundWidth, int boundHeight)
        {
            var minBounds = new Size(boundWidth, boundHeight);
            using (var img = CreateBitmap(width, heigh, TestColor))
            using (var resizedStream = _resizer.DownscaleIfLarger(img, minBounds))
            {
                resizedStream.Should().BeNull();
            }
        }

        [Fact]
        public void DownscaleIfLarger_WithByteArray_Resizes()
        {
            var imgBytes = CreateBitmapArray(10, 20, TestColor);

            var resizedBytes = _resizer.DownscaleIfLarger(imgBytes, new Size(5, 10));

            //Assert
            using (var resizedStream = new MemoryStream(resizedBytes))
            using (var resizedImg = Image.FromStream(resizedStream))
            {
                AssertImage(resizedImg, new Size(5, 10), TestColor);
            }
        }

        [Fact]
        public void DownscaleIfLarger_WithByteArray_DoesNotAffectOriginalArray()
        {
            var imgBytes = CreateBitmapArray(10, 20, TestColor);

            var imgBytesArg = (byte[]) imgBytes.Clone();
            _resizer.DownscaleIfLarger(imgBytesArg, new Size(5, 10));

            imgBytesArg.SequenceEqual(imgBytes).Should().BeTrue();
        }

        [Fact]
        public void ResizeToSizes_ValidArgs_ResizesToSpecifiedSizes()
        {
            var sizes = new[] {new Size(5, 5), new Size(10, 10), new Size(20, 20)};
            var imgStream = new MemoryStream();
            using (var img = CreateBitmap(10, 10, Color.White))
            {
                img.Save(imgStream, TestFormat);
            }

            //Act
            var resized = _resizer.ResizeToSizes(imgStream, sizes);

            //Assert
            foreach (var size in sizes)
            {
                using (var resizedStream = new MemoryStream(resized[size]))
                using (var resizedImg = Image.FromStream(resizedStream))
                {
                    AssertImage(resizedImg, size, TestColor);
                }
            }
        }

        private static byte[] CreateBitmapArray(int width, int height, Color color)
        {
            using (var img = CreateBitmap(width, height, color))
                return img.ToByteArray(TestFormat);
        }

        private static Bitmap CreateBitmap(int width, int height, Color color)
        {
            var img = new Bitmap(width, height);
            for(var i =0; i < img.Width; i++)
            for (var j = 0; j < img.Height; j++)
                img.SetPixel(i, j, color);
            return img;
        }

        private static void AssertImage(Image image, Size expectedSize, Color expectedColor)
        {
            using (var bmp = new Bitmap(image))
            {
                bmp.Size.Should().Be(expectedSize);
                IsFilledWithColor(bmp, expectedColor).Should().BeTrue();
            }

            bool IsFilledWithColor(Bitmap img, Color color)
            {
                //ignore borders because of interpolation effects
                for(var i =1; i < img.Width - 1; i++)
                for (var j = 1; j < img.Height - 1; j++)
                {
                    var pixel = img.GetPixel(i, j);
                    if (pixel.R != color.R || pixel.G != color.G || pixel.B != color.B)
                        return false;
                }
                return true;
            }
        }
    }
}