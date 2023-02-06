using System;
using Newtonsoft.Json;

namespace Yandex.Taximeter.Test.Utils.Redis
{
    internal class SerializedRedisItem : IRedisValue
    {
        public SerializedRedisItem(object value)
        {
            Value = value;
        }

        public SerializedRedisItem(object value, TimeSpan expireTimeout)
        {
            Value = value;
            ExpireDate = DateTime.Now + expireTimeout;
        }

        public object Value { get; }

        public DateTime? ExpireDate { get; private set; }
        public void Expire(TimeSpan timeout)
        {
            ExpireDate = DateTime.Now + timeout;
        }

        public override string ToString()
        {
            if (Value == null)
                return null;
            if (Value is string)
                return (string)Value;
            return JsonConvert.SerializeObject(Value);
        }

        public T ConvertValue<T>()
        {
            if (Value == null)
                return default(T);
            if (Value is T)
                return (T) Value;
            if (Value is string)
                return JsonConvert.DeserializeObject<T>((string) Value);
            return JsonConvert.DeserializeObject<T>(
                JsonConvert.SerializeObject(Value));
        }
    }
}