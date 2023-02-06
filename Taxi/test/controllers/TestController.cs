using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.CodeAnalysis;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using NLog.Common;
using Yandex.Taximeter.Admin.Areas.test.Models;
using Yandex.Taximeter.Admin.Controllers;
using Yandex.Taximeter.Core.Clients;
using Yandex.Taximeter.Core.Clients.Personal;
using Yandex.Taximeter.Core.Extensions;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Models.Geography;
using Yandex.Taximeter.Core.Models.Orders;
using Yandex.Taximeter.Core.Mvc.Authentication.Service;
using Yandex.Taximeter.Core.Redis;
using Yandex.Taximeter.Core.Redis.Services;
using Yandex.Taximeter.Core.Repositories.MongoDB;
using Yandex.Taximeter.Core.Repositories.MongoDB.Docs.Car;
using Yandex.Taximeter.Core.Repositories.MongoDB.Dtos.Driver;
using Yandex.Taximeter.Core.Repositories.Sql.Entities;
using Yandex.Taximeter.Core.Services.AdminTasks.Spam.Model;
using Yandex.Taximeter.Core.Services.Culture;
using Yandex.Taximeter.Core.Services.Driver;
using Yandex.Taximeter.Core.Services.Gas;
using Yandex.Taximeter.Core.Services.Order.SetCar;
using Yandex.Taximeter.Core.Services.Order.SetCar.Model;
using Yandex.Taximeter.Core.Services.PaySystem;
using Yandex.Taximeter.Core.Services.Push;
using Yandex.Taximeter.Core.Services.Push.Messages;
using Yandex.Taximeter.Core.Services.Push.Providers;
using Yandex.Taximeter.Core.Services.Resources;
using Yandex.Taximeter.Core.Services.Scripts;
using Yandex.Taximeter.Core.Services.Settings;
using Yandex.Taximeter.Core.Services.Sms;
using Yandex.Taximeter.Core.Services.Sql;

namespace Yandex.Taximeter.Admin.Areas.test.Controllers
{
    [Route("test")]
    [Permissions(Permissions.AdminRead)]
    public class TestController: AdminControllerBase
    {
        private readonly IParkRepository _parkRepository;
        private readonly IDriverRepository _driverRepository;
        private readonly IPushMessageProvider[] _pushMessageProviders;
        private readonly IMailClient _mailClient;
        private readonly IMdsClient _mdsClient;
        private readonly ILogger _logger;
        private readonly ICultureService _cultureService;

        public TestController(
            IParkRepository parkRepository,
            IDriverRepository driverRepository,
            IPushMessageProvider[] pushMessageProviders,
            IMailClient mailClient,
            IMdsClient mdsClient,
            ILoggerFactory loggerFactory,
            ICultureService cultureService)
            : base(loggerFactory)
        {
            _parkRepository = parkRepository;
            _driverRepository = driverRepository;
            _pushMessageProviders = pushMessageProviders;
            _mailClient = mailClient;
            _mdsClient = mdsClient;
            _cultureService = cultureService;
            _logger = loggerFactory.CreateLogger(GetType());
        }

        [HttpGet("script")]
        public IActionResult Script()
        {
            return View(new TestScriptModel());
        }

