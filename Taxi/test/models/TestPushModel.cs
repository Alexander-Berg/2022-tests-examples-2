using Yandex.Taximeter.Core.Services.Push;

namespace Yandex.Taximeter.Admin.Areas.test.Models
{
    public class TestPushModel
    {
        public string Db { get; set; }

        public string Driver { get; set; }

        public string Topic { get; set; }

        public PushMessageAction PushType { get; set; }

        public string Provider { get; set; }
        
        public string Json { get; set; }

        public string Result { get; set; }

        public bool UseMessageQueue { get; set; }
    }
}
