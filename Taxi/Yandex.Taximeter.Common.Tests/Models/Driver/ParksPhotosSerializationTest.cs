using System.Collections.Generic;
using FluentAssertions;
using Newtonsoft.Json;
using Xunit;
using Yandex.Taximeter.Core.Clients;
using Yandex.Taximeter.Core.Helper;

namespace Yandex.Taximeter.Common.Tests.Models.Driver
{
    public class ParksPhotosSerializationTest
    {
        [Fact]
        public void Test_ResponseOk()
        {
            const string strPhotos =
                "{" +
                "  'photos': [" +
                "     {" +
                "       'type': 'driver'," +
                "       'scale': 'original'," +
                "       'href': 'asd'" +
                "     }, {" +
                "       'type': 'front'," +
                "       'scale': 'large'," +
                "       'href': 'asd'" +
                "     }, {" +
                "       'type': 'salon'," +
                "       'scale': 'small'," +
                "       'href': 'asd'" +
                "     }, {" +
                "       'type': 'left'," +
                "       'scale': 'original'," +
                "       'href': 'asd'" +
                "     }" +
                "   ]" +
                "}";

            var photos = new ParksPhotosResponse
            {
                photos = new List<ParksPhoto>
                {
                    new ParksPhoto {type = ePhotoType.Driver, scale = ePhotoScale.Original, href = "asd"},
                    new ParksPhoto {type = ePhotoType.Front, scale = ePhotoScale.Large, href = "asd"},
                    new ParksPhoto {type = ePhotoType.Salon, scale = ePhotoScale.Small, href = "asd"},
                    new ParksPhoto {type = ePhotoType.Left, scale = ePhotoScale.Original, href = "asd"},
                }
            };

            JsonConvert.DeserializeObject<ParksPhotosResponse>(strPhotos,
                StaticHelper.JsonSerializerSettings).Should().BeEquivalentTo(photos);
        }

        [Fact]
        public void Test_ResponseUnexpectedFormat()
        {
            const string strPhotos = "{" +
                                      "  'photos': [" +
                                      "     {" +
                                      "       'type': 'driver'," +
                                      "       'scale': 'original'," +
                                      "       'reference': 'asd'" +
                                      "     }" +
                                      "   ]" +
                                      "}";

            Assert.Throws<JsonSerializationException>(
                () => JsonConvert.DeserializeObject<ParksPhotosResponse>(strPhotos,
                    StaticHelper.JsonSerializerSettings));
        }

        [Fact]
        public void Test_DeleteRequest()
        {
            const string strRequest = "{\"photos\":[\"driver\",\"left\",\"front\",\"salon\"]}";

            var request = new ParksPhotosDeleteRequest
            {
                photos = new List<ePhotoType> {ePhotoType.Driver, ePhotoType.Left, ePhotoType.Front, ePhotoType.Salon}
            };

            JsonConvert.SerializeObject(request).Should().Be(strRequest);
        }
    }
}