        [HttpPost("script")]
        public async Task<IActionResult> Script(string type, TestScriptModel model, IFormFile scriptFile, [FromServices]IScriptCompilationService scriptCompilationService)
        {
            try
            {
                string code = null;
                if (scriptFile != null)
                {
                    using (var sr = new StreamReader(scriptFile.OpenReadStream()))
                    {
                        code = await sr.ReadToEndAsync();
                    }
                }
                else if (!string.IsNullOrEmpty(model.Url))
                {
                    code = await scriptCompilationService.CheckoutScriptAsync(model.Url, CancellationToken.None,
                        new FixedStrategy(TimeSpan.FromSeconds(1), 10));
                }
                if (!string.IsNullOrEmpty(code))
                {
                    switch (type.ToLower())
                    {
                        case "check":
                            scriptCompilationService.TryCompileScript(code, CancellationToken.None);
                            ViewBag.Success = true;
                            break;
                        case "run":
                            //Доступно только в тестинге
                            if (!StaticHelper.IsTesting())
                            {
                                return NotFound();
                            }
                            var script = scriptCompilationService.CompileScript(code, CancellationToken.None);
                            var scriptArgs = string.IsNullOrWhiteSpace(model.Args)
                                ? Enumerable.Empty<string>()
                                : CommandLineParser.SplitCommandLineIntoArguments(model.Args, false);
                            using (var sw = new StringWriter())
                            {
                                await script.RunAsync(scriptArgs.ToArray(), sw, CancellationToken.None);
                                return File(Encoding.UTF8.GetBytes(sw.ToString()), "text/plain",
                                    $"{script.Name}_output.txt");
                            }
                        default:
                            return NotFound();
                    }
                }
            }
            catch (Exception ex)
            {
                if (StaticHelper.IsTesting())
                {
                    ModelState.AddModelError(string.Empty, ex.ToString());
                }
                else
                {
                    ModelState.AddModelError(string.Empty, ex.Message);
                }
            }
            return View(model);
        }

