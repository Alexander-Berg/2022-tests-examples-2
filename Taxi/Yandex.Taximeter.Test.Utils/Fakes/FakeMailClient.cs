using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Yandex.Taximeter.Core.Clients;

namespace Yandex.Taximeter.Test.Utils.Fakes
{
    public class FakeMailClient : IMailClient
    {
        public List<SentMail> SentMails { get; } = new List<SentMail>();

        public class SentMail
        {
            public string From { get; set; }
            public string To { get; set; }
            public string Subject { get; set; }
            public string Body { get; set; }
            public Dictionary<string, string> Headers { get; set; }
            public Tuple<string, byte[]> File { get; set; }
        }

        public Task SendAsync(string @from, List<string> to, string subject, string body, Dictionary<string, string> header = null)
        {
            foreach (var receiver in to)
                SentMails.Add(new SentMail
                {
                    From = from,
                    To = receiver,
                    Subject = subject,
                    Body = body,
                    Headers = header
                });
            return Task.CompletedTask;
        }

        public Task SendAsync(string @from, List<string> to, string subject, string body, Dictionary<string, string> header, Tuple<string, byte[]> fileAttachment)
        {
            foreach (var receiver in to)
                SentMails.Add(new SentMail
                {
                    From = from,
                    To = receiver,
                    Subject = subject,
                    Body = body,
                    Headers = header,
                    File = fileAttachment
                });
            return Task.CompletedTask;

        }

        public Task SendToAllAsync(string db, string @from, string subject, string msg)
        {
            throw new NotImplementedException();
        }

        public Task<List<string>> GetMailsAsync(string db)
        {
            throw new NotImplementedException();
        }

        public Task SendFromTaximeterCronAsync(string subject, string body, Tuple<string, byte[]> file)
        {
            throw new NotImplementedException();
        }
    }
}