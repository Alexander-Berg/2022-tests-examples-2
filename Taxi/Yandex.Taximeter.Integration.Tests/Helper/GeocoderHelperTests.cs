using FluentAssertions;
using Microsoft.Extensions.Logging;
using Moq;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.Extensions.Options;
using Xunit;
using Yandex.Taximeter.Core.Configuration.Options;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Services.Geography;
using Yandex.Taximeter.Integration.Tests.Fixtures;
using Yandex.Taximeter.Test.Utils.Fakes;
using Microsoft.Extensions.DependencyInjection;

namespace Yandex.Taximeter.Integration.Tests.Helper
{
    public class GeocoderHelperTests: IClassFixture<FatFixture>
    {
        private readonly ILoggerFactory _loggerFactory;
        private readonly Mock<ICityRepository> _cityRepository;
        private readonly Mock<IParkRepository> _parkRepository;
        private readonly Mock<ITaxiGeoareaService> _geoareaServise;
        private readonly Mock<ICountryRepository> _countryRepository;
        private readonly FatFixture _fixture; 
        
        public GeocoderHelperTests(FatFixture fixture)
        {
            _fixture = fixture;
            _loggerFactory = new FakeLoggerFactory();
            _cityRepository = new Mock<ICityRepository>();
            _cityRepository.Setup(x => x.GetCityCountryMapAsync())
                .ReturnsAsync(new Dictionary<string, string>
                {
                    { "Москва", "Россия" }
                });
            _parkRepository = new Mock<IParkRepository>();
            _geoareaServise = new Mock<ITaxiGeoareaService>();
            _countryRepository = new Mock<ICountryRepository>();
        }

        [Fact]
        public async Task Suggests_AddressAsync()
        {
            GeocoderHelper.Inject(_parkRepository.Object, _loggerFactory, _cityRepository.Object, _geoareaServise.Object,
                _fixture.ServiceProvider.GetService<IOptions<GeoMapsOptions>>(), _countryRepository.Object);

            var model = await GeocoderHelper.Suggests.AddressAsync("Большой", 55.753676, 37.619899, "ru");
            model?.results.Should().NotBeNull();
        }

        [Fact]
        public async Task Suggests_CityAsync()
        {
            GeocoderHelper.Inject(_parkRepository.Object, _loggerFactory, _cityRepository.Object,
                _geoareaServise.Object, _fixture.ServiceProvider.GetService<IOptions<GeoMapsOptions>>(), _countryRepository.Object);

            var model = await GeocoderHelper.Suggests.CityAsync("Россия", " Моск");
            model.Should().NotBeNullOrEmpty();
        }


