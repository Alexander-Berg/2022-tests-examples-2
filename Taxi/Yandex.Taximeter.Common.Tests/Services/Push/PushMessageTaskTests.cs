using FluentAssertions;
using Newtonsoft.Json;
using Xunit;
using Yandex.Taximeter.Core.Services.Push;
using Yandex.Taximeter.Core.Services.Push.Messages;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Services.Push
{
    public class PushMessageTaskTests
    {
        [Fact]
        public void Serialization_NotNullData_SerializesAndDeserializes()
        {
            var taskBalance = new PushBalance
            {
                Balance = 1.5,
                Limit = 100
            };
            var task = new PushMessageTask(taskBalance)
            {
                Action = PushMessageAction.MessageRate,
                Db = TestUtils.NewId(),
                Driver = TestUtils.NewId()
            };
            var serialized = JsonConvert.SerializeObject(task);
            var deserialized = JsonConvert.DeserializeObject<PushMessageTask>(serialized);
            var deserializedBalance = deserialized.ConvertData<PushBalance>();

            deserialized.Action.Should().Be(task.Action);
            deserialized.Db.Should().Be(task.Db);
            deserialized.Driver.Should().Be(task.Driver);
            deserializedBalance.Limit.Should().Be(taskBalance.Limit);
            deserializedBalance.Balance.Should().Be(taskBalance.Balance);
        }

        [Fact]
        public void Serialization_PrimitiveData_SerializesAndDeserializes()
        {
            var task = new PushMessageTask(true)
            {
                Action = PushMessageAction.MessageRate,
                Db = TestUtils.NewId(),
                Driver = TestUtils.NewId()
            };
            var serialized = JsonConvert.SerializeObject(task);
            var deserialized = JsonConvert.DeserializeObject<PushMessageTask>(serialized);

            deserialized.Action.Should().Be(task.Action);
            deserialized.Db.Should().Be(task.Db);
            deserialized.Driver.Should().Be(task.Driver);
            deserialized.ConvertData<bool>().Should().Be(true);
        }
        
        [Fact]
        public void Serialization_TypeConversion_SerializesAndDeserializes()
        {
            var task = new PushMessageTask(100)
            {
                Action = PushMessageAction.MessageRate,
                Db = TestUtils.NewId(),
                Driver = TestUtils.NewId()
            };
            var serialized = JsonConvert.SerializeObject(task);
            var deserialized = JsonConvert.DeserializeObject<PushMessageTask>(serialized);

            deserialized.Action.Should().Be(task.Action);
            deserialized.Db.Should().Be(task.Db);
            deserialized.Driver.Should().Be(task.Driver);
            deserialized.ConvertData<long>().Should().Be(100L);
        }
    }
}