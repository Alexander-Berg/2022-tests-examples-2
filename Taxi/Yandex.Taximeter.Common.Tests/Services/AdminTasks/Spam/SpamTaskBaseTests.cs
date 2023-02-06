using System;
using Xunit;
using Yandex.Taximeter.Core.Services.AdminTasks.Spam;
using Yandex.Taximeter.Core.Services.AdminTasks.Spam.Model;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Services.AdminTasks.Spam
{
    public class SpamTaskBaseTests
    {
        [Fact]
        public void Serialization_DriversSpamTask_SerializesAndDeserializes()
        {
            TestUtils.CheckJsonSerialization<SpamTaskBase>(new DriversSpamTask
            {
                AuthorLogin = "login",
                Cities = new[] { "city1", "city2" },
                Filter = DriversSpamTaskFilter.Offline,
                Message = "msg",
                SenderLogin = "sender",
                CreationTime = DateTime.Today,
                UpdateTime = DateTime.Today
            }, new SpamTaskConverter());
        }

        [Fact]
        public void Serialization_ClientsSpamTask_SerializesAndDeserializes()
        {
            TestUtils.CheckJsonSerialization<SpamTaskBase>(new ClientSpamTask
            {
                AuthorLogin = "login",
                Cities = new [] { "city1", "city2"},
                Filter = ClientSpamTaskFilter.Archive,
                Message = "msg",
                Subject = "subj",
                SenderLogin = "sender",
                CreationTime = DateTime.Today,
                UpdateTime = DateTime.Today
            }, new SpamTaskConverter());
        }
    }
}