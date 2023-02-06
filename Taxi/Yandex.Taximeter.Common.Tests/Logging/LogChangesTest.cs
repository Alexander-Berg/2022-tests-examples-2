using System;
using System.Collections.Generic;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Admin.Areas.admin.Models;
using Yandex.Taximeter.Core.Models.Admin;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.City;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Country;
using Yandex.Taximeter.Core.Services.Log;

namespace Yandex.Taximeter.Common.Tests.Logging
{
    public class LogChangesTest
    {
        [Fact]
        public void TestAddCity()
        {
            var newCityModel = new CityViewModel
            {
                City = new CityDoc
                {
                    Country = Country.RUSSIA_NAME,
                    CountryId = Country.RUSSIA_ID,
                    Lat = 50.7,
                    Lon = 42.0,
                    Name = "Урюпинск",
                    TimeZone = 4
                }
            };

            var changes = CityViewModel.BuildChanges(null, newCityModel);
            changes.Should().BeEquivalentTo("<b>Добавлено:</b> Урюпинск (rus)");
        }

        [Fact]
        public void TestRemoveCity()
        {
            var oldCityModel = new CityViewModel
            {
                City = new CityDoc
                {
                    Country = Country.RUSSIA_NAME,
                    CountryId = Country.RUSSIA_ID,
                    Lat = 50.7,
                    Lon = 42.0,
                    Name = "Урюпинск",
                    TimeZone = 4
                }
            };

            var changes = CityViewModel.BuildChanges(oldCityModel, null);
            changes.Should().BeEquivalentTo("<b>Удалено:</b> Урюпинск (rus)");
        }

        [Fact]
        public void TestEditCity()
        {
            var oldCityModel = new CityViewModel
            {
                City = new CityDoc
                {
                    Country = Country.RUSSIA_NAME,
                    CountryId = Country.RUSSIA_ID,
                    Lat = 50.7,
                    Lon = 42.0,
                    Name = "Урюпинск",
                    TimeZone = 4
                }
            };

            var newCityModel = new CityViewModel
            {
                City = new CityDoc
                {
                    Country = Country.RUSSIA_NAME,
                    CountryId = Country.RUSSIA_ID,
                    Lat = 50.7,
                    Lon = 42.1,
                    Name = "Урюпинск",
                    TimeZone = 5
                }
            };

            var changes = CityViewModel.BuildChanges(oldCityModel, newCityModel);
            changes.Should().Be($"<b>Изменено:</b> Урюпинск (rus)<br/><ul><li>Координаты: 50.7,42 -> 50.7,42.1</li>{Environment.NewLine}<li>Часовой пояс: 4.00 -> 5.00</li></ul>");
        }

        [Fact]
        public void TestEditTaximeterVersion()
        {
            var oldModel = new TaximeterUpdateViewModel
            {
                CurrentVersion = "8.07",
                MinVersion = "8.06",
                Versions = new Dictionary<string, bool>
                {
                    {"8.07", false},
                    {"8.06", false},
                    {"8.05", true},
                    {"8.04", true},
                    {"8.03", true}
                }
            };

            var newModel = new TaximeterUpdateViewModel
            {
                CurrentVersion = "8.07",
                MinVersion = "8.06",
                Versions = new Dictionary<string, bool>
                {
                    {"8.07", false},
                    {"8.06", true},
                    {"8.05", false},
                    {"8.04", true},
                    {"8.03", true}
                }
            };

            var changes = TaximeterUpdateViewModel.BuildChanges(oldModel, newModel);
            changes.Should().BeEquivalentTo("<b>Изменено:</b> Версии таксометров<br/><ul><li>Запретить взятие заказов: добавлено: 8.06; удалено: 8.05; </li></ul>");
        }

        [Fact]
        public void TestDictionary()
        {
            var oldModel = new Dictionary<string, string>()
            {
                {"key1", "value1"},
                {"key2", "value2"},
                {"removed1", "removedValue1"},
                {"removed2", "removedValue2"},
                {"changed", "value"},
            };

            var newModel = new Dictionary<string, string>()
            {
                {"key1", "value1"},
                {"key2", "value2"},
                {"added1", "addedValue1"},
                {"added2", "addedValue2"},
                {"changed", "newValue"},
            };

            var builder = ChangesBuilderFactory.Create(oldModel, newModel, "Dictionary");
            builder.AddDictionary("Content", d => d);
            var changes = builder.ToString();
            changes.Should().BeEquivalentTo("<b>Изменено:</b> Dictionary<br/><ul><li>Content: добавлено: added1=addedValue1, added2=addedValue2; удалено: removed1=removedValue1, removed2=removedValue2; изменено: changed=(value -> newValue); </li></ul>");
        }
    }
}
