using System.Collections.Generic;
using System.Collections.Immutable;
using System.Linq;
using System.Reflection;
using System.Threading.Tasks;
using Moq;
using Xunit;
using Xunit.Sdk;
using Yandex.Taximeter.Core.Extensions;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Repositories;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Car;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Park;
using Yandex.Taximeter.Core.Repositories.MongoDB.Dtos.Car;
using Yandex.Taximeter.Core.Repositories.MongoDB.Dtos.Driver;
using Yandex.Taximeter.Core.Repositories.MongoDB.Dtos.Park;

namespace Yandex.Taximeter.Common.Tests.Clients
{
    [Collection(nameof(YandexClientTestsBase))]
    public class YandexClientCarCategoriesTests : YandexClientTestsBase
    {
        private async Task TestCategories(
            CategoryFlags carCategories,
            HashSet<ParkRobotSettings> parkSettings,
            RobotHelper.Setting driverRestrictions,
            CategoryFlags expectedCategories
        )
        {            
            ParkRepository.Setup(x => x.GetDtoAsync<ParkSettingsDto>(Db, It.IsAny<QueryMode>()))
                .ReturnsAsync(new ParkSettingsDto
                {
                    Id = Db, 
                    RobotSettings = parkSettings.ToHashSet()
                });

            DriverRepository.Setup(x => x.GetAsync<DriverDtoBase>(Db, Driver, It.IsAny<QueryMode>(), It.IsAny<string>(), It.IsAny<string>(), It.IsAny<int>()))
                .ReturnsAsync(new DriverDtoBase
                {
                    DriverId = Driver,
                    ParkId = Db,
                });
            
            CarRepository.Setup(x => x.GetAsync<CarCategoryDto>(Db, Car,  It.IsAny<QueryMode>()))
                .ReturnsAsync(new CarCategoryDto
                {
                    CarId = Car,
                    ParkId = Db,
                    Category = (CarCategory) carCategories
                });
            
            await RobotHelper.Driver.Settings.RemoveAsync(Db, Driver);
            foreach (var setting in driverRestrictions.ToFlags())
            {
                await RobotHelper.Driver.Settings.SetAsync(Db, Driver, setting, true);
            }

            var categories = await YandexClient.LoadCarCategory(Driver, Car);
            if (expectedCategories != categories)
            {
                var park = await ParkRepository.Object.GetDtoAsync<ParkSettingsDto>(Db);
                var parkExcludedFlags = ParkTariffSettings.Except(park.RobotSettings).ToList();
                var parkIncludedFlags = park.RobotSettings.Except(ParkTariffSettings).ToList();
                var parkStr = "(ALL)";
                if (parkExcludedFlags.Any()) parkStr += $" - ({string.Join(", ", parkExcludedFlags)})";
                if (parkIncludedFlags.Any()) parkStr += $" + ({string.Join(", ", parkIncludedFlags)})";

                var driverActualRestrictions = await RobotHelper.Driver.Settings.GetAsync(Db, Driver);

                var car = await CarRepository.Object.GetAsync<CarCategoryDto>(Db, Car);
                
                throw new AssertActualExpectedException(
                    expectedCategories,
                    categories, 
                    $"Categories not equal: park={parkStr} car={car.CategoryFlags()} driver={driverActualRestrictions}",
                    nameof(expectedCategories),
                    nameof(categories));
            }
        }

        private static readonly ISet<ParkRobotSettings> ParkTariffSettings =
            typeof(ParkRobotSettings)
                .GetFields(BindingFlags.Static | BindingFlags.Public)
                .Where(x => x.Name.StartsWith("Disable"))
                .Select(x => (ParkRobotSettings)x.GetValue(null))
                .ToImmutableHashSet();

        public HashSet<ParkRobotSettings> MakeSettings(bool commonSettingsEnabled,
            params ParkRobotSettings[] excludedTariffSettings)
        {
            var result = new HashSet<ParkRobotSettings>(ParkTariffSettings);
            if (commonSettingsEnabled) result.Add(ParkRobotSettings.CommonSettingsEnabled);
           
            foreach (var s in excludedTariffSettings)
            {
                result.Remove(s);
            }

            return result;
        }

        [Fact]
        public async Task TestCarCategories_Simple()
        {
            await TestCategories(
                CategoryFlags.Econom | CategoryFlags.Comfort,
                MakeSettings(true, ParkRobotSettings.DisableEconom),
                RobotHelper.Setting.ЭКОНОМ_Disable,
                CategoryFlags.Comfort
            );
        }