        [Route("push")]
        public async Task<IActionResult> Push(TestPushModel model, [FromServices]IServiceProvider serviceProvider)
        {
            if (!StaticHelper.IsTesting())
            {
                return NotFound();
            }

            if (model.PushType == 0)
            {
                return View(new TestPushModel());
            }

            if (!string.IsNullOrEmpty(model.Db))
            {
                var parkDto = await _parkRepository.GetCommonAsync(model.Db);
                if (parkDto != null && !parkDto.IsActive)
                {
                    ModelState.AddModelError(string.Empty, $"Парк {model.Db} не является тестовым");
                }
            }

            if (ModelState.IsValid)
            {

                var pushMessageService = SelectPushMessageService(model, serviceProvider);

                var random = new Random();
                object content = null;
                switch (model.PushType)
                {
                    case PushMessageAction.MessageNew:
                        if (model.Json != null)
                        {
                            await pushMessageService.AlertAsync(model.Db, model.Driver,
                                JsonConvert.DeserializeObject<PushAlert>(model.Json));
                        }
                        else
                        {
                            content = new PushAlert
                            {
                                Message =
                                    $"Тестовое сообщение {DateTime.UtcNow.ToString("u", CultureInfo.InvariantCulture)} [Yandex](https://yandex.ru)",
                                Id = Guid.NewGuid().ToString("N"),
                                Name = string.Empty
                            };
                        }
                        break;
                    case PushMessageAction.MessageNewOffline:
                        if (model.Json != null)
                        {
                            await pushMessageService.AlertOfflineAsync(model.Db, model.Driver,
                                JsonConvert.DeserializeObject<PushAlert>(model.Json));
                        }
                        else
                        {
                            content = new PushAlert
                            {
                                Message =
                                    $"Тестовое сообщение {DateTime.UtcNow.ToString("u", CultureInfo.InvariantCulture)} [Yandex](https://yandex.ru)",
                                Id = Guid.NewGuid().ToString("N"),
                                Name = string.Empty
                            };
                        }
                        break;
                    case PushMessageAction.ParkMessage:
                        if (model.Json != null)
                        {
                            await pushMessageService.ParkMessageAsync(model.Db, model.Driver,
                                JsonConvert.DeserializeObject<PushParkMessage>(model.Json));
                        }
                        else
                        {
                            content = new PushParkMessage
                            {
                                Message =
                                    $"Тестовое сообщение {DateTime.UtcNow.ToString("u", CultureInfo.InvariantCulture)} [Yandex](https://yandex.ru)",
                                Id = Guid.NewGuid().ToString("N"),
                                Name = string.Empty
                            };
                        }
                        break;
                    case PushMessageAction.MessageBalance:
                        if (model.Json != null)
                        {
                            var driverDto = await _driverRepository.GetAsync<DriverPushDto>(model.Db, model.Driver);
                            await pushMessageService.BalanceAsync(model.Db, model.Driver,
                                JsonConvert.DeserializeObject<PushBalance>(model.Json), DriverPushInfo.FromDto(driverDto));
                        }
                        else
                        {
                            var balance = random.Next(0, 10000) + random.NextDouble();
                            content = new PushBalance
                            {
                                Text = "Тестовое сообщение об изменении баланса",
                                PaymentGroup = DriverPaymentGroup.Прочее,
                                Balance = balance,
                                Limit = balance + random.Next(1000) + random.NextDouble(),
                                BalanceRevision = random.Next(100000,1000000)
                            };
                        }
                        break;
                    case PushMessageAction.MessageQc:
                        if (model.Json != null)
                        {
                            await pushMessageService.QcAsync(model.Db, model.Driver, false);
                        }
                        else
                        {
                            content = new { };
                        }
                        break;
                    case PushMessageAction.OrderSetCarRequest:
                    case PushMessageAction.UpdateRequest:
                    case PushMessageAction.OrderSetCarChain:
                        if (model.Json != null)
                        {
                            if (model.PushType == PushMessageAction.UpdateRequest)
                            {
                                var driverDto = await _driverRepository.GetAsync<DriverPushDto>(model.Db, model.Driver);
                                await pushMessageService.UpdateRequestAsync(model.Db, model.Driver,
                                    JsonConvert.DeserializeObject<SetCarItem>(model.Json), DriverPushInfo.FromDto(driverDto));
                            }
                            else
                            {
                                await pushMessageService.OrderSetCarRequestAsync(model.Db, model.Driver,
                                    JsonConvert.DeserializeObject<SetCarItem>(model.Json),
                                    isChainOrder: model.PushType == PushMessageAction.OrderSetCarChain);
                            }
                        }
                        else
                        {
                            var clid = (await _parkRepository.GetYandexConfigAsync(model.Db)).clid;
                            var carId = await _driverRepository.GetAsync(model.Db, model.Driver, x=>x.CarId);
                            content = new SetCarItem
                            {
                                id = Guid.NewGuid().ToString("N"),
                                provider = Provider.Яндекс,
                                number = random.Next(1, 100),
                                date_create = DateTime.UtcNow,
                                date_drive = DateTime.UtcNow,
                                date_last_change = DateTime.UtcNow,
                                category = CategoryFlags.Comfort,
                                pay_type = OrderPayType.Наличные,
                                kind = OrderKind.None,
                                clid = clid,
                                AddressFrom =
                                    new Address(null, "Москва, улица Льва Толстого, 16", null, null, null, null, null)
                                    {
                                        Lon = 37.587874,
                                        Lat = 55.73367,
                                        Region = "ЦАО"
                                    },
                                AddressTo = new DestAddress(null, "Аэропорт Внуково", null, null, null, null, null, 1,
                                    500)
                                {
                                    Lon = 37.278638,
                                    Lat = 55.600918,
                                    Region = "ВНУКОВО"
                                },
                                RequirementList = new RequirementCollection() {new Requirement(Requirement.ID_CREDITCARD) },
                                type_name = RuleTypeHelper.DefaultNames.YANDEX,
                                type_id = "4964b852670045b196e526d59915b777",
                                type_color = "#ff8000",
                                Tariff = new Tariff
                                {
                                    Id = "dd5f03783a0341c08aeef981b4e665f7",
                                    Geoareas = new[] {"dad4ee6fad674399b04576c793f0a04a"},
                                    IsSynchronizable = true
                                },
                                description = "Yandex.",
                                driver_id = model.Driver,
                                driver_name = "Пушкин Александр Сергеевич",
                                driver_signal = "00001",
                                car_id = carId,
                                car_name = "BMW 7ER",
                                car_number = "ТТ12377",
                                experiments = new HashSet<string>() {"direct_assignment"},
                            };
                            if (model.PushType == PushMessageAction.OrderSetCarChain)
                            {
                                var contentItem = content as SetCarItem;
                                contentItem.chain = new SetCarChain
                                {
                                    dist = 1500,
                                    time = 6,
                                    prev_lat = 55.65217325,
                                    prev_lon = 37.50356417
                                };
                            }
                        }
                        break;
                    case PushMessageAction.OrderChangeStatus:
                        if (model.Json != null)
                        {
                            await pushMessageService.OrderChangeStatusAsync(model.Db, model.Driver,
                                JsonConvert.DeserializeObject<PushOrderStatus>(model.Json));
                        }
                        else
                        {
                            content = new PushOrderStatus
                            {
                                Cost = random.Next(0, 1000) + random.NextDouble(),
                                Id = Guid.NewGuid().ToString("N"),
                                Payment = random.Next(4),
                                Status = random.Next(2, 6)
                            };
                        }
                        break;
                    case PushMessageAction.OrderRequest:
                        if (model.Json != null)
                        {
                            await pushMessageService.OrderRequestAsync(model.Db, model.Driver,
                                JsonConvert.DeserializeObject<PushOrderRequest>(model.Json));
                        }
                        else
                        {
                            content = new PushOrderRequest
                            {
                                Category = (int) CategoryFlags.Comfort,
                                Categories = CategoryFlags.Comfort,
                                Date = DateTime.UtcNow,
                                Distance = random.Next(10, 50) + random.NextDouble(),
                                Experiments = new HashSet<string> {"direct_assignment", "xiva_taximeter"},
                                Factor = 1.0d,
                                From = "Москва, улица Льва Толстого, 16",
                                Latitude = 55.73367,
                                Longitude = 37.587874,
                                Order = Guid.NewGuid().ToString("N"),
                                RoadTime = random.Next(0, 100) + random.NextDouble(),
                                Timeout = 50
                            };
                        }
                        break;
                    case PushMessageAction.OrderCanceled:
                        if (model.Json != null)
                        {
                            var push = JsonConvert.DeserializeObject<PushOrderCancel>(model.Json);
                            await pushMessageService.OrderCancelAsync(model.Db, model.Driver, push.Order);
                        }
                        else
                        {
                            content = new PushOrderCancel
                            {
                                Order = Guid.NewGuid().ToString("N")
                            };
                        }
                        break;
                    case PushMessageAction.RobotChange:
                        if (model.Json != null)
                        {
                            await pushMessageService.RobotChangeAsync(model.Db, model.Driver,
                                JsonConvert.DeserializeObject<RobotHelper.Setting>(model.Json));
                        }
                        else
                        {
                            content = (RobotHelper.Setting) random.Next(0, 0x7FFF);
                        }

                        break;
                    case PushMessageAction.StatusChange:
                        if (model.Json != null)
                        {
                            await pushMessageService.StatusChangeAsync(
                                model.Db, model.Driver, JsonConvert.DeserializeObject<bool>(model.Json));
                        }
                        else
                        {
                            content = random.Next(100) > 50;
                        }
                        break;
                    case PushMessageAction.StatusChangeObj:
                        if (model.Json != null)
                        {
                            await pushMessageService.StatusChangeAsync(
                                model.Db, model.Driver, JsonConvert.DeserializeObject<PushStatusUpdate>(model.Json));
                        }
                        else
                        {
                            content = new PushStatusUpdate {Busy = true};
                        }
                        break;
                    case PushMessageAction.MessageRate:
                        if (model.Json != null)
                        {
                            var push = JsonConvert.DeserializeObject<PushRate>(model.Json);
                            await pushMessageService.RateAsync(model.Db, model.Driver,
                                new DriverRates
                                {
                                    AcceptanceRate = push.AcRate,
                                    AcceptanceRateAmnesty = push.AcRateAmnesty,
                                    CompletionRate = push.CompRate,
                                    CompletionRateAmnesty = push.CompRateAmnesty,
                                    DriverId = model.Driver
                                }, push.AcRateSettings, push.CompRateSettings);
                        }
                        else
                        {
                            content = new PushRate
                            {
                                AcRate = random.NextDouble(),
                                AcRateSettings = new DriverHelper.Rating.Yandex.AcceptanceRate_Settings.Item(),
                                CompRateSettings = new DriverHelper.Rating.Yandex.CompletionRate_Settings.Item(),
                                AcRateAmnesty = new RateBlockAmnesty(DateTime.UtcNow.AddHours(random.NextDouble())),
                                CompRateAmnesty = new RateBlockAmnesty(DateTime.UtcNow.AddHours(random.NextDouble()))
                            };
                        }
                        break;
                    case PushMessageAction.NewsItem:
                        if (model.Json != null)
                        {
                            var push = JsonConvert.DeserializeObject<NewsItemData>(model.Json);
                            await pushMessageService.NewsItemAsync(model.Db, model.Driver, push);
                        }
                        else
                        {
                            content = new NewsItemData
                            {
                                Title = string.Format(
                                    Backend.SubventionNotificationsService_RulesNotification_OnceBonus_Title, 1,500, 5),
                                Body = string.Format(
                                    Backend.SubventionNotificationsService_RulesNotification_OnceBonus_Descr, 1, 500, 100,
                                    1)
                            };
                        }
                        break;
                    case PushMessageAction.WallChanged:
                        if (string.IsNullOrEmpty(model.Topic))
                        {
                            await pushMessageService.DriverWallChangedAsync(model.Db, model.Driver);
                        }
                        else
                        {
                            await pushMessageService.PublicWallChangedAsync(model.Topic);
                        }
                        break;
                    case PushMessageAction.DriverCheck:
                        await pushMessageService.DriverCheckAsync(model.Db, model.Driver);
                        break;
                    case PushMessageAction.MessageDesiredPaymentType:
                        if (model.Json != null)
                        {
                            var push = JsonConvert.DeserializeObject<JObject>(model.Json);
                            await pushMessageService.UpdateDesiredPaymentType(model.Db, model.Driver, push);
                        }
                        else
                        {
                            content = new
                            {
                                is_enabled = true,
                                selected_type = 0,
                                timestamp = DateTime.UtcNow.ToUnixTime()
                            };
                        }
                        break;
                    case PushMessageAction.OrderChangePayment:
                        if (model.Json != null)
                        {
                            var push = JsonConvert.DeserializeObject<PushOrderChangePayment>(model.Json);
                            await pushMessageService.OrderChangePaymentAsync(model.Db, model.Driver, push);
                        }
                        else
                        {
                            content = new PushOrderChangePayment
                            {
                                Message = Backend.UpdateRequest_Push_PaymentChanged_Cash,
                                Order = Guid.NewGuid().ToString("n"),
                                Payment = (int)OrderPayType.Наличные
                            };
                        }
                        break;
                    case PushMessageAction.DriverSpam:
                        if (model.Json != null)
                        {
                            var push = JsonConvert.DeserializeObject<PushDriverSpam>(model.Json);
                            await pushMessageService.DriverSpamAsync(model.Topic, push);
                        }
                        else
                        {
                            content = new PushDriverSpam
                            {
                                Id = Guid.NewGuid().ToString("n"),
                                Message = "Тестовая рассылка",
                                SpamFeature = SpamTaskFeature.Rain,
                                SpamShowOnlineOffer = true
                            };
                        }
                        break;
                    case PushMessageAction.OrderUserReady:
                        if (model.Json != null)
                        {
                            var push = JsonConvert.DeserializeObject<PushOrderUserReady>(model.Json);
                            await pushMessageService.OrderUserReadyAsync(model.Db, model.Driver, push);
                        }
                        else
                        {
                            content = new PushOrderUserReady
                            {
                                Message = Backend.UpdateRequest_Push_UserReady,
                                Order = Guid.NewGuid().ToString("n")
                            };
                        }
                        break;
                    case PushMessageAction.OrderTips:
                        if (model.Json != null)
                        {
                            var push = JsonConvert.DeserializeObject<PushOrderTips>(model.Json);
                            await pushMessageService.OrderTipsAsync(model.Db, model.Driver, push);
                        }
                        else
                        {
                            var culture = await _cultureService.GetGlobalAsync("ru");
                            content = new PushOrderTips
                            {
                                Message = MessageDistribution.Ext.YandexController_Payment_Driver_Tips_Msg(
                                    culture, 100, "Р"),
                                Order = Guid.NewGuid().ToString("n")
                            };
                        }
                        break;
                    case PushMessageAction.ChatUpdated:
                        if (model.Json != null)
                        {
                            var push = JsonConvert.DeserializeObject<PushChatUpdate>(model.Json);
                            await pushMessageService.ChatUpdatedAsync(model.Db, model.Driver, push);
                        }
                        else
                        {
                            content = new PushChatUpdate
                            {
                                ChatId = Guid.NewGuid().ToString("n"),
                                NewestMessageId = Guid.NewGuid().ToString("n"),
                                OrderId = Guid.NewGuid().ToString("n"),
                                UpdatedDate = DateTime.UtcNow
                            };
                        }
                        break;
                    case PushMessageAction.PersonalOffer:
                        if (model.Json != null)
                        {
                            await pushMessageService.PushPersonalOfferAsync(model.Db, model.Driver,
                                JsonConvert.DeserializeObject<PushPersonalOffer>(model.Json));
                        }
                        else
                        {
                            content = new PushPersonalOffer
                            {
                                Text =
                                    $"Test Text {DateTime.UtcNow.ToString("u", CultureInfo.InvariantCulture)} [Yandex](https://yandex.ru)",
                                Id = Guid.NewGuid().ToString("N"),
                                Action = "Yet Another Action",
                                ActionLink = "https://yandex.ru",
                                ActionLinkNeedAuth = false,
                                NeedNotification = true
                            };
                        }
                        break;
                    case PushMessageAction.ForcePollingOrder:
                        if (model.Json != null)
                        {
                            await pushMessageService.ForcePollingOrderAsync(model.Db, model.Driver);
                        }
                        else
                        {
                            content = new { };
                        }
                        break;
                    case PushMessageAction.DriverModeSubscriptionMessage:
                        if (model.Json != null)
                        {
                            var push = JsonConvert.DeserializeObject<JObject>(model.Json);
                            await pushMessageService.DriverModeSubscriptionMessageAsync(model.Db, model.Driver, push);
                        }
                        else
                        {
                            var pushData = "{\"keep_in_busy\": true, \"notifications\": [{\"delay_on_order\": false, \"fullscreen_notification\": {\"ui\": {\"bottom_items\": [{\"accent\": true, \"horizontal_divider_type\": \"none\", \"payload\": {\"type\": \"deeplink\", \"url\": \"taximeter://screen/driver_mode\"}, \"title\": \"Сменить режим дохода\", \"type\": \"button\"}], \"items\": [{\"gravity\": \"left\", \"horizontal_divider_type\": \"none\", \"subtitle\": \"Парк отключил режим дохода\", \"type\": \"header\"}, {\"horizontal_divider_type\": \"none\", \"padding\": \"small_bottom\", \"text\": \"Обратитесь в парк, чтобы узнать в чём дело или смените режим дохода\", \"type\": \"text\"}]}}, \"id\": \"driver_mode_subscription_notification_banned_by_park\", \"push_notification\": {\"button_deeplink\": \"taximeter://screen/driver_mode\", \"button_text\": \"Сменить режим дохода\", \"notification_header\": \"Парк отключил режим дохода\", \"notification_text\": \"Обратитесь в парк, чтобы узнать в чём дело или смените режим дохода\"}}]}";
                            content = JsonConvert.DeserializeObject<JObject>(pushData);
                        }
                        break;
                    case PushMessageAction.QuasiSelfemployedProposal:
                        if (model.Json != null)
                        {
                            var push = JsonConvert.DeserializeObject<JObject>(model.Json);
                            await pushMessageService.PushQuasiSelfemployedProposalAsync(model.Db, model.Driver, push);
                        }
                        else
                        {
                            var pushData = "{\"is_sms_code_check_needed\": true }";
                            content = JsonConvert.DeserializeObject<JObject>(pushData);
                        }
                        break;
                    default:
                        ModelState.AddModelError("", $"Тип сообщения {model.PushType} не поддерживается");
                        break;
                }
                if (content != null)
                {
                    model.Json = JsonConvert.SerializeObject(content, Formatting.Indented);
                }
            }
            return View(model);
        }

