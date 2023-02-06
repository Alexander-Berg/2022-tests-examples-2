using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using FluentAssertions;
using MongoDB.Bson.Serialization;
using Xunit;
using Yandex.Taximeter.Core.Extensions;
using Yandex.Taximeter.Core.Services.Subventions;
using Yandex.Taximeter.Core.Services.Subventions.Docs;

namespace Yandex.Taximeter.Common.Tests.Services.Subventions
{
    public class OrderSubventionReasonsTests
    {
        [Fact]
        public void Constructor_HasUnpaidRules_TakesVisibleUnpaidRules()
        {
            var doc = new OrderSubventionReasonsDoc
            {
                SubventionCalcRules = new List<SubventionCalcRuleDoc>
                {
                    new SubventionCalcRuleDoc
                    {
                        DisplayInTaximeter = true,
                        Sum = 10,
                        Type = "type1",
                        DeclineReasons = new List<SubventionDeclineReasonDoc>
                        {
                            new SubventionDeclineReasonDoc
                            {
                                Key ="key1",
                                Minimum = "10",
                                Value = "5",
                                Reason = "reason1"
                            }
                        }
                    },
                    new SubventionCalcRuleDoc
                    {
                        DisplayInTaximeter = false,
                        Sum = 20,
                        Type = "type2",
                        DeclineReasons = new List<SubventionDeclineReasonDoc>
                        {
                            new SubventionDeclineReasonDoc
                            {
                                Key ="key2",
                                Minimum = "10",
                                Value = "5",
                                Reason = "reason2"
                            }
                        }
                    }
                }
            };

            var reasons = new OrderSubventionReasons(doc);

            reasons.UnpaidRules.Count.Should().Be(1);
            var rule = reasons.UnpaidRules[0];
            rule.Sum.Should().Be(10);
            rule.Type.Should().Be("type1");
            rule.DeclineReasons.Count.Should().Be(1);
        }

        [Fact]
        public void BuildDisabledDto_NoDisabledRules_ReturnsEmptyDto()
        {
            var reasons = new OrderSubventionReasons(new OrderSubventionReasonsDoc
            {
                PaidCommission = 20,
                SubventionCalcRules = new List<SubventionCalcRuleDoc>
                {
                    new SubventionCalcRuleDoc
                    {
                        Type = "type1",
                        PaidSum = 200,
                    }
                }
            });

            var dto = reasons.BuildDisabledDto(CultureInfo.GetCultureInfo("ru"));
            dto.DisabledRules.Should().BeEmpty();
        }

        [Fact]
        public void BuildDisabledDto_HasDisabledRules_BuildsDto()
        {
            var reasons = new OrderSubventionReasons(new OrderSubventionReasonsDoc
            {
                PaidCommission = 20,
                SubventionCalcRules = new List<SubventionCalcRuleDoc>
                {
                    new SubventionCalcRuleDoc
                    {
                        PaidSum = 200,
                    },
                    new SubventionCalcRuleDoc
                    {
                        Sum = 100,
                        Type = "type1",
                        DisplayInTaximeter = true,
                        DeclineReasons = new List<SubventionDeclineReasonDoc>
                        {
                            new SubventionDeclineReasonDoc
                            {
                                Key = "ride_count",
                                Reason = "too_low_value",
                                Minimum = "100",
                                Value = "10"
                            }
                        }
                    },
                    new SubventionCalcRuleDoc
                    {
                        Sum = 200,
                        Type = "type2",
                        DisplayInTaximeter = true,
                        DeclineReasons = new List<SubventionDeclineReasonDoc>
                        {
                            new SubventionDeclineReasonDoc
                            {
                                Key = "acceptance_rate",
                                Reason = "too_low_value",
                                Minimum = "100",
                                Value = "10"
                            }
                        }
                    },
                    new SubventionCalcRuleDoc
                    {
                        Sum = 200,
                        Type = "type3",
                        DisplayInTaximeter = true,
                        DeclineReasons = new List<SubventionDeclineReasonDoc>
                        {
                            new SubventionDeclineReasonDoc
                            {
                                Key = "ride_count",
                                Reason = "sticker",
                                Minimum = "100",
                                Value = "1000"
                            }
                        }
                    }
                }
            });

            var dto = reasons.BuildDisabledDto(CultureInfo.GetCultureInfo("ru"));

            dto.DisabledRules.Length.Should().Be(3);

            dto.DisabledRules[0].Type.Should().Be("type1");
            dto.DisabledRules[0].DeclineReasons[0].Should().Be("Выполнено 10 из 100 заказов");

            dto.DisabledRules[1].Type.Should().Be("type2");
            dto.DisabledRules[1].DeclineReasons[0].Should().Be("Доля принятых заказов 10 из 100");

            dto.DisabledRules[2].Type.Should().Be("type3");
            dto.DisabledRules[2].DeclineReasons[0].Should().StartWith("Ваш автомобиль не забрендирован");

        }