        [Fact]
        public async Task TestCarCategories_CommonSettingsDisabled()
        {
            await TestCategories(
                CategoryFlags.Econom | CategoryFlags.Comfort,
                MakeSettings(false, ParkRobotSettings.DisableEconom),
                RobotHelper.Setting.ЭКОНОМ_Disable,
                CategoryFlags.Econom | CategoryFlags.Comfort
            );
        }

        [Fact]
        public async Task TestCarCategories_RealDriver1()
        {
            await TestCategories(
                CategoryFlags.Econom | CategoryFlags.Comfort | CategoryFlags.ComfortPlus |
                CategoryFlags.Business | CategoryFlags.Start | CategoryFlags.Standard,
                new HashSet<ParkRobotSettings>
                {
                    ParkRobotSettings.CommonSettingsEnabled
                },
                RobotHelper.Setting.Standard_Disable | RobotHelper.Setting.Start_Disable |
                RobotHelper.Setting.БИЗНЕС_Disable,
                CategoryFlags.Econom | CategoryFlags.Comfort | CategoryFlags.ComfortPlus
            );
        }
        
        [Fact]
        public async Task TestCarCategories_RealDriver2()
        {
            await TestCategories(
                CategoryFlags.Econom | CategoryFlags.Comfort | CategoryFlags.ComfortPlus |
                CategoryFlags.Start | CategoryFlags.Express,
                new HashSet<ParkRobotSettings>
                {
                    ParkRobotSettings.CommonSettingsEnabled,
                    ParkRobotSettings.Robot,
                    ParkRobotSettings.DisableExpress
                },
                RobotHelper.Setting.Standard_Disable | RobotHelper.Setting.Start_Disable | 
                RobotHelper.Setting.Express_Disable | RobotHelper.Setting.УНИВЕРСАЛ_Disable | 
                RobotHelper.Setting.МИНИВЭН_Disable | RobotHelper.Setting.БИЗНЕС_Disable,
                CategoryFlags.Comfort | CategoryFlags.ComfortPlus | CategoryFlags.Econom
            );
        }
        
        [Fact]
        public async Task TestCarCategories_RealDriver2NoCommonSettings()
        {
            await TestCategories(
                CategoryFlags.Econom | CategoryFlags.Comfort | CategoryFlags.ComfortPlus |
                CategoryFlags.Start | CategoryFlags.Express,
                new HashSet<ParkRobotSettings>
                {
                    ParkRobotSettings.DisableExpress
                },
                RobotHelper.Setting.Standard_Disable | RobotHelper.Setting.Start_Disable | 
                RobotHelper.Setting.Express_Disable | RobotHelper.Setting.УНИВЕРСАЛ_Disable | 
                RobotHelper.Setting.МИНИВЭН_Disable | RobotHelper.Setting.БИЗНЕС_Disable,
                CategoryFlags.Comfort | CategoryFlags.ComfortPlus | CategoryFlags.Econom | 
                CategoryFlags.Start
            );
        }
        
        [Fact]
        public async Task TestCarCategories_RealDriver3()
        {
            await TestCategories(
                CategoryFlags.Econom | CategoryFlags.Comfort | CategoryFlags.Minivan |
                CategoryFlags.Start | CategoryFlags.Standard | CategoryFlags.Express,
                new HashSet<ParkRobotSettings>
                {
                    ParkRobotSettings.CommonSettingsEnabled, 
                    ParkRobotSettings.Robot,
                    ParkRobotSettings.DisableExpress,
                    ParkRobotSettings.DisableBusiness
                },
                RobotHelper.Setting.УНИВЕРСАЛ_Disable | RobotHelper.Setting.КОМФОРТПЛЮС_Disable |
                RobotHelper.Setting.БИЗНЕС_Disable,
                CategoryFlags.Econom | CategoryFlags.Start | CategoryFlags.Minivan | 
                CategoryFlags.Comfort | CategoryFlags.Express | CategoryFlags.Standard
            );
        }
        
        [Fact]
        public async Task TestCarCategories_RealDriver3NoCommonSettings()
        {
            await TestCategories(
                CategoryFlags.Econom | CategoryFlags.Comfort | CategoryFlags.Minivan |
                CategoryFlags.Start | CategoryFlags.Standard | CategoryFlags.Express,
                new HashSet<ParkRobotSettings>
                {
                    ParkRobotSettings.DisableExpress,
                    ParkRobotSettings.DisableBusiness
                },
                RobotHelper.Setting.УНИВЕРСАЛ_Disable | RobotHelper.Setting.КОМФОРТПЛЮС_Disable |
                RobotHelper.Setting.БИЗНЕС_Disable,
                CategoryFlags.Econom | CategoryFlags.Start | CategoryFlags.Minivan | 
                CategoryFlags.Comfort | CategoryFlags.Express | CategoryFlags.Standard
            );
        }
    }
        

}