        private IPushMessageService SelectPushMessageService(TestPushModel model, IServiceProvider serviceProvider)
        {
            if (model.UseMessageQueue)
            {
                return new QueuePushMessageService(
                    serviceProvider.GetService<ILoggerFactory>(),
                    serviceProvider.GetService<IQueueService<PushMessageTask>>());
            }
            return new DirectPushMessageService(
                GetPushMessageProviders(model.Provider).ToArray(),
                serviceProvider.GetService<ILoggerFactory>(),
                serviceProvider.GetService<IDriverRepository>(),
                serviceProvider.GetService<ISetCarDtoConverter>(),
                serviceProvider.GetService<ICultureService>(),
                serviceProvider.GetService<IGlobalSettingsService>()
            );
        }

        private IEnumerable<IPushMessageProvider> GetPushMessageProviders(string providerType)
        {
            switch (providerType?.ToLower())
            {
                case "communications":
                    return _pushMessageProviders.Where(p => p is CommunicationsServiceProvider);
                case "client-notify":
                    return _pushMessageProviders.Where(p => p is ClientNotifyServiceProvider);
                default:
                    return _pushMessageProviders;
            }
        }

        [HttpGet("testmail")]
        public async Task<IActionResult> SendTestMessage(string to)
        {
            var fileAttachment = Encoding.UTF8.GetBytes("test file attachment content");
            await _mailClient.SendAsync("s-uskov@yandex-team.ru", new List<string>{ to },
                "test subj", "test msg", null,
                Tuple.Create("file.txt", fileAttachment));
            return Ok();
        }

