using System;
using System.Collections.Generic;
using MongoDB.Bson;
using Newtonsoft.Json;
using Xunit;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Car;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Models.Car
{
    public class CarUpdatedMessageDeserializeTest
    {
        [Fact]
        public void Test()
        {
            var date = new DateTime(2000, 1, 2, 13, 33, 45, 67, DateTimeKind.Utc);
            var car = new CarDoc
            {
                Id = ObjectId.Parse("012345678901234567890123"),
                ParkId = "park",
                CarId = "car",
                Number = "number",
                NumberNormalized = "number_normalized",
                Vin = "vin",
                Brand = "brand",
                Model = "model",
                Year = 2018,
                Color = "Черный",
                Callsign = "callsign",
                Description = "descrition",
                EuroCarSegment = "eurocarsegment",
                RegistrationCertificate = "registrationssertificate",
                OwnerId = "owner",
                PermitNumber = "permitnumber",
                PermitSeries = "permitseries",
                PermitDocument = "permitdocument",
                Status = CarWorkStatus.Repairing,
                Category = new CarCategory
                {
                    Econom = true,
                    Comfort = true,
                    ComfortPlus = true,
                    Business = true,
                    Minivan = true,
                    Limousine = true,
                    Vip = true,
                    Trucking = true,
                    Wagon = true,
                    Minibus = true,
                    Pool = true,
                    Start = true,
                    Standard = true,
                    Ultimate = true,
                    SelfDriving = true,
                    DemoStand = true,
                    Maybach = true,
                    MKK = true
                },
                Service = new CarService
                {
                    WiFi = true,
                    Conditioner = true,
                    Wagon = true,
                    Animals = true,
                    Smoking = true,
                    Delivery = true,
                    ChildSeat = true,
                    VipEvent = true,
                    WomanDriver = true,
                    POS = true,
                    PrintBill = true,
                    YandexMoney = true,
                    Bicycle = true,
                    Booster = true,
                    Ski = true,
                    ExtraSeats = true,
                    Lightbox = true,
                    Sticker = true,
                    Charge = true,
                    Rug = true,
                    Franchise = true
                },
                Transmission = CarTransmission.Robotic,
                Chairs = new List<CarChair>
                {
                    new CarChair
                    {
                        Brand   = "brand",
                        Categories = new SortedSet<int>{1,4},
                        Isofix = true
                    }
                },
                ConfirmedChairs = new List<CarConfirmedChair>
                {
                    new CarConfirmedChair
                    {
                        Brand = "brand",
                        Categories = new SortedSet<int>{1,4},
                        Isofix = true,
                        InventoryNumber = "number",
                        IsEnabled = true                        
                    }
                },
                ConfirmedBoosters = 3,
                CreatedDate = date,
                ServiceDate = date,
                OsagoDate = date,
                OsagoNumber = "osago",
                KaskoDate = date,
                BoosterCount = 2,
                LightboxConfirmed = true,
                StickerConfirmed = true,
                RugConfirmed = true,
                ChargeConfirmed = true,
                Onlycard = true,
                Rental = true,
                Mileage = 10,
                Tariffs = new List<string>{"tariff"},
                Tags = new HashSet<string>{"tag1", "tag2", "tag2"},
                ModifiedDate = date
            };
            
            var serializedCar = JsonConvert.SerializeObject(car, StaticHelper.JsonSerializerSettings);
            var fakeNewData = JsonConvert.SerializeObject(new CarDoc
            {
                ParkId = "fake",
                CarId = "fake"
            }, StaticHelper.JsonSerializerSettings);
            
            var message = JsonConvert.DeserializeObject<CarUpdatedMessage>(
                $"{{'new_data': {serializedCar}}}", StaticHelper.JsonSerializerSettings);
            TestUtils.CheckJsonSerialization(message);
            message = JsonConvert.DeserializeObject<CarUpdatedMessage>(
                $"{{'new_data': {fakeNewData}, 'old_data': {serializedCar}}}", StaticHelper.JsonSerializerSettings);
            TestUtils.CheckJsonSerialization(message);
        }
    }
}
