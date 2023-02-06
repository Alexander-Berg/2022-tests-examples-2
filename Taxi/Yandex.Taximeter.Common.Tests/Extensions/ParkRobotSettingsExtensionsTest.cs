using System.Collections.Generic;
using Xunit;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Car;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Park;

namespace Yandex.Taximeter.Common.Tests.Extensions
{
    public class ParkRobotSettingsExtensionsTest
    {
        [Fact]
        public void TestParkRobotSettingsExtensions_ToParkCategories_CommonSettingsEnabled()
        {
            var categories = new HashSet<ParkRobotSettings>
            {
                ParkRobotSettings.CommonSettingsEnabled,
                ParkRobotSettings.Robot,
                ParkRobotSettings.DisableBusiness,
                ParkRobotSettings.DisableMinivan,
                ParkRobotSettings.DisableComfortPlus,
                ParkRobotSettings.DisableWagon,
                ParkRobotSettings.DisableExpress
            };

            var expectedCategories = ParkRobotSettingsExtensions.AllCategoryFlags;
            
            Assert.Equal(expectedCategories, categories.GetParkCategories());
        }
        
        [Fact]
        public void TestParkRobotSettingsExtensions_ToParkCategories_CommonSettingsDisabled()
        {
            var categories = new HashSet<ParkRobotSettings>
            {
                ParkRobotSettings.Robot,
                ParkRobotSettings.DisableBusiness,
                ParkRobotSettings.DisableMinivan,
                ParkRobotSettings.DisableComfortPlus,
                ParkRobotSettings.DisableWagon,
                ParkRobotSettings.DisableExpress
            };

            var expectedCategories = ParkRobotSettingsExtensions.AllCategoryFlags &
                                     (CategoryFlags.Business | CategoryFlags.Minivan |
                                      CategoryFlags.ComfortPlus | CategoryFlags.Wagon | CategoryFlags.Express);
            
            
            Assert.Equal(expectedCategories, categories.GetParkCategories());
        }
    }
}
