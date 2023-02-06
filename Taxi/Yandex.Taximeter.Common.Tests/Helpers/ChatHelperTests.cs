using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Models.Chat;

namespace Yandex.Taximeter.Common.Tests.Helpers
{
    public class ChatHelperTests
    {
        [Fact]
        public void Messages_ShouldBeCenzored_True()
        {
            AssertCenzored("авыа ! авыа аы а. https://www.youtube.com/watch?v=bj9JoTRgbtQ (change.org) авыаыв");
            AssertCenzored(" авыа ! авыа аы а. ffff.com/watch ?v=bj9JoTRgbtQ авыаыв");
        }

        [Fact]
        public void Messages_ShouldBeCenzored__False()
        {
            AssertNotCenzored("авыа ! авыа аы а. https://www.youtube.com/watch?v=bj9JoTRgbtQ авыаыв");
            AssertNotCenzored(" авыа ! авыа аы а. driver.yandex/watch?v=bj9JoTRgbtQ авыаыв");
            AssertNotCenzored("http?аыалыра раырв оар ыоора http");
            AssertNotCenzored(@"<img src=""/assets/emoticons/0001.png""><img src=""/assets/emoticons/0001.png"">fds");
            AssertNotCenzored(@"https://youtu.be/5U6V7VP3JGc");
            AssertNotCenzored(
                @"<img src=""/assets/emoticons/0118.png""><img src=""/assets/emoticons/0118.png""><img src=""/assets/emoticons/0119.png""><img src=""/assets/emoticons/0087.png""><img src=""/assets/emoticons/26a0.png""><img src=""/assets/emoticons/26a0.png""><img src=""/assets/emoticons/26a0.png"">");
            AssertNotCenzored("taxifm@taxifm.ru");
        }

        private void AssertNotCenzored(string msg)
        {
            ChatHelper.Messages.ShouldBeCenzored(new ChatItem
            {
                msg = msg
            }).Should().BeFalse();
        }

        private void AssertCenzored(string msg)
        {
            ChatHelper.Messages.ShouldBeCenzored(new ChatItem
            {
                msg = msg
            }).Should().BeTrue();
        }
    }
}
