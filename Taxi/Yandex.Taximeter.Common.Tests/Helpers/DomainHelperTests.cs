//using System;
//using FluentAssertions;
//using Xunit;
//using Yandex.Taximeter.Core.Dto.Billing;
//using Yandex.Taximeter.Core.Repositories.Sql.Entities;
//using Yandex.Taximeter.Core.Helper;
//
//namespace Yandex.Taximeter.Core.Tests.Helpers
//{
//    public class DomainHelperTests
//    {
//        // UpdateLicenseUsedQty tests
//
//        [Fact]
//        public void NewLicenseFirstUpdateTest()
//        {
//            var license = new ParkLicense
//            {
//                Start = new DateTime(2016, 5, 24),
//                End = new DateTime(2016, 6, 22),
//                UsedQty = 0,
//                UsedUpdated = new DateTime(2016, 5, 24)
//            };
//
//            // First day (license is created with UsedQty = 1
//            var now = new DateTime(2016, 5, 24);
//            var result = DomainHelper.YandexBalance.Order.CalcUsedDays(now, license);
//            result.Should().Be(1);
//
//            // Second day
//            now = new DateTime(2016, 5, 25);
//            result = DomainHelper.YandexBalance.Order.CalcUsedDays(now, license);
//            result.Should().Be(2);
//
//            // Third day
//            now = new DateTime(2016, 5, 26);
//            result = DomainHelper.YandexBalance.Order.CalcUsedDays(now, license);
//            result.Should().Be(3);
//
//            // Last day - 1
//            now = new DateTime(2016, 6, 21);
//            result = DomainHelper.YandexBalance.Order.CalcUsedDays(now, license);
//            result.Should().Be(29);
//
//            // Last day
//            now = new DateTime(2016, 6, 22);
//            result = DomainHelper.YandexBalance.Order.CalcUsedDays(now, license);
//            result.Should().Be(30);
//
//            // Last day + 1
//            now = new DateTime(2016, 6, 24);
//            result = DomainHelper.YandexBalance.Order.CalcUsedDays(now, license);
//            result.Should().Be(30);
//
//            // Last day + 2
//            now = new DateTime(2016, 6, 25);
//            result = DomainHelper.YandexBalance.Order.CalcUsedDays(now, license);
//            result.Should().Be(30);
//        }
//
//        [Fact]
//        public void ExistingLicenseUpdateTest()
//        {
//            var license = new ParkLicense
//            {
//                Start = new DateTime(2016, 5, 24),
//                End = new DateTime(2016, 6, 22),
//                UsedQty = 1,
//                UsedUpdated = new DateTime(2016, 5, 24)
//            };
//
//            // First day (license is created with UsedQty = 1
//            var now = new DateTime(2016, 5, 24);
//            var result = DomainHelper.YandexBalance.Order.CalcUsedDays(now, license);
//            result.Should().Be(0);
//
//            // Second day
//            now = new DateTime(2016, 5, 25);
//            result = DomainHelper.YandexBalance.Order.CalcUsedDays(now, license);
//            result.Should().Be(1);
//
//            // Third day
//            now = new DateTime(2016, 5, 26);
//            result = DomainHelper.YandexBalance.Order.CalcUsedDays(now, license);
//            result.Should().Be(2);
//
//            // Last day - 1
//            now = new DateTime(2016, 6, 21);
//            result = DomainHelper.YandexBalance.Order.CalcUsedDays(now, license);
//            result.Should().Be(28);
//
//            // Last day
//            now = new DateTime(2016, 6, 22);
//            result = DomainHelper.YandexBalance.Order.CalcUsedDays(now, license);
//            result.Should().Be(29);
//
//            // Last day + 1
//            now = new DateTime(2016, 6, 24);
//            result = DomainHelper.YandexBalance.Order.CalcUsedDays(now, license);
//            result.Should().Be(29);
//
//            // Last day + 2
//            now = new DateTime(2016, 6, 25);
//            result = DomainHelper.YandexBalance.Order.CalcUsedDays(now, license);
//            result.Should().Be(29);
//        }
//    }
//}
