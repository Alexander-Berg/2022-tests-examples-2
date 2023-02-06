using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Utils;

namespace Yandex.Taximeter.Common.Tests.Utils
{
    public class EmailUtilitiesTests
    {
        [Fact]
        public void TestValidDomain()
        {
            EmailUtilities.IsValidDomain(".com").Should().BeTrue();
            EmailUtilities.IsValidDomain("com").Should().BeFalse();
            EmailUtilities.IsValidDomain(".comcomcom").Should().BeFalse();
            EmailUtilities.IsValidDomain("").Should().BeFalse();
            EmailUtilities.IsValidDomain(".рф").Should().BeTrue();
            EmailUtilities.IsValidDomain(".yandex").Should().BeTrue();
            EmailUtilities.IsValidDomain("fakeaddress.fakeaddress2.yandex").Should().BeTrue();
        }

        [Fact]
        public void TestValidEmail()
        {
            EmailUtilities.IsValidEmail("david.jones@proseware.com").Should().BeTrue();
            EmailUtilities.IsValidEmail("d.j@server1.proseware.com").Should().BeTrue();
            EmailUtilities.IsValidEmail("jones@ms1.proseware.com").Should().BeTrue();
            EmailUtilities.IsValidEmail("j.@server1.proseware.com").Should().BeFalse();
            EmailUtilities.IsValidEmail("j..s@proseware.com").Should().BeFalse();
            EmailUtilities.IsValidEmail("js@proseware.yandex").Should().BeTrue();
            EmailUtilities.IsValidEmail("igor@everest8800.comличная почта").Should().BeFalse();
            EmailUtilities.IsValidEmail("отсрочка 5 дней").Should().BeFalse();
            EmailUtilities.IsValidEmail("oooviva.taxi").Should().BeFalse();
            EmailUtilities.IsValidEmail("kuznetsova.katerina2017@yandex.ru / katerina2702198@gmail.com").Should().BeFalse();
            EmailUtilities.IsValidEmail("kuznetsova.katerina2017@yandex.ru/katerina2702198@gmail.com").Should().BeFalse();
            EmailUtilities.IsValidEmail("kuznetsova.katerina2017@yandex.ru;katerina2702198@gmail.com").Should().BeFalse();
            EmailUtilities.IsValidEmail("kuznetsova.katerina2017@yandex.ru.katerina2702198@gmail.com").Should().BeFalse();
            EmailUtilities.IsValidEmail("9096465033").Should().BeFalse();
            EmailUtilities.IsValidEmail("izvozchik-perm11139142@yandex.ruigorshumkov@permcabby.ru").Should().BeFalse();
            EmailUtilities.IsValidEmail("izvozchik-perm11139142@yandex.ruigorshumkov@permcabby.ru (личная)").Should().BeFalse();
            EmailUtilities.IsValidEmail("89123899494@mail.ru , Isaev.r.b@yandex.ru").Should().BeFalse();
            EmailUtilities.IsValidEmail("ИванПетров@почта.рф").Should().BeTrue();
        }
    }
}