        [HttpGet("testmailplain")]
        public async Task<IActionResult> SendTestMessagePlain(string to)
        {
            await _mailClient.SendAsync("s-uskov@yandex-team.ru", new List<string> { to },
                "test subj", "test msg", null);
            return Ok();
        }

        [HttpGet("testmds")]
        public async Task<ActionResult> TestMds()
        {
            var key = await _mdsClient.UploadAsync(Guid.NewGuid().ToString(),
                Encoding.UTF8.GetBytes(Guid.NewGuid().ToString()));
            var content2 = await _mdsClient.GetAsync(key);
            await _mdsClient.DeleteAsync(key);
            return Content(Encoding.UTF8.GetString(content2));
        }

        [HttpGet("testlog")]
        public ActionResult TestLog(string message)
        {
            _logger.LogInformation(message);
            return Content("OK");
        }

        [HttpGet("internallog")]
        public ActionResult InternalLog(string message)
        {
            InternalLogger.Info(message);
            return Json(new
            {
                InternalLogger.LogLevel,
                InternalLogger.LogFile,
                InternalLogger.LogToConsole,
                InternalLogger.LogToConsoleError,
                InternalLogger.LogToTrace,
                InternalLogger.IncludeTimestamp
            });
        }

        [Route("park_table_map")]
        public async Task<IActionResult> GetParkTableMapAsync(string db, [FromServices] IParkSqlTableMapService service)
        {
            var maps = new Dictionary<string, object>();
            foreach (var database in EnumExtensions.GetEnumValues<SqlDatabase>())
            {
                var dbMap = await service.GetParkMapAsync(db, database);
                maps[database.ToString()] = new {table = dbMap.Table, shard = dbMap.Shard};
            }

            return Content(
                JsonConvert.SerializeObject(maps, Formatting.Indented,
                    StaticHelper.JsonSerializerExplicitSettings),
                "application/json");
        }

