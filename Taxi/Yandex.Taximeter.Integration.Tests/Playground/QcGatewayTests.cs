using System;
using System.Collections.Generic;
using System.Linq;
using FluentAssertions;
using System.Threading.Tasks;
using Microsoft.Extensions.DependencyInjection;
using Xunit;
using Yandex.Taximeter.Core.Services.NewQualityControl;
using Yandex.Taximeter.Integration.Tests.Fixtures;

namespace Yandex.Taximeter.Integration.Tests.Playground
{
    /// <summary>
    /// Playground for experiments with QC microservice.
    /// </summary>
    public class QcGatewayTests : IClassFixture<FatFixture>
    {
        private readonly IQcGateway _qcGateway;

        private const string PARK_ID = "c52e88b724674ef7917ee0f8fa4627de";
        private const string DRIVER_ID = "e3325d7fafc744a1a62024d7a261e1ed";
        private const string CAR_ID = "04e4a77a2ff843c78b852ace7e0e6d4f";

        private Task<(CallReason, int?, string[], string[], Release?)> CallInfo(int? period)
        {
            return Task.FromResult((new CallReason(), period,
                new[] {QcConst.Sanction.ORDERS_OFF}, new[] {QcConst.Media.FRONT}, (Release?) null));
        }

        public QcGatewayTests(FatFixture fixture)
        {
            _qcGateway = fixture.ServiceProvider.GetService<IQcGateway>();
        }

        private async Task<QcStateExam> GetExamState(string exam)
        {
            var driverState = await _qcGateway.GetDriverStateAsync(PARK_ID, DRIVER_ID, exam);
            return driverState.Exams.FirstOrDefault(x => x.Code == exam);
        }

        [Fact]
        public async Task FromNeedPass()
        {
            // похождение и дедлайн прямо сейчас
            await _qcGateway.PostDriverStateAsync(PARK_ID, DRIVER_ID, QcConst.Exam.DKB, new QcStatePostItem
            {
                Present = new QcExamPresent
                {
                    CanPass = true,
                    Sanctions = new HashSet<string> {QcConst.Sanction.ORDERS_OFF}
                },
                Pass = new QcExamPostPass
                {
                    Media = new[] {QcConst.Media.FRONT}
                }
            });

            var dkkState = await GetExamState(QcConst.Exam.DKB);
            dkkState.Should().NotBeNull();
            dkkState.Present.Should().NotBeNull();
            dkkState.Present.Pass.Should().NotBeNull();
            dkkState.Present.Pass.Media.Should().NotBeNullOrEmpty();
            dkkState.Future.Should().BeNull();

            // enable = true -> включить экзамен:
            //   nextPass != null - вызов на экзамен
            //   nextPass == null - включение/выключение экзамена в пред. состоянии
            // enable = false -> выключить экзамен

            var stateEnable = await dkkState.BuildStatePost(true, null, () => CallInfo(12));
            var stateDisable = await dkkState.BuildStatePost(false, null, () => CallInfo(12));
            var stateCall = await dkkState.BuildStatePost(true, DateTime.UtcNow, () => CallInfo(12));
            var nextPass = DateTime.UtcNow + TimeSpan.FromDays(1);
            var statePostpone = await dkkState.BuildStatePost(true, nextPass, () => CallInfo(12));

            stateEnable.Should().BeNull();
            stateDisable.Should().NotBeNull();
            stateDisable.Enabled.Should().BeFalse();
            stateDisable.Present.Should().BeNull();
            stateDisable.Future.Should().BeNull();
            stateDisable.Pass.Should().BeNull();
            stateCall.Should().BeNull();
            statePostpone.Should().NotBeNull();
            statePostpone.Present.CanPass.Should().BeFalse();
            statePostpone.Future.Length.Should().Be(2);
            statePostpone.Future.Last().Begin.Should().Be(nextPass);
        }

