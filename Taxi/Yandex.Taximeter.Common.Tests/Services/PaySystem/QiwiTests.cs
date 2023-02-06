using System;
using System.Collections.Generic;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Services.PaySystem.QiwiContracts;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Services.PaySystem
{
    public class QiwiTests
    {
        [Fact]
        public void SerializationTest_SimpleRequest()
        {
            var request = new Request
            {
                Phone = "0000000000",
                RequestType = "test"
            };
            TestUtils.CheckXmlSerialization(@"<?xml version=""1.0"" encoding=""utf-8""?>
                <request>
                    <request-type>test</request-type>
                    <protocol-version>4.00</protocol-version>
                    <terminal-id>0000000000</terminal-id>
                </request>", request);
        }

        [Fact]
        public void SerializationTest_RequestWithExtra()
        {
            var request = new Request
            {
                Phone = "0000000000",
                RequestType = "test",
                Parameters = new List<ExtraParameter>()
                {
                    new ExtraParameter {  Name = "token", Value = "123456abcdef" }
                }
            };
            TestUtils.CheckXmlSerialization(@"<?xml version=""1.0"" encoding=""utf-8""?>
                <request>
                    <request-type>test</request-type>
                    <protocol-version>4.00</protocol-version>
                    <extra name=""token"">123456abcdef</extra>
                    <terminal-id>0000000000</terminal-id>
                </request>", request);
        }

        [Fact]
        public void SerializationTest_StatusBillRequest()
        {
            var request = new StatusBillRequest()
            {
                Phone = "0000000000",
                RequestType = "test",
                Parameters = new List<ExtraParameter>()
                {
                    new ExtraParameter {  Name = "token", Value = "123456abcdef" }
                },
                BillsList = new []
                {
                    new Bill { TxnId = "123" }
                }
            };
            TestUtils.CheckXmlSerialization(@"<?xml version=""1.0"" encoding=""utf-8""?>
                <request>
                    <request-type>test</request-type>
                    <protocol-version>4.00</protocol-version>
                    <extra name=""token"">123456abcdef</extra>
                    <terminal-id>0000000000</terminal-id>
                    <bills-list>
                        <bill txn-id=""123"" status=""0"" sum=""0"" currency=""0""/>
                    </bills-list>
                </request>", request);
        }

        [Fact]
        public void SerializationTest_AuthRequest()
        {
            var request = new AuthRequest()
            {
                Phone = "0000000000",
                RequestType = "auth",
                Password = "Qwerty123" 
            };
            TestUtils.CheckXmlSerialization(@"<?xml version=""1.0"" encoding=""utf-8""?>
                <request>
                    <request-type>auth</request-type>
                    <auth-version>2.0</auth-version>
                    <phone>0000000000</phone>
                    <password>Qwerty123</password>
                    <client-id>android</client-id>
                </request>", request);
        }

        [Fact]
        public void SerializationTest_GetPaymentsReportRequest()
        {
            var request = new GetPaymentsReportRequest()
            {
                Phone = "0000000000",
                RequestType = "get-payments-report",
                Parameters = new List<ExtraParameter>()
                {
                    new ExtraParameter {  Name = "token", Value = "123456abcdef" },
                    new ExtraParameter { Name = "client-software", Value = "android" },
                    new ExtraParameter { Name = "udid", Value = "000000000000" },
                },
                FromDate = "01.01.2016",
                ToDate = "31.12.2016",
                Full = 1,
                Period = "custom"
            };
            TestUtils.CheckXmlSerialization(@"<?xml version=""1.0"" encoding=""utf-8""?>
              <request>
                  <request-type>get-payments-report</request-type>
                  <protocol-version>4.00</protocol-version>
                  <extra name=""token"">123456abcdef</extra>
                  <extra name=""client-software"">android</extra>
                  <extra name=""udid"">000000000000</extra>
                  <terminal-id>0000000000</terminal-id>
                  <period>custom</period>
                  <from-date>01.01.2016</from-date>
                  <to-date>31.12.2016</to-date>
                  <full>1</full>
                </request>", request);
        }

        [Fact]
        public void DeserializationTest_SimpleResponse()
        {
            var response = StaticHelper.FromXml<Response>(@"<?xml version=""1.0"" encoding=""utf-8""?>
                <response>
                    <result-code fatal=""false"" message=""Ok"" msg=""Ok"">0</result-code>
                </response>");
            response.ResultCode.Message.Should().BeEquivalentTo("Ok");
            response.ResultCode.Value.Should().Be(0);
            response.ResultCode.Fatal.Should().Be(false);
        }

        [Fact]
        public void DeserializationTest_AuthResponse()
        {
            var response = StaticHelper.FromXml<AuthResponse>(@"<?xml version=""1.0"" encoding=""utf-8""?>
                <response>
                    <result-code>0</result-code>
                    <access-token>123456abcdef</access-token>
                </response>");
            response.ResultCode.Value.Should().Be(0);
            response.AccessToken.Should().BeEquivalentTo("123456abcdef");
        }

        [Fact]
        public void DeserializationTest_PingResponse()
        {
            var response = StaticHelper.FromXml<PingResponse>(@"<?xml version=""1.0"" encoding=""utf-8""?>
            <response>
                <result-code fatal=""false"" message=""Ok"" msg=""Ok"">0</result-code>
                <balances>
                    <balance code=""643"">120.00</balance>
                </balances>
                <f></f>
                <qvc>
                    <qvc_bal cur=""643""></qvc_bal>
                </qvc>
                <identification-status bank-id=""900001"">simple</identification-status>
                <lk-status>001</lk-status>
            </response>");

            response.ResultCode.Value.Should().Be(0);

            response.Balances.Length.Should().Be(1);
            response.Balances[0].Amount.Should().Be(120.0m);
            response.Balances[0].Currency.Should().Be(643);

            response.QvcBalances.Length.Should().Be(1);
            response.QvcBalances[0].Amount.Should().Be(0.0m);
            response.QvcBalances[0].Currency.Should().Be(643);

            response.IdentificationStatus.BankId.Should().BeEquivalentTo("900001");
            response.IdentificationStatus.Value.Should().BeEquivalentTo("simple");

            response.LkStatus.Should().BeEquivalentTo("001");

        }

        [Fact]
        public void DeserializationTest_ListBillResponse()
        {
            var response = StaticHelper.FromXml<ListBillResponse>(@"<?xml version=""1.0"" encoding=""utf-8""?>
            <response>
               <result-code fatal=""false"" message=""Ok"" msg=""Ok"">0</result-code>
               <account-list>
                    <account>
                        <id>751774831</id>
                        <term-ransaction>249143</term-ransaction>
                        <from>
                            <prv>6459</prv>
                            <trm-id>ООО Ромашка</trm-id>
                        </from>
                        <to>
                            <prv>7</prv>
                            <trm-id>79266546367</trm-id>
                        </to>
                        <amount>500.00</amount>
                        <currency>643</currency>
                        <src>
                            <amount-lk>500.00</amount-lk>
                            <amount-mob prvId=""1801"">522.50</amount-mob>
                        </src>
                        <bill-date>2016-07-26 01:08:02.0</bill-date>
                        <comment>Оплата заказа №249143</comment>
                        <status>60</status>
                        <direct>1</direct>
                        <ident>0</ident>
                    </account>
                </account-list>
            </response>");

            response.ResultCode.Value.Should().Be(0);
            response.AccountList.Length.Should().Be(1);

            response.AccountList[0].Id.Should().BeEquivalentTo("751774831");
            response.AccountList[0].TransactionId.Should().BeEquivalentTo("249143");

            response.AccountList[0].From.ProviderId.Should().BeEquivalentTo("6459");
            response.AccountList[0].From.Id.Should().BeEquivalentTo("ООО Ромашка");
            response.AccountList[0].To.ProviderId.Should().BeEquivalentTo("7");
            response.AccountList[0].To.Id.Should().BeEquivalentTo("79266546367");

            response.AccountList[0].Amount.Should().Be(500.0);
            response.AccountList[0].Currency.Should().Be(643);

            response.AccountList[0].AmountInfo.AmountLk.Should().Be(500.0m);
            response.AccountList[0].AmountInfo.AmountMob.ProviderId.Should().BeEquivalentTo("1801");
            response.AccountList[0].AmountInfo.AmountMob.Value.Should().Be(522.50m);

            response.AccountList[0].BillDate.Should().Be(DateTime.Parse("2016-07-26 01:08:02.0"));
            response.AccountList[0].Comment.Should().BeEquivalentTo("Оплата заказа №249143");
            response.AccountList[0].Status.Should().Be(60);
            response.AccountList[0].Direct.Should().Be(1);
            response.AccountList[0].Ident.Should().Be(0);
        }

        [Fact]
        public void DeserializationTest_GetPaymentsReportResponse()
        {
            var response = StaticHelper.FromXml<GetPaymentsReportResponse>(@"<?xml version=""1.0"" encoding=""utf-8""?>
            <response>
               <result-code fatal=""false"" message=""Ok"" msg=""Ok"">0</result-code>
               <p-list>
                    <p d=""-"" from_c=""643"" to_c=""643"" t=""26.07.2016 01:08:47"" t_utc=""2016-07-25T22:08:47.00Z"" p=""Контрагент 1"" a=""1111"" s=""500.00"" rs=""505.00"" st=""60"" e=""0"" e_message=""Ок"" id=""11111111"" p-id=""111"" from=""Visa QIWI Wallet"" from_agt=""0000000000"" cmnt=""Оплата заказа"" />
                    <p d=""+"" from_c=""643"" to_c=""643"" t=""26.07.2016 01:06:56"" t_utc=""2016-07-25T22:06:56.00Z"" p=""Контрагент 2"" a=""2222"" s=""500.00"" rs=""505.00"" st=""60"" e=""0"" e_message=""Ок"" id=""22222222"" p-id=""222"" from_agt=""35"" />
                  
             </p-list>
            </response>");

            response.ResultCode.Value.Should().Be(0);
            response.Payments.Length.Should().Be(2);

            response.Payments[0].Id.Should().BeEquivalentTo("11111111");
            response.Payments[0].Direction.Should().Be(PaymentDirection.Outgoing);

            response.Payments[1].Id.Should().BeEquivalentTo("22222222");
            response.Payments[1].Direction.Should().Be(PaymentDirection.Incoming);
        }
    }
}
