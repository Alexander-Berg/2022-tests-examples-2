using System;
using Yandex.Taximeter.Core.Services.Driver;

namespace Yandex.Taximeter.Common.Tests.Services.Driver.Fakes
{
    public class FakeTaxiDriverData
    {
        public FakeTaxiDriverData(string db, DateTime rateUpdateTime, DriverRates rates)
        {
            Db = db;
            RateUpdateTime = rateUpdateTime;
            Rates = rates;
        }

        public string Db { get; }
        public DateTime RateUpdateTime { get; }
        public DriverRates Rates { get; }
    }
}