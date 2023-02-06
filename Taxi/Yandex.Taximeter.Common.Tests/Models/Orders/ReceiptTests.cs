using FluentAssertions;
using JetBrains.Annotations;
using Xunit;
using Yandex.Taximeter.Core.Models.Orders;
using Yandex.Taximeter.Test.Utils.Fakes;

namespace Yandex.Taximeter.Common.Tests.Models.Orders
{
    public class ReceiptTests
    {
        [Fact]
        public void TestReceipt_ParseEmptyString_ReturnsNullReceipt()
        {
            var data = string.Empty;
            var receipt = Receipt.Parse(data);
            receipt.Should().BeNull();
        }
        
        [Fact]
        public void TestReceipt_ParseNull_ReturnsNullReceipt()
        {
            var data = "null";
            var receipt = Receipt.Parse(data);
            receipt.Should().BeNull();
        }
        
        [Theory]
        [InlineData("{}", null)]
        [InlineData("{'calc_method':2}", RequestConfirmCalcMethod.Fixed)]
        public void TestReceipt_Parse_ParsesCalcMethod(string data, RequestConfirmCalcMethod? method)
        {
            var receipt = Receipt.Parse(data);
            receipt.Should().NotBeNull();
            receipt.CalcMethod.Should().Be(method);
        }

        [Theory]
        [InlineData("{}", null)]
        [InlineData("{'details':[]}", null)]
        [InlineData("{'details':[{'service_type':'free_route','sum':0.0}]}", null)]
        [InlineData("{'details':[{'service_type':'waiting_in_transit','sum':123.0}]}", 123.0)]
        [InlineData("{'details':[{'service_type':'waiting_in_transit','sum':100.0},{'service_type':'waiting_in_transit','sum':23.0}]}", 123.0)]
        public void TestReceipt_Parse_ParsesWaitingInTransit(string data, double? expected)
        {
            var receipt = Receipt.Parse(data);
            receipt.Should().NotBeNull();
            receipt.Data?.WaitingInTransitSum.Should().Be((decimal?)expected);
        }
        
        [Theory]
        [InlineData("{'details':[{'service_type':'service','count':2,'name':'child_chair','price':400,'sum':200}]}", 
            "child_chair", 400.0, 2, 200.0)]
        [InlineData("{'details':[{'service_type':'service','count':1,'name':'third_passenger','price':200,'sum':200}]}",
            "third_passenger", 200.0, 1, 200.0)]
        [InlineData("{'details':[{'service_type':'service','name':'hourly_rental.2_hours','price':200,'sum':200}]}",
            "hourly_rental.2_hours", 200.0, 0, 200.0)]
        [InlineData("{'details':[{'service_type':'service','name':'hourly_rental.5_hours','price':400}]}",
            "hourly_rental.5_hours", 400.0, 0, 0)]
        [InlineData("{'details':[{'service_type':'service','name':'child_chair.booster','count':1,'price':200}]}",
            "child_chair.booster", 200.0, 1, 0)]
        [InlineData("{'details':[{'service_type':'service','count':1,'name':'not_yet_known','price':200,'sum':200}]}",
            "not_yet_known", 200.0, 1, 200.0)]
        [InlineData("{'details':[{'service_type':'service','name':'child_chair','sum':200}]}",
            null, 0, 0, 0)]
        [InlineData("{'details':[{'service_type':'service','name':'','price':200}]}",
            null, 0, 0, 0)]
        public void TestReceipt_Parse_ParsesService(string data, [CanBeNull] string name, double expectedCost, double expectedCount, double expectedItemCost)
        {
            var receipt = Receipt.Parse(data);
            receipt.Should().NotBeNull();
            if (!string.IsNullOrEmpty(name))
            {    
                receipt.Data?.Services[name].Should().Be((decimal)expectedCost);
                receipt.Data?.ServicesCount[name]["count"].Should().Be((decimal)expectedCount);
                receipt.Data?.ServicesCount[name]["price"].Should().Be((decimal)expectedCost);
                receipt.Data?.ServicesCount[name]["sum"].Should().Be((decimal)expectedItemCost);
            }
            else
            {
                receipt.Data?.Services.Should().BeNull();
                receipt.Data?.ServicesCount.Should().BeNull();
            }
        }
    }
}
