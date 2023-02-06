using System;
using System.Collections.Generic;
using MongoDB.Bson;
using Newtonsoft.Json;
using Xunit;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Driver;
using Yandex.Taximeter.Test.Utils.Utils;
using Yandex.Taximeter.XService.Areas.utils;

namespace Yandex.Taximeter.Common.Tests.Models.Driver
{
    public class DriverUpdatedMessageDeserializeTest
    {
        [Fact]
        public void Test()
        {
            var date = new DateTime(2000, 1, 2, 13, 33, 45, 67, DateTimeKind.Utc);
            var driver = new DriverDoc
            {
                Id = ObjectId.Parse("012345678901234567890123"),
                ParkId = "park",
                DriverId = "driver",
                CarId = "car",
                FirstName = "name",
                LastName = "surname",
                WorkStatus = DriverWorkStatus.Working,
                Password = "qwerty",
                HiringDetails = new DriverHiringDetails
                {
                    HiringDate = date,
                    HiringType = "some_type"
                },
                Tags = new HashSet<string>{"tag1", "tag2", "tag2"},
                QcSync = new Dictionary<string, DateTime?>{["qc1"]=null, ["qc2"]=date}
            };
            
            var serializedDriver = JsonConvert.SerializeObject(driver, StaticHelper.JsonSerializerSettings);
            var fakeNewData = JsonConvert.SerializeObject(new DriverDoc
            {
                ParkId = "fake",
                DriverId = "fake"
            }, StaticHelper.JsonSerializerSettings);
            
            var message = JsonConvert.DeserializeObject<DriverUpdatedMessage>(
                $"{{'new_data': {serializedDriver}}}", StaticHelper.JsonSerializerSettings);
            TestUtils.CheckJsonSerialization(message);
            message = JsonConvert.DeserializeObject<DriverUpdatedMessage>(
                $"{{'new_data': {fakeNewData}, 'old_data': {serializedDriver}}}", StaticHelper.JsonSerializerSettings);
            TestUtils.CheckJsonSerialization(message);

            message = JsonConvert.DeserializeObject<DriverUpdatedMessageRequest>(
                $"{{'new_driver': {serializedDriver}}}", StaticHelper.JsonSerializerSettings);
            TestUtils.CheckJsonSerialization(message);
            
            message = JsonConvert.DeserializeObject<DriverUpdatedMessageRequest>(
                $"{{'new_driver': {fakeNewData}, 'old_driver': {serializedDriver}}}", StaticHelper.JsonSerializerSettings);
            TestUtils.CheckJsonSerialization(message);
        }
    }
}