        [Route("table_shard_map")]
        public async Task<IActionResult> GetTableShardMapAsync(string tableName,
            [FromServices] IParkSqlTableMapService service)
        {
            var mapping = await service.GetMappingAsync();
            if(mapping.TableShardMap.TryGetValue(tableName, out var shard))
            {
                return Json(new {shard});
            }
            return Json(null);
        }

        [Route("create_transaction")]
        public async Task<IActionResult> CreateTransactionAsync(string db, string driver,
            [FromServices]IPaySystemTransactionsService service)
        {
            var payId = Guid.NewGuid().ToString("n");
            await service.AddAsync(db, PaySystemType.Qiwi, payId, "1",
                TransactionFactor.Приход, 100.5, "описание", TransactionStatus.Accept, driver);
            var t = await service.ContainsAsync(db, PaySystemType.Qiwi, payId);
            return Ok(t.ToString());
        }

        [Route("control_characters_log")]
        public IActionResult ControlCharacterLogAsync()
        {
            var logMessage = "Following are contorl characters:";
            for (int ch = 0; ch < 10; ch++)
            {
                logMessage += (char) ch;
            }
            _logger.LogInformation(logMessage);
            return Ok();
        }

        [HttpGet("redis_lock_prolong_test")]
        public async Task<ActionResult> TestProlongAsync([FromServices] IRedisManagerAsync redisManager)
        {
            var l = redisManager.Lock.CreateLock("test-lock", withLog: true);
            try
            {
                await l.TakeAsync(TimeSpan.FromSeconds(10), TimeSpan.MaxValue);
                l.StartAutoProlongingTask(TimeSpan.FromMilliseconds(500), TimeSpan.FromSeconds(10));
                await Task.Delay(10000);
            }
            finally
            {
                await l.ReleaseAsync();
            }

            return Ok();
        }

