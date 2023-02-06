using System.Collections.Generic;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using Moq;
using Newtonsoft.Json.Linq;
using Xunit;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Models.Orders;
using Yandex.Taximeter.Core.Services;
using Yandex.Taximeter.Core.Services.Culture;
using Yandex.Taximeter.Core.Services.Order.SetCar;
using Yandex.Taximeter.Core.Services.Order.SetCar.Model;

namespace Yandex.Taximeter.Common.Tests.Services.Order
{
    public class SetCarDtoConverterTests
    {
        private readonly ISetCarDtoConverter _converter = new SetCarDtoConverter(Mock.Of<ILogger<SetCarDtoConverter>>());
        
        [Fact]
        public void TestToDriverPushDto_FixedPriceHidden_RemovesFixedPrice()
        {
            var setCar = new SetCarItem
            {
                FixedPrice = new FixedPriceSettings
                {
                    Show = false,
                    Price = 100
                }
            };

            var json = _converter.ToDriverPushDto(setCar, new TaximeterCultureInfo("en-US"), false);
            json.Should().NotContainKey(OrderSqlColumns.FIXED_PRICE);
        }
        
        [Fact]
        public void TestToDriverPushDto_DriverFixedPriceHidden_RemovesDriverFixedPrice()
        {
            var setCar = new SetCarItem
            {
                DriverFixedPrice = new FixedPriceSettings
                {
                    Show = false,
                    Price = 100
                }
            };

            var json = _converter.ToDriverPushDto(setCar, new TaximeterCultureInfo("en-US"), false);
            json.Should().NotContainKey(SetCarItem.DRIVER_FIXED_PRICE);
        }
        
        [Fact]
        public void TestOrderPoolToDriverDto_FixedPriceHidden_RemovesPrice()
        {
            var pool = new Pool
            {
                Orders = new Dictionary<string, SetCarItem> {
                    ["order1"] = new SetCarItem
                    {
                        FixedPrice = new FixedPriceSettings
                        {
                            Show = false,
                            Price = 100
                        }
                    }
                }
            };

            dynamic json = _converter.OrderPoolToDriverDto(pool, new Dictionary<string, RequestConfirmStatus>());
            
            ((JObject)json.orders.order1).Should().ContainKey(OrderSqlColumns.FIXED_PRICE);
            ((JObject)json.orders.order1.fixed_price).Should().NotContainKey(FixedPriceSettings.PRICE);
        }
        
        [Fact]
        public void TestToDriverPushDto_FixedPriceShown_DoesNotRemoveFixedPrice()
        {
            var setCar = new SetCarItem
            {
                FixedPrice = new FixedPriceSettings
                {
                    Show = true,
                    Price = 100
                }
            };

            var json = _converter.ToDriverPushDto(setCar, new TaximeterCultureInfo("en-US"), false);
            json.Should().ContainKey(OrderSqlColumns.FIXED_PRICE);
        }
        
          
        [Fact]
        public void TestSetCarDtoConveter_FixedPriceAbsent_DoesNothing()
        {
            var setCar = new SetCarItem
            {
            };

            var json = _converter.ToDriverPushDto(setCar, new TaximeterCultureInfo("en-US"), false);
            json.Should().NotContainKey(OrderSqlColumns.FIXED_PRICE);
        }
    }
}