using System;
using System.Net.Http;
using Yandex.Taximeter.Core.Clients;

namespace Yandex.Taximeter.Test.Utils.Fakes
{
    public class FakeTaxiClient : ITaxiClient, IDisposable
    {
        public FakeHttpMessageHandler DevUtilsHandler = new FakeHttpMessageHandler();

        public FakeHttpMessageHandler CabinetHandler = new FakeHttpMessageHandler();

        public FakeHttpMessageHandler TaxiUtilsHandler = new FakeHttpMessageHandler();

        public FakeHttpMessageHandler TaximeterApiHandler = new FakeHttpMessageHandler();

        public FakeHttpMessageHandler DriverAuthorizerHandler = new FakeHttpMessageHandler();

        public FakeHttpMessageHandler DriverProtocolHandler = new FakeHttpMessageHandler();
        
        public FakeHttpMessageHandler DriverStatusHandler = new FakeHttpMessageHandler();
        
        public FakeHttpMessageHandler DriverCategorieslHandler = new FakeHttpMessageHandler();

        public FakeHttpMessageHandler EatsTimeTablesHandler = new FakeHttpMessageHandler();

        public FakeHttpMessageHandler PersonalWalletHandler = new FakeHttpMessageHandler();

        public FakeHttpMessageHandler ExternalChatHandler = new FakeHttpMessageHandler();
        
        public FakeHttpMessageHandler MlHandler = new FakeHttpMessageHandler();
        
        public FakeHttpMessageHandler ReportsHandler = new FakeHttpMessageHandler();

        public FakeHttpMessageHandler TrackerHandler = new FakeHttpMessageHandler();
        
        public FakeHttpMessageHandler GeotracksHandler = new FakeHttpMessageHandler();

        public FakeHttpMessageHandler BillingHandler = new FakeHttpMessageHandler();
        
        public FakeHttpMessageHandler PartnerContractsHandler = new FakeHttpMessageHandler();
        
        public FakeHttpMessageHandler PartnerApiProxyHandler = new FakeHttpMessageHandler();
                
        public HttpClient DevUtils => new HttpClient(DevUtilsHandler) {BaseAddress = new Uri("http://dev_utils")};

        public HttpClient Cabinet => new HttpClient(CabinetHandler) {BaseAddress = new Uri("http://cabinet")};

        public HttpClient CabinetPayments => Cabinet;

        public HttpClient TaxiUtils => new HttpClient(TaxiUtilsHandler) {BaseAddress = new Uri("http://taxi_utils")};

        public HttpClient TaximeterApi => new HttpClient(TaximeterApiHandler) {BaseAddress = new Uri("http://taximeter_api")};
       
        public HttpClient DriverAuthorizer => new HttpClient(DriverAuthorizerHandler) {BaseAddress = new Uri("http://driver_authorizer")};

        public HttpClient DriverProtocol => new HttpClient(DriverProtocolHandler) {BaseAddress = new Uri("http://driver_protocol")};
        
        public HttpClient ExternalChat => new HttpClient(ExternalChatHandler) {BaseAddress = new Uri("http://external_chat")};
        
        public HttpClient Ml => new HttpClient(MlHandler) {BaseAddress = new Uri("http://ml")};
        
        public HttpClient Reports => new HttpClient(ReportsHandler) {BaseAddress = new Uri("http://reports")};
        
        public HttpClient Tracker => new HttpClient(TrackerHandler) {BaseAddress = new Uri("http://tracker")};
        
        public HttpClient Geotracks => new HttpClient(GeotracksHandler) {BaseAddress = new Uri("http://geotracks")};

        public HttpClient BillingOrders => new HttpClient(BillingHandler) {BaseAddress = new Uri("http://billing")};
        public HttpClient BillingReports => new HttpClient(BillingHandler) {BaseAddress = new Uri("http://billing-reports")};

        public HttpClient PartnerContracts =>
            new HttpClient(PartnerContractsHandler) {BaseAddress = new Uri("http://partner-contracts")};

        public HttpClient PersonalWallet =>
            new HttpClient(PersonalWalletHandler) {BaseAddress = new Uri("http://personal-wallet")};

        public HttpClient GetDriverCategories(int timeout)
        {
            return new HttpClient(DriverCategorieslHandler) { BaseAddress = new Uri("http://driver-categories-api"), Timeout = TimeSpan.FromMilliseconds(timeout) };
        }

        public HttpClient PartnerApiProxy(int timeout)
        {
            return new HttpClient(PartnerApiProxyHandler) { BaseAddress = new Uri("http://partner-api-proxy"), Timeout = TimeSpan.FromMilliseconds(timeout) };
        }

        public HttpClient EatsTimeTables(int timeout)
        {
            return new HttpClient(EatsTimeTablesHandler) {BaseAddress = new Uri("http://courier-time-table"), Timeout = TimeSpan.FromMilliseconds(timeout) };
        }
        
        public HttpClient GetDriverStatus(int timeout)
        {
            return new HttpClient(DriverStatusHandler) { BaseAddress = new Uri("http://driver-status"), Timeout = TimeSpan.FromMilliseconds(timeout) };
        }

        public HttpClient CreateParkCabinet(string apiKey, int timeout = 0)
        {
            throw new System.NotImplementedException();
        }

        public HttpClient CreateCabinet(int timeout)
        {
            throw new System.NotImplementedException();
        }

        public HttpClient CreateDevUtils(int timeout)
        {
            throw new System.NotImplementedException();
        }

        public void Dispose()
        {
            DevUtils?.Dispose();
            Cabinet?.Dispose();
            TaxiUtils?.Dispose();
            TaximeterApi?.Dispose();
            ExternalChat?.Dispose();
        }
    }
}