        [Route("remove_gas_cabinet")]
        public async Task<IActionResult> RemoveGasCabinet(string db, [FromServices] IGasStationsService gasStations)
        {
            if (!StaticHelper.IsTesting())
                return NotFound();
            var result = await gasStations.RemoveGasStationsCabinetAsync(db);
            return Content(result);
        }

        [Route("test_personal")]
        public async Task<IActionResult> TestPersonal([FromServices]IPersonalDataLicensesGateway licenses)
        {
            var storeResponse = await licenses.StoreAsync("УУ11");
            var findResponse = await licenses.FindAsync("УУ11");
            var retrieveResponse = await licenses.RetrieveAsync(storeResponse.Id);

            Debug.Assert(storeResponse.Id == findResponse.Id);
            Debug.Assert(retrieveResponse.License == storeResponse.License);

            var bulkStoreResponse = await licenses.BulkStoreAsync(new[] {"УУ22", "УУ33"});
            var bulkRetrieveAsync = await licenses.BulkRetrieveAsync(bulkStoreResponse.Items.Select(x => x.Id).ToList());

            Debug.Assert(bulkRetrieveAsync.Items.FirstOrDefault(x => x.License == "YY22") != null);
            Debug.Assert(bulkRetrieveAsync.Items.FirstOrDefault(x => x.License == "YY33") != null);

            return Ok();
        }

        [Route("test_voice")]
        public async Task<IActionResult> TestSms([FromQuery]string db,
            [FromQuery]string order,
            [FromQuery]string driver,
            [FromQuery]SmsNotificationType smsNotificationType,
            [FromServices] ISmsService smsService)
        {
            if (!StaticHelper.IsTesting())
                return NotFound();
            await smsService.CreateNotification(smsNotificationType,
                db,
                order,
                driver);
            return Ok();
        }
    }
}