        [Fact]
        public void BuildDisabledRules_HasFraudReasons_HidesFraudReasons()
        {
            var reasons = new OrderSubventionReasons(new OrderSubventionReasonsDoc
            {
                PaidCommission = 20,
                SubventionCalcRules = new List<SubventionCalcRuleDoc>
                {
                    new SubventionCalcRuleDoc
                    {
                        Sum = 100,
                        Type = "type1",
                        DisplayInTaximeter = true,
                        DeclineReasons = new List<SubventionDeclineReasonDoc>
                        {
                            new SubventionDeclineReasonDoc
                            {
                                Key = OrderSubventionReasons.CalcRule.ORDER_COST_REASON
                            }
                        }
                    }
                }
            });

            var dto = reasons.BuildDisabledDto(CultureInfo.GetCultureInfo("en"));
            dto.DisabledRules.Single().Type.Should().Be("type1");
            dto.DisabledRules.Single().Sum.Should().Be(100);
            dto.DisabledRules.Single().DeclineReasons.Should().BeEmpty();
        }

        [Fact]
        public void CalcPaidAndPromised_NoBonusAndNoUndeclinedRules_ReturnsZero()
        {
            var reasons = new OrderSubventionReasons(new OrderSubventionReasonsDoc());

            var paidAndPromised = reasons.CalcPaidAndPromised(250);

            paidAndPromised.Should().Be(0m);
        }

        [Fact]
        public void CalcPaidAndPromised_HasBonusesAndUndeclinedRules_ReturnsSumOfRulesAndLastBonus()
        {
            const decimal typeAddSum = 25;
            const decimal typeDiscountPaybackSum = 50;
            const decimal typeGuaranteeSum = 200;
            const decimal lastBonus = 30;
            const decimal orderCost = 100m;

            var reasons = new OrderSubventionReasons(
                new OrderSubventionReasonsDoc
                {
                    SubventionCalcRules = new List<SubventionCalcRuleDoc>
                    {
                        new SubventionCalcRuleDoc
                        {
                            Type = SubventionCalcRuleDoc.TYPE_ADD,
                            PaidSum = typeAddSum,
                            IsBonus = true
                        },
                        new SubventionCalcRuleDoc
                        {
                            Type = SubventionCalcRuleDoc.TYPE_DISCOUNT_PAYBACK,
                            PaidSum = typeDiscountPaybackSum,
                            IsBonus = true
                        },
                        new SubventionCalcRuleDoc
                        {
                            DisplayInTaximeter = false,
                            Sum = typeGuaranteeSum,
                            Type = SubventionCalcRuleDoc.TYPE_GUARANTEE,
                            IsBonus = false
                        }
                    },
                    SubventionBonus = new List<SubventionBonusDoc>
                    {
                        new SubventionBonusDoc
                        {
                            Value = "100"
                        },
                        new SubventionBonusDoc
                        {
                            Value = lastBonus.ToString(CultureInfo.InvariantCulture)
                        }
                    }
                });

            var paidAndPromised = reasons.CalcPaidAndPromised(orderCost);

            paidAndPromised.Should()
                .Be(typeGuaranteeSum - orderCost - typeDiscountPaybackSum +
                    typeAddSum +
                    lastBonus);
        }