        [Fact]
        public async Task TestParseAddrResponse()
        {
            //curl 'http://addrs.yandex.ru:17140/yandsearch?ms=json&lang=ru&mode=reverse&ll=37.587937,55.73377&type=geo&origin=example&results=1'

            var response =
                @"{'_json_geosearch_version':'27.04.15','_json_source':'GeoMetaSearch','features':[{'geometry':{'coordinates':[37.587093,55.733969],'type':'Point'},'properties':{'ArrivalMetaData':{'ArrivalPoints':[{'Point':{'coordinates':[37.588458,55.733959],'type':'Point'},'direction':[140,0],'name':'1'},{'Point':{'coordinates':[37.588036,55.734197],'type':'Point'},'direction':[206,0],'name':'2'},{'Point':{'coordinates':[37.587416,55.734364],'type':'Point'},'direction':[129,0],'name':'3'},{'Point':{'coordinates':[37.587209,55.734045],'type':'Point'},'direction':[63,0],'name':'4'},{'Point':{'coordinates':[37.587757,55.733761],'type':'Point'},'direction':[319,0],'name':'5'},{'Point':{'coordinates':[37.588206,55.733766],'type':'Point'},'direction':[140,0]},{'Point':{'coordinates':[37.586805,55.734004],'type':'Point'},'direction':[230,0]},{'Point':{'coordinates':[37.587461,55.733558],'type':'Point'},'direction':[230,0]}]},'GeocoderMetaData':{'Address':{'Components':[{'kind':'country','name':'Россия'},{'kind':'province','name':'Центральный федеральный округ'},{'kind':'province','name':'Москва'},{'kind':'locality','name':'Москва'},{'kind':'street','name':'улица Льва Толстого'},{'kind':'house','name':'16'}],'country_code':'RU','formatted':'Россия, Москва, улица Льва Толстого, 16','postal_code':'119021'},'InternalToponymInfo':{'MatchedComponent':{'kind':'house'},'Point':{'coordinates':[37.587937,55.733771],'type':'Point'},'geoid':213,'houses':0,'seoname':'ulitsa_lva_tolstogo_16'},'id':'56697621','kind':'house','precision':'exact','text':'Россия, Москва, улица Льва Толстого, 16'},'URIMetaData':{'URI':{'uri':'ymapsbm1:/geo?ll=37.587%2C55.734&spn=0.001%2C0.001&text=%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D1%8F%2C%20%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0%2C%20%D1%83%D0%BB%D0%B8%D1%86%D0%B0%20%D0%9B%D1%8C%D0%B2%D0%B0%20%D0%A2%D0%BE%D0%BB%D1%81%D1%82%D0%BE%D0%B3%D0%BE%2C%2016'}},'boundedBy':[[37.582987,55.731653],[37.591198,55.736285]],'description':'Москва, Россия','hasYandexTravelRefs':'','name':'улица Льва Толстого, 16','title':'Улица Льва Толстого, 16','titleHighlight':null},'type':'Feature'}],'properties':{'Origin':'example','ResponseMetaData':{'SearchRequest':{'Point':{'coordinates':[37.587937,55.73377],'type':'Point'},'request':'37.587937,55.73377','results':1,'skip':0},'SearchResponse':{'InternalResponseInfo':{'context':'ZAAAAAgAEAAaKAoSCd6NBYVBy0JAEZlk5Czs3UtAEhIJzDvxQg5stD8RIq629DL/pj8iAQAoADABOPfahd+Yk8X/pgFA3q0HSAFVAACAv1j/8BagBwAJ0BAAAAAKABAKgBAA==','display':'multiple','drag_context':'ZAAAAAgAEAAaKAoSCd6NBYVBy0JAEZlk5Czs3UtAEhIJzDvxQg5stD8RIq629DL/pj8iAQAoADABOPfahd+Yk8X/pgFA3q0HSAFVAACAv1j///////////8BagBwAJ0BAAAAAKABAKgBAA==','link_from_serp':'ZAAAAAgAEAMaKAoSCd6NBYVBy0JAEZlk5Czs3UtAEhIJzDvxQg5stD8RIq629DL/pj8iAQAoADABOPfahd+Yk8X/pgFA3q0HSAFVAACAv1j///////////8BagBwAJ0BAAAAAKABAKgBAA==','reqid':'1564148920213707-2435582281-sas1-5947','serpid':'1564148920213707-2435582281-sas1-5947'},'Point':{'coordinates':[37.58709252,55.73396898],'type':'Point'},'SourceMetaDataList':{'SourceMetaData':{'GeocoderResponseMetaData':{'InternalResponseInfo':{'accuracy':'1','boundedBy':[[37.582987,55.731653],[37.591198,55.736285]],'mode':'reverse','version':'19.07.26-0'},'Point':{'coordinates':[37.587937,55.73377],'type':'Point'},'boundedBy':[[37.548052,55.711311],[37.627822,55.756219]],'found':9,'request':'37.587937,55.73377','results':1}}},'boundedBy':[[37.582987,55.731653],[37.591198,55.736285]],'found':9}}},'type':'FeatureCollection'}";
            GeocoderHelper.Inject(_parkRepository.Object, _loggerFactory, _cityRepository.Object,
                _geoareaServise.Object, _fixture.ServiceProvider.GetService<IOptions<GeoMapsOptions>>(),
                _countryRepository.Object);

            var model = GeocoderHelper.ParseAddrResponse(response);
            model.Street.Should().NotBeNullOrEmpty();
            
        }
    }
}
