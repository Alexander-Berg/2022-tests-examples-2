using System;
using System.Collections.Generic;
using System.Linq;
using FluentAssertions;
using GeoAPI.Geometries;
using Moq;
using NetTopologySuite.Geometries;
using Xunit;
using Yandex.Taximeter.Core.Repositories.MongoDB.Dtos.DbTaxi;
using Yandex.Taximeter.Core.Services.Geography;
using Yandex.Taximeter.Core.Services.Geometry;
using Yandex.Taximeter.Test.Utils.Fakes;
using Yandex.Taximeter.Test.Utils.Utils;

namespace Yandex.Taximeter.Common.Tests.Services.Geography
{
    public class GeoareaIndexTests
    {
        private readonly Mock<ITaxiGeoareaService> _geoareaService;
        private readonly GeoareaIndex _geoareaIndex;

        public GeoareaIndexTests()
        {
            _geoareaService = new Mock<ITaxiGeoareaService>();
            _geoareaIndex = new GeoareaIndex(_geoareaService.Object, new FakeMemoryCache(), new FakeLoggerFactory());
        }

        [Fact]
        public async void GetGeoareasAsync_EmptyGeoareasList_ReturnsEmptyList()
        {
            SetupGeoareas(Array.Empty<GeoareaDto>());

            var result = await _geoareaIndex.GetGeoareasAsync(new Envelope(new Coordinate(1, 1)));

            result.Should().BeEmpty();
        }

        [Fact]
        public async void GetGeoareasAsync_PointDoesNotFallIntoAnyGeoareas_ReturnsEmptyList()
        {
            SetupGeoareas(SimpleGeoareas);

            var result = await _geoareaIndex.GetGeoareasAsync(new Envelope(new Coordinate(2, 2.1)));
            
            result.Should().BeEmpty();
        }

        [Fact]
        public async void GetGeoareasAsync_PointFallsIntoSingleGeoarea_ReturnsGeoarea()
        {
            SetupGeoareas(SimpleGeoareas);

            var result = await _geoareaIndex.GetGeoareasAsync(new Envelope(new Coordinate(.1, .2)));

            result.Should().BeEquivalentTo(SimpleGeoareas[0]);
        }

        [Fact]
        public async void GetGeoareasAsync_PointFallsIntoMultipleGeoareas_ReturnsGeoareas()
        {
            SetupGeoareas(SimpleGeoareas);

            var result = await _geoareaIndex.GetGeoareasAsync(new Envelope(new Coordinate(.6, .8)));

            result.Should().BeEquivalentTo(SimpleGeoareas[0], SimpleGeoareas[1]);
        }

        [Fact]
        public async void GetGeoareasAsync_PointFallsIntoConvexGeoarea_ReturnsGeoarea()
        {
            SetupGeoareas(SimpleGeoareas);

            var result = await _geoareaIndex.GetGeoareasAsync(new Envelope(new Coordinate(1.25, 1.25)));

            result.Should().BeEquivalentTo(SimpleGeoareas[2]);
        }

        private IList<GeoareaDto> SimpleGeoareas { get; } =
            new[]
            {
                new GeoareaDto
                {
                    Id = TestUtils.NewId(),
                    Name = "moscow",
                    Polygon = BuildPolygon( //square
                        new GeoPoint(0, 0),
                        new GeoPoint(0, 1),
                        new GeoPoint(1, 1),
                        new GeoPoint(1, 0),
                        new GeoPoint(0, 0))
                },
                new GeoareaDto
                {
                    Id = TestUtils.NewId(),
                    Name = "samara",
                    Polygon = BuildPolygon( //triangle
                        new GeoPoint(0.5, 0.5),
                        new GeoPoint(1.5, 1),
                        new GeoPoint(0.5, 1.5),
                        new GeoPoint(0.5, 0.5))
                },
                new GeoareaDto
                {
                    Id = TestUtils.NewId(),
                    Name = "spb",
                    Polygon = BuildPolygon( //convex polygon
                        new GeoPoint(1, 1),
                        new GeoPoint(1.5, 1.25),
                        new GeoPoint(2, 1),
                        new GeoPoint(2, 2),
                        new GeoPoint(1, 2),
                        new GeoPoint(1, 1))
                }
            };

        private void SetupGeoareas(ICollection<GeoareaDto> geoareas)
            => _geoareaService.Setup(x => x.GetGeoareasAsync())
                .ReturnsAsync(geoareas.ToDictionary(x => x.Id));

        private static Polygon BuildPolygon(params GeoPoint[] points)
            => new Polygon(
                new LinearRing(
                    points.Select(x => x.ToCoordinate()).ToArray()));
    }
}