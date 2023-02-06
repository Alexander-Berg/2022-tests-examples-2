using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using Yandex.Taximeter.Core;
using Yandex.Taximeter.Core.Clients;
using Yandex.Taximeter.Core.Extensions;
using Yandex.Taximeter.Core.Helper;

namespace Yandex.Taximeter.ScriptRunner.Scripts
{
    /// <summary>
    /// Relates: TAXIMETERBACK-3696
    /// </summary>
    public class TestRatingLoader : CustomScriptBase
    {
        private readonly ITaxiClient _taxiClient;

        public TestRatingLoader(ILoggerFactory loggerFactory, ITaxiClient taxiClient) 
            : base("test_rating_loader", loggerFactory)
        {
            _taxiClient = taxiClient;
        }

        public override async Task RunAsync(string[] args, TextWriter output, CancellationToken ct)
        {
            Items data = null;
            var url = "utils/1.0/drivers_rating_bulk";
            using (var client = _taxiClient.CreateDevUtils(128000))
            {
                for (var i = 1; i <= 4; i++)
                {
                    try
                    {
                        using (var response = await client.GetAsync(url))
                        {
                            var serializer = new JsonSerializer();
                            using (var responseStream = await response.Content.ReadAsStreamAsync())
                            using (var streamReader = new StreamReader(responseStream, Encoding.UTF8))
                            using (var jsonReader = new JsonTextReader(streamReader))
                            {
                                data = serializer.Deserialize<Items>(jsonReader);
                            }
                        }
                        break;
                    }
                    catch (WebException ex)
                    {
                        Logger.LogError(ex);
                        // повторим N раз если ЯТ кабинет дал 502 ошибку
                        if (i != 4)
                        {
                            await Task.Delay(200).ConfigureAwait(false);
                            continue;
                        }
                        throw;
                    }
                }
            }
            Logger.LogInformation($"data loaded using streams: {data?.drivers.Count}. {data?.parks2cities.Count}");
            
            using (var client = _taxiClient.CreateDevUtils(128000))
            {
                for (var i = 1; i <= 4; i++)
                {
                    try
                    {
                        var json = await client.GetStringAsync(url);
                        data = JsonConvert.DeserializeObject<Items>(json);
                        break;
                    }
                    catch (WebException ex)
                    {
                        Logger.LogError(ex);
                        // повторим N раз если ЯТ кабинет дал 502 ошибку
                        if (i != 4)
                        {
                            await Task.Delay(200).ConfigureAwait(false);
                            continue;
                        }
                        throw;
                    }
                }
            }
            Logger.LogInformation($"data loaded using GetStringAsync: {data?.drivers.Count}. {data?.parks2cities.Count}");
        }
        
        class Items
        {
            public List<DriverHelper.Rating.Yandex.Item> drivers { get; set; }

            public DriverHelper.Rating.Yandex.E_Settings.Item E_settings { get; set; }

            [JsonProperty("settings")]
            public DriverHelper.Rating.Yandex.Settings.Item Settings { get; set; }

            [JsonProperty("acceptance_rate_settings")]
            public List<DriverHelper.Rating.Yandex.AcceptanceRate_Settings.Item> AcceptanceRateSettings { get; set; } = new List<DriverHelper.Rating.Yandex.AcceptanceRate_Settings.Item>();

            [JsonProperty("completed_rate_settings")]
            public List<DriverHelper.Rating.Yandex.CompletionRate_Settings.Item> CompletionRateSettings { get; set; } = new List<DriverHelper.Rating.Yandex.CompletionRate_Settings.Item>();

            public List<DriverHelper.Rating.Yandex.L_Settings.Item> L_settings { get; set; }

            public List<CityItem> parks2cities { get; set; }
        }
        
        public class CityItem
        {
            public string clid { get; set; }
            public string city { get; set; }
        }
    }
}