        [Fact]
        public async Task FromCanPass()
        {
            // похождение прямо сейчас, дедлайн через час
            await _qcGateway.PostDriverStateAsync(PARK_ID, DRIVER_ID, QcConst.Exam.DKB, new QcStatePostItem
            {
                Present = new QcExamPresent
                {
                    CanPass = true
                },
                Future = new[]
                {
                    new QcExamFuture
                    {
                        CanPass = true,
                        Begin = DateTime.UtcNow + TimeSpan.FromHours(1),
                        Sanctions = new HashSet<string> {QcConst.Sanction.ORDERS_OFF},
                    }
                },
                Pass = new QcExamPostPass
                {
                    Media = new[] {QcConst.Media.FRONT}
                }
            });

            var dkkState = await GetExamState(QcConst.Exam.DKB);
            dkkState.Should().NotBeNull();
            dkkState.Present.Should().NotBeNull();
            dkkState.Present.Pass.Should().NotBeNull();
            dkkState.Present.Pass.Media.Should().NotBeNullOrEmpty();
            dkkState.Future.Should().NotBeNull();
            // enable = true -> включить экзамен:
            //   nextPass != null - вызов на экзамен
            //   nextPass == null - включение/выключение экзамена в пред. состоянии
            // enable = false -> выключить экзамен

            var stateEnable = await dkkState.BuildStatePost(true, null, () => CallInfo(12));
            var stateDisable = await dkkState.BuildStatePost(false, null, () => CallInfo(12));
            var stateCall = await dkkState.BuildStatePost(true, DateTime.UtcNow, () => CallInfo(12));

            var nextPassDay = DateTime.UtcNow + TimeSpan.FromDays(1);
            var statePostponeDay = await dkkState.BuildStatePost(true, nextPassDay, () => CallInfo(12));

            var nextPassHour = DateTime.UtcNow + TimeSpan.FromHours(1);
            var statePostponeHour = await dkkState.BuildStatePost(true, nextPassHour, () => CallInfo(12));

            stateEnable.Should().BeNull();
            stateDisable.Should().NotBeNull();
            stateDisable.Enabled.Should().BeFalse();
            stateDisable.Present.Should().BeNull();
            stateDisable.Future.Should().BeNull();
            stateDisable.Pass.Should().BeNull();
            stateCall.Should().NotBeNull();
            stateCall.Present.CanPass.Should().BeTrue();
            stateCall.Future.Should().BeNull();
            statePostponeDay.Should().NotBeNull();
            statePostponeDay.Present.CanPass.Should().BeFalse();
            statePostponeDay.Future.Length.Should().Be(2);
            statePostponeDay.Future.Last().Begin.Should().Be(nextPassDay);
            statePostponeHour.Should().BeNull();
        }

        [Fact]
        public async Task FromDisablePassed()
        {
            // похождение прямо сейчас, дедлайн через час
            await _qcGateway.PostDriverStateAsync(PARK_ID, DRIVER_ID, QcConst.Exam.DKB, new QcStatePostItem
            {
                Present = new QcExamPresent
                {
                    CanPass = true
                },
                Future = new[]
                {
                    new QcExamFuture
                    {
                        CanPass = true,
                        Begin = DateTime.UtcNow + TimeSpan.FromDays(1),
                        Sanctions = new HashSet<string> {QcConst.Sanction.ORDERS_OFF},
                    }
                },
                Pass = new QcExamPostPass
                {
                    Media = new[] {QcConst.Media.FRONT}
                }
            });

            // возвращаем состояние, которое было до disable
            var dkkState = await GetExamState(QcConst.Exam.DKB);
            var modifiedFirst = dkkState.Modified;
            await _qcGateway.PostDriverStateAsync(PARK_ID, DRIVER_ID, QcConst.Exam.DKB,
                await dkkState.BuildStatePost(false, null, () => CallInfo(12)));

            // disable
            dkkState = await GetExamState(QcConst.Exam.DKB);
            dkkState.Should().BeNull();
            await _qcGateway.PostDriverStateAsync(PARK_ID, DRIVER_ID, QcConst.Exam.DKB,
                await dkkState.BuildStatePost(true, null, () => CallInfo(12)));

            // enable
            dkkState = await GetExamState(QcConst.Exam.DKB);
            var modifiedLast = dkkState.Modified;
            dkkState.Should().NotBeNull();
            dkkState.Present.Should().NotBeNull();
            dkkState.Present.Pass.Should().NotBeNull();
            dkkState.Present.Pass.Media.Should().NotBeNullOrEmpty();
            dkkState.Present.Sanctions.Should().BeNullOrEmpty();

            (modifiedLast - modifiedFirst).Should().BeGreaterThan(TimeSpan.Zero);
        }

        [Fact]
        public async Task Amnesty()
        {
            // похождение и дедлайн в будущем
            await _qcGateway.PostDriverStateAsync(PARK_ID, DRIVER_ID, QcConst.Exam.DKB, new QcStatePostItem
            {
                Present = new QcExamPresent
                {
                    CanPass = false
                },
                Future = new []
                {
                    new QcExamFuture
                    {
                        Begin = DateTime.UtcNow + TimeSpan.FromHours(10),
                        CanPass = true
                    },
                    new QcExamFuture
                    {
                        Begin = DateTime.UtcNow + TimeSpan.FromDays(10),
                        CanPass = true,
                        Sanctions = new HashSet<string> {QcConst.Sanction.ORDERS_OFF}
                    }
                },
                Pass = new QcExamPostPass
                {
                    Media = new[] {QcConst.Media.FRONT}
                }
            });

            // возвращаем состояние, которое было до disable
            var dkkState = await GetExamState(QcConst.Exam.DKB);
            dkkState.Present.Should().BeNull();
            dkkState.Future.Should().NotBeNull();

            var needState = await dkkState.BuildStatePost(true, DateTime.UtcNow + TimeSpan.FromHours(1), () => CallInfo(null));
            needState.Should().NotBeNull();
            await _qcGateway.PostDriverStateAsync(PARK_ID, DRIVER_ID, QcConst.Exam.DKB, needState);

            dkkState = await GetExamState(QcConst.Exam.DKB);
            dkkState.Present.Should().NotBeNull();
            dkkState.Present.Pass.Should().NotBeNull();
            dkkState.Present.Pass.Media.Should().NotBeNullOrEmpty();
            dkkState.Future.Should().NotBeNull();
        }

        [Fact]
        public async Task TestCopy()
        {
            var oldParkId = "93e8f59ef68e44a2adbbc0dd8262f4d9";
            var oldDriverId = "f8e2b9a527f0489bb0dc89b0d5d3deb7";

            var oldState = await _qcGateway.GetDriverStateAsync(oldParkId, oldDriverId);

            var newParkId = "7ad36bc7560449998acbe2c57a75c293";
            var newDriverId = "98eb55c39e3c42bb8de00fe0dce933c3";

            {
                // copy dkk
                var examState = oldState?.Exams?.FirstOrDefault(x => x.Code == QcConst.Exam.DKB);
                if (examState != null)
                {
                    var newState = examState.CopyStatePost(CallReason.Newbie(), 3);
                    await _qcGateway.PostDriverStateAsync(newParkId, newDriverId, examState.Code, newState);
                }
            }

            {
                // copy dkvu
                var examState = oldState?.Exams?.FirstOrDefault(x => x.Code == QcConst.Exam.DKVU);
                if (examState != null)
                {
                    var newState = examState.CopyStatePost(CallReason.Newbie(), 3);
                    await _qcGateway.PostDriverStateAsync(newParkId, newDriverId, examState.Code, newState);
                }
            }
        }

        [Fact]
        public async Task GetStateFromCache()
        {
            var carState = await _qcGateway.GetCarCachedStateAsync("93e8f59ef68e44a2adbbc0dd8262f4d9",
                "6795eea89d894054b819b2f4ef3666f4");

            var driverState = await _qcGateway.GetDriverCachedStateAsync("93e8f59ef68e44a2adbbc0dd8262f4d9",
                "f8e2b9a527f0489bb0dc89b0d5d3deb7");

            Assert.NotNull(carState);
            Assert.NotNull(driverState);
        }

        [Fact]
        public async Task LoadMedia()
        {
            var passId = "5d56ed0dfa207c151d381e76";
            try
            {
                await _qcGateway.PostPassMediaAsync(passId, QcConst.Media.FRONT, new byte[] {1, 2});
            }
            catch (Exception ex)
            {
                var d = ex ?? throw new ArgumentNullException(nameof(ex));
            }
        }


        [Fact]
        public async Task UpdateDataInPass()
        {
            var qcPass = await _qcGateway.GetPassAsync("5dc947aefa207c300218901f");

            var passData = new Dictionary<string, string>();
            passData[QcConst.DataField.City] = "Москва";
            passData[QcConst.DataField.CityLevel] = "1";
            passData[QcConst.DataField.Country] = "rus";
            passData[QcConst.DataField.DriverName] = "[123] Тест";
            passData[QcConst.DataField.CarId] = "93e8f59ef68e44a2adbbc0dd8262f4d9";
            passData[QcConst.DataField.CarName] = "Машина 777";
            passData[QcConst.DataField.CarNumber] = "777";

            var modified = await _qcGateway.PostPassDataAsync(qcPass.Id, passData, qcPass.Modified);
            Assert.Null(modified);
        }
    }
}
