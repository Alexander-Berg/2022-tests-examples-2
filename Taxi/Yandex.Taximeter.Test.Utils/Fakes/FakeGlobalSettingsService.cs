using System.Threading.Tasks;
using Yandex.Taximeter.Core.Services.Settings;

namespace Yandex.Taximeter.Test.Utils.Fakes
{
    public class FakeGlobalSettingsService : IGlobalSettingsService
    {
        public GlobalSettings GlobalSettings { get; set; } = new GlobalSettings();

        public ValueTask<GlobalSettings> GetAsync() => new ValueTask<GlobalSettings>(GlobalSettings);

        public void StartUpdateCycle()
        {}
    }
}