using System;
using System.Globalization;
using System.Linq;
using System.Threading.Tasks;
using FluentAssertions;
using Moq;
using Newtonsoft.Json;
using Xunit;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Services;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Services.Driver
{
    public class DriverPositionServiceTests
    {
        [Fact]
        public async Task DriverTrackTest_MileageAndTime()
        {
            var driverPositions = new[]
            {
                "{'U':'2018-10-30T20:51:54','S':1,'L':53.5086438,'O':49.282022}",
                "{'U':'2018-10-30T20:52:59','S':1,'L':53.5078367,'O':49.2832251}",
                "{'U':'2018-10-30T20:53:56','S':1,'L':53.5085012,'O':49.2867834}",
                "{'U':'2018-10-30T20:54:53','S':2,'L':53.5092317,'O':49.2871297}",
                "{'U':'2018-10-30T20:55:53','S':2,'L':53.5092073,'O':49.2871068}",
                "{'U':'2018-10-30T20:56:51','S':2,'L':53.5092665,'O':49.2869729}",
                "{'U':'2018-10-30T20:57:57','S':3,'L':53.5092017,'O':49.2870494}",
                "{'U':'2018-10-30T20:58:54','S':3,'L':53.508249,'O':49.2896477}",
                "{'U':'2018-10-30T20:59:57','S':3,'L':53.50674,'O':49.2916808}",
                "{'U':'2018-10-30T21:00:54','S':3,'L':53.5052136,'O':49.2929209}",
                "{'U':'2018-10-30T21:01:52','S':3,'L':53.5069089,'O':49.301569}",
                "{'U':'2018-10-30T21:02:58','S':3,'L':53.512059,'O':49.3055777}",
                "{'U':'2018-10-30T21:03:54','S':3,'L':53.5159644,'O':49.308902}",
                "{'U':'2018-10-30T21:04:51','S':3,'L':53.5204269,'O':49.3170144}",
                "{'U':'2018-10-30T21:05:58','S':3,'L':53.5241219,'O':49.3254536}",
                "{'U':'2018-10-30T21:06:57','S':3,'L':53.5280506,'O':49.327285}",
                "{'U':'2018-10-30T21:07:59','S':3,'L':53.5331913,'O':49.328612}",
                "{'U':'2018-10-30T21:08:59','S':3,'L':53.5391277,'O':49.3300478}",
                "{'U':'2018-10-30T21:09:52','S':3,'L':53.5412711,'O':49.330352}",
                "{'U':'2018-10-30T21:10:55','S':3,'L':53.5393797,'O':49.3267656}",
                "{'U':'2018-10-30T21:11:53','S':3,'L':53.5382752,'O':49.3252679}",
                "{'U':'2018-10-30T21:12:51','S':2,'L':53.5381495,'O':49.3253477}"
            }.Select(JsonConvert.DeserializeObject<DriverPositionLog>).ToArray();
            
            var service = new Mock<IDriverPositionService>();
            service.Setup(x => x.FindHistoryAsync("park_id", "driver_id", It.IsAny<DateTime>(), It.IsAny<DateTime>())).ReturnsAsync(driverPositions);
            var driverTrack = await service.Object.GetDriverTrack("park_id", "driver_id", CultureInfo.CurrentUICulture,
                0d, DateTime.UtcNow, DateTime.UtcNow);
            
            driverTrack.Select(x => Math.Round(x.distance, 1)).Should().BeEquivalentTo(0.0, 0.1, 0.4, 0.0, 0.0, 0.0, 0.0, 0.2, 0.4, 0.6, 1.2, 1.8, 2.3, 3.1, 3.7, 4.2, 4.8, 5.4, 5.7, 6.0, 6.2, 0.0);
            driverTrack.Select(x => Math.Round(x.time.TotalMinutes, 0)).Should().BeEquivalentTo(0.0, 1.0, 2.0, 0.0, 1.0, 2.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 0.0);
        }
    }
}