        [Fact]
        public void CalcPoolPaidAndPromised_NoBonusAndNoPaidRules_ReturnsZero()
        {
            var reasons = new OrderSubventionReasons(new OrderSubventionReasonsDoc());

            reasons.CalcPoolPaidAndPromised(100m).Should().Be(0m);
        }

        [Fact]
        public void CalcPoolPaidAndPromised_HasBonusPoolPaidAndPaidRules_SumsAllPaidRulesAndBonus()
        {
            const decimal typeAddSum = 60m;
            const decimal typeDiscountPaybackSum = 70m;
            const decimal lastBonus = 50m;
            const decimal poolPaid = 100m;
            const decimal orderCost = 100m;

            var reasons = new OrderSubventionReasons(
                new OrderSubventionReasonsDoc
                {
                    SubventionCalcRules = new List<SubventionCalcRuleDoc>
                    {
                        new SubventionCalcRuleDoc
                        {
                            Type = SubventionCalcRuleDoc.TYPE_ADD,
                            PaidSum = typeAddSum,
                            IsBonus = true
                        },
                        new SubventionCalcRuleDoc
                        {
                            Type = SubventionCalcRuleDoc.TYPE_DISCOUNT_PAYBACK,
                            PaidSum = typeDiscountPaybackSum,
                            IsBonus = true
                        },
                        new SubventionCalcRuleDoc
                        {
                            DisplayInTaximeter = false,
                            Sum = 112,
                            Type = SubventionCalcRuleDoc.TYPE_GUARANTEE,
                            IsBonus = false
                        }
                    },
                    SubventionBonus = new List<SubventionBonusDoc>
                    {
                        new SubventionBonusDoc
                        {
                            Value = lastBonus.ToString(CultureInfo.InvariantCulture)
                        }
                    },
                    PoolPaidSum = poolPaid
                });

            reasons.CalcPoolPaidAndPromised(orderCost).Should()
                .Be(typeAddSum + typeDiscountPaybackSum + lastBonus + poolPaid);
        }
        
        [Fact]
        public void CalcPaidAndPromised_HasPersonalSubventions_ReturnsCorrectPersonalSum()
        {
            var reasons = new OrderSubventionReasons(
                new OrderSubventionReasonsDoc
                {
                    SubventionCalcRules = new List<SubventionCalcRuleDoc>
                    {
                        new SubventionCalcRuleDoc
                        {
                            DisplayInTaximeter = true,
                            Type = SubventionCalcRuleDoc.TYPE_ADD,
                            Sum = 25,
                            IsBonus = false,
                            Id = "p_test_1"
                        },
                        new SubventionCalcRuleDoc
                        {
                            DisplayInTaximeter = true,
                            Type = SubventionCalcRuleDoc.TYPE_ADD,
                            Sum = 50,
                            IsBonus = false,
                            Id = "p_test_2"
                        },
                        new SubventionCalcRuleDoc
                        {
                            Type = SubventionCalcRuleDoc.TYPE_DISCOUNT_PAYBACK,
                            PaidSum = 50,
                            IsBonus = true,
                        },
                        new SubventionCalcRuleDoc
                        {
                            DisplayInTaximeter = true,
                            Sum = 200,
                            Type = SubventionCalcRuleDoc.TYPE_GUARANTEE,
                            IsBonus = true
                        },
                        new SubventionCalcRuleDoc
                        {
                            DisplayInTaximeter = true,
                            Sum = 300,
                            Type = SubventionCalcRuleDoc.TYPE_GUARANTEE,
                            IsBonus = false
                        }
                    },
                    SubventionBonus = new List<SubventionBonusDoc>
                    {
                        new SubventionBonusDoc
                        {
                            Value = "100"
                        },
                        new SubventionBonusDoc
                        {
                            Value = "30"
                        }
                    }
                });

            var paidAndPromised = reasons.CalcPaidAndPromised(100);

            //Bonus = 200 - (ordercost = 100) - (discount=50) = 50
            //NotBonus = Max(25,50) = 50
            //LastBonus = 30
            //Total = 50+50+30+50 = 180
            paidAndPromised.Should().Be(180);
        }
        
           [Fact]
        public void CalcPaidAndPromised_HasHoldedSubventions_DoesNotIncludeHolded()
        {
            var reasons = new OrderSubventionReasons(
                new OrderSubventionReasonsDoc
                {
                    SubventionCalcRules = new List<SubventionCalcRuleDoc>
                    {
                        new SubventionCalcRuleDoc
                        {
                            DisplayInTaximeter = true,
                            Type = SubventionCalcRuleDoc.TYPE_ADD,
                            Sum = 25,
                            IsBonus = false,
                            IsHolded = true,
                            Id = "p_test_1"
                        },
                        new SubventionCalcRuleDoc
                        {
                            DisplayInTaximeter = true,
                            Type = SubventionCalcRuleDoc.TYPE_ADD,
                            Sum = 50,
                            IsBonus = false,
                            IsHolded = true,
                            Id = "p_test_2"
                        },
                        new SubventionCalcRuleDoc
                        {
                            Type = SubventionCalcRuleDoc.TYPE_DISCOUNT_PAYBACK,
                            PaidSum = 50,
                            IsBonus = true,
                        },
                        new SubventionCalcRuleDoc
                        {
                            DisplayInTaximeter = true,
                            Sum = 200,
                            Type = SubventionCalcRuleDoc.TYPE_GUARANTEE,
                            IsBonus = true
                        },
                        new SubventionCalcRuleDoc
                        {
                            DisplayInTaximeter = true,
                            Sum = 300,
                            Type = SubventionCalcRuleDoc.TYPE_GUARANTEE,
                            IsBonus = false
                        }
                    },
                    SubventionBonus = new List<SubventionBonusDoc>
                    {
                        new SubventionBonusDoc
                        {
                            Value = "100"
                        },
                        new SubventionBonusDoc
                        {
                            Value = "30"
                        }
                    }
                });

            var paidAndPromised = reasons.CalcPaidAndPromised(100);

            //Bonus = 200 - (ordercost = 100) - (discount=50) = 50
            //NotBonus = 300 - (ordercost = 100) - (discount=50) = 150
            //LastBonus = 30
            //Total = 50+150+30+50 = 280
            paidAndPromised.Should().Be(280);
        }

        [Theory]
        [InlineData(291.0,33.0,0.0, "{\"_id\":ObjectId(\"5bd0c792099bfbac5f523228\"),\"order_id\":\"c17084d72eb6cb791b60fb569e4e4bce\",\"tickets\":[],\"subvention_calc_rules\":[{\"id\":ObjectId(\"5aeb20cab14b1dc01a56f0a5\"),\"sum\":0.0,\"type\":\"discount_payback\",\"is_fake\":false,\"is_holded\":false,\"sub_commission\":false,\"is_bonus\":true,\"is_once\":false,\"decline_reasons\":[],\"display_in_taximeter\":false,\"rule_display_in_taximeter\":false,\"driver_points\":null,\"clear_time\":null,\"group_id\":null,\"paid_sum\":\"33.0\"},{\"id\":ObjectId(\"5b97a38e07d86bd2349bea26\"),\"sum\":150.0,\"type\":\"guarantee\",\"is_fake\":false,\"is_holded\":false,\"sub_commission\":true,\"is_bonus\":false,\"is_once\":false,\"decline_reasons\":[],\"display_in_taximeter\":true,\"rule_display_in_taximeter\":true,\"driver_points\":41.0,\"clear_time\":null,\"group_id\":null},{\"id\":ObjectId(\"58a55b5c23ab3516851381ff\"),\"sum\":200.0,\"type\":\"guarantee\",\"is_fake\":true,\"is_holded\":false,\"sub_commission\":true,\"is_bonus\":false,\"is_once\":false,\"decline_reasons\":[{\"reason\":\"too_low_value\",\"minimum\":\"279\",\"value\":\"14\",\"key\":\"ride_count\"}],\"display_in_taximeter\":false,\"rule_display_in_taximeter\":false,\"driver_points\":null,\"clear_time\":null,\"group_id\":\"b61946a82c3a94dcd1395294dc1ffbf676ccfe63\"}],\"driver_id\":\"400000001383_76519554ac9948369f5e1797ee774487\",\"is_calculated\":false,\"is_fraud\":false,\"alias_id\":\"3b8ecd81784b4f7ab045bfa072801c52\",\"due\":ISODate(\"2018-10-24T19:32:00Z\"),\"updated\":ISODate(\"2018-10-25T09:07:09.002Z\"),\"version\":8,\"paid_commission\":\"0\",\"subvention_bonus\":[]}")]
        [InlineData(130.0,0.0,70.0,"{\"_id\":ObjectId(\"5bd09373099bfbac5f821a2b\"),\"order_id\":\"b3d09deb25662b5e1399d991c98df009\",\"tickets\":[],\"subvention_calc_rules\":[{\"id\":ObjectId(\"59ca185616e53027355b361c\"),\"sum\":0.0,\"type\":\"discount_payback\",\"is_fake\":false,\"is_holded\":false,\"sub_commission\":false,\"is_bonus\":true,\"is_once\":false,\"decline_reasons\":[],\"display_in_taximeter\":false,\"rule_display_in_taximeter\":false,\"driver_points\":null,\"clear_time\":null,\"group_id\":null,\"paid_sum\":\"0\"},{\"id\":ObjectId(\"5b86c7fa0e9d63004a5b6b48\"),\"sum\":180.0,\"type\":\"guarantee\",\"is_fake\":false,\"is_holded\":true,\"sub_commission\":true,\"is_bonus\":false,\"is_once\":false,\"decline_reasons\":[{\"till\":\"2018-10-26T04:38:47.878762\",\"reason\":\"holded\",\"key\":\"holded\"}],\"display_in_taximeter\":false,\"rule_display_in_taximeter\":true,\"driver_points\":41.0,\"clear_time\":ISODate(\"2018-10-26T04:38:47.878Z\"),\"group_id\":null},{\"id\":ObjectId(\"5b86ca8d0e9d63004a0d8d06\"),\"sum\":200.0,\"type\":\"guarantee\",\"is_fake\":false,\"is_holded\":true,\"sub_commission\":true,\"is_bonus\":false,\"is_once\":false,\"decline_reasons\":[{\"till\":\"2018-10-26T04:38:47.879006\",\"reason\":\"holded\",\"key\":\"holded\"}],\"display_in_taximeter\":false,\"rule_display_in_taximeter\":true,\"driver_points\":41.0,\"clear_time\":ISODate(\"2018-10-26T04:38:47.879Z\"),\"group_id\":null,\"paid_sum\":\"70.0\"},{\"id\":ObjectId(\"5b9cf5ca41e102a72fd4beb8\"),\"sum\":200.0,\"type\":\"guarantee\",\"is_fake\":false,\"is_holded\":true,\"sub_commission\":true,\"is_bonus\":false,\"is_once\":false,\"decline_reasons\":[{\"till\":\"2018-10-26T04:38:47.879078\",\"reason\":\"holded\",\"key\":\"holded\"}],\"display_in_taximeter\":false,\"rule_display_in_taximeter\":true,\"driver_points\":41.0,\"clear_time\":ISODate(\"2018-10-26T04:38:47.879Z\"),\"group_id\":null},{\"id\":ObjectId(\"5b9cf60a41e102a72fe71de5\"),\"sum\":200.0,\"type\":\"guarantee\",\"is_fake\":false,\"is_holded\":true,\"sub_commission\":true,\"is_bonus\":false,\"is_once\":false,\"decline_reasons\":[{\"till\":\"2018-10-26T04:38:47.879121\",\"reason\":\"holded\",\"key\":\"holded\"}],\"display_in_taximeter\":false,\"rule_display_in_taximeter\":true,\"driver_points\":41.0,\"clear_time\":ISODate(\"2018-10-26T04:38:47.879Z\"),\"group_id\":null},{\"id\":ObjectId(\"5b9cf67841e102a72f0704c8\"),\"sum\":200.0,\"type\":\"guarantee\",\"is_fake\":false,\"is_holded\":true,\"sub_commission\":true,\"is_bonus\":false,\"is_once\":false,\"decline_reasons\":[{\"till\":\"2018-10-26T04:38:47.879162\",\"reason\":\"holded\",\"key\":\"holded\"}],\"display_in_taximeter\":false,\"rule_display_in_taximeter\":true,\"driver_points\":41.0,\"clear_time\":ISODate(\"2018-10-26T04:38:47.879Z\"),\"group_id\":null},{\"id\":ObjectId(\"5b86c9fa0e9d63004ae59f88\"),\"sum\":90.0,\"type\":\"guarantee\",\"is_fake\":true,\"is_holded\":false,\"sub_commission\":true,\"is_bonus\":false,\"is_once\":false,\"decline_reasons\":[{\"reason\":\"too_low_value\",\"minimum\":\"199\",\"value\":\"19\",\"key\":\"ride_count\"}],\"display_in_taximeter\":false,\"rule_display_in_taximeter\":false,\"driver_points\":41.0,\"clear_time\":null,\"group_id\":\"1355ba47d4c29a8b670626a48adc5d285cdf39bb\"}],\"driver_id\":\"400000033085_43e16e32ecd846ffa5b66a67c77e5084\",\"is_calculated\":false,\"is_fraud\":false,\"alias_id\":\"f6d103e9420d46c7ac5c78de9884008f\",\"due\":ISODate(\"2018-10-24T15:48:00Z\"),\"updated\":ISODate(\"2018-10-25T04:38:52.227Z\"),\"version\":4,\"paid_commission\":\"10.4984600\",\"subvention_bonus\":[]}")]
        [InlineData(598.0, 44.87, 0.0, "{\"_id\":ObjectId(\"5bcf6073099bfbac5f1cb4c4\"),\"order_id\":\"28962fa5faaa9c017bcdcc93e81e137f\",\"tickets\":[],\"subvention_calc_rules\":[{\"id\":ObjectId(\"5aeb20cab14b1dc01a56f0a5\"),\"sum\":0.0,\"type\":\"discount_payback\",\"is_fake\":false,\"is_holded\":false,\"sub_commission\":false,\"is_bonus\":true,\"is_once\":false,\"decline_reasons\":[],\"display_in_taximeter\":false,\"rule_display_in_taximeter\":false,\"driver_points\":null,\"clear_time\":null,\"group_id\":null,\"paid_sum\":\"44.870\"},{\"id\":ObjectId(\"5b97a38e07d86bd2349bea25\"),\"sum\":200.0,\"type\":\"guarantee\",\"is_fake\":false,\"is_holded\":false,\"sub_commission\":true,\"is_bonus\":false,\"is_once\":false,\"decline_reasons\":[],\"display_in_taximeter\":true,\"rule_display_in_taximeter\":true,\"driver_points\":41.0,\"clear_time\":null,\"group_id\":null},{\"id\":ObjectId(\"58a55b5c23ab3516851381ff\"),\"sum\":200.0,\"type\":\"guarantee\",\"is_fake\":true,\"is_holded\":false,\"sub_commission\":true,\"is_bonus\":false,\"is_once\":false,\"decline_reasons\":[{\"reason\":\"too_low_value\",\"minimum\":\"279\",\"value\":\"12\",\"key\":\"ride_count\"}],\"display_in_taximeter\":false,\"rule_display_in_taximeter\":false,\"driver_points\":null,\"clear_time\":null,\"group_id\":\"b61946a82c3a94dcd1395294dc1ffbf676ccfe63\"}],\"driver_id\":\"1956791981_17ad397c0c094d489d5ae9d8a5d5c92b\",\"is_calculated\":false,\"is_fraud\":false,\"alias_id\":\"151af069179f462291f78cb14014525b\",\"due\":ISODate(\"2018-10-23T17:56:00Z\"),\"updated\":ISODate(\"2018-10-24T09:33:10.428Z\"),\"version\":6,\"paid_commission\":\"0\",\"subvention_bonus\":[]}")]
        [InlineData(86.0,114.0,0.0,"{\"_id\":ObjectId(\"5bd16a06099bfbac5f559c5a\"),\"order_id\":\"16cbc98bf9a922e298b95cfedc9bef6b\",\"tickets\":[],\"subvention_calc_rules\":[{\"rule_display_in_taximeter\":false,\"is_fake\":false,\"display_in_taximeter\":false,\"clear_time\":null,\"sum\":0.0,\"is_once\":false,\"decline_reasons\":[],\"sub_commission\":false,\"is_bonus\":true,\"driver_points\":null,\"id\":ObjectId(\"5aeb20cab14b1dc01a56f0a5\"),\"is_holded\":false,\"group_id\":null,\"type\":\"discount_payback\",\"paid_sum\":\"13.0\"},{\"rule_display_in_taximeter\":true,\"is_fake\":false,\"display_in_taximeter\":true,\"clear_time\":null,\"sum\":200.0,\"is_once\":false,\"decline_reasons\":[],\"sub_commission\":true,\"is_bonus\":false,\"driver_points\":41.0,\"id\":ObjectId(\"5b97a38e07d86bd2349bea25\"),\"is_holded\":false,\"group_id\":null,\"type\":\"guarantee\",\"paid_sum\":\"101.0\"},{\"rule_display_in_taximeter\":false,\"is_fake\":true,\"display_in_taximeter\":false,\"clear_time\":null,\"sum\":200.0,\"is_once\":false,\"decline_reasons\":[{\"reason\":\"too_low_value\",\"minimum\":\"279\",\"value\":\"4\",\"key\":\"ride_count\"}],\"sub_commission\":true,\"is_bonus\":false,\"driver_points\":null,\"is_holded\":false,\"group_id\":\"b61946a82c3a94dcd1395294dc1ffbf676ccfe63\",\"type\":\"guarantee\",\"id\":ObjectId(\"58a55b5c23ab3516851381ff\")}],\"driver_id\":\"1956793623_979e92602c8949b29c3f963b4ce1563e\",\"is_calculated\":false,\"is_fraud\":false,\"alias_id\":\"07ec9944b4ef481eaa2b1527e94058a5\",\"due\":ISODate(\"2018-10-25T07:11:00Z\"),\"updated\":ISODate(\"2018-10-25T07:46:20.955Z\"),\"version\":3,\"paid_commission\":\"21.45240\"}")]
        public void TestOrderSubventions_RealData(double orderCost, double expectedPaid, double expectedPromised, string reasonsJson)
        {
            var reasons = BsonSerializer.Deserialize<OrderSubventionReasonsDoc>(reasonsJson);
            var subventions = new OrderSubventions(reasons, (decimal)orderCost);
            subventions.PaidSum.Should().Be((decimal) expectedPaid);
            subventions.PromisedSum.Should().Be((decimal) expectedPromised);
        }
    }
}
