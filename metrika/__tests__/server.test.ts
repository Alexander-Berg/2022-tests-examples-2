import fetch from 'node-fetch';
import { readFile } from 'fs/promises';
import { AuthenticationMode } from '@server-libs/http-server/auth';
import { Get, HttpController, Post, Put, Qualifier } from '@server-libs/http-server/decorators';
import { HttpMethod } from '@server-libs/http-server/method';
import {
    BadRequestError,
    ForbiddenError,
    LOCKED_ERROR,
    NotFoundError,
    RuntimeError,
    UnauthorizedError,
} from '@server-libs/node-tools/error';
import { ServerTestStage } from './server-test-stage';
import { CustomResponse, HttpRequest, FileResponse } from '@server-libs/http-server/controller';
import { decodeBase64ToUtf } from '@server-libs/node-tools/string';
import { TvmClient } from '@server-libs/tvm-client/tvm-client';
import { URL } from 'url';
import { HttpHeader } from '@shared/http/http-header';
import { BlackboxClient } from '@server-libs/blackbox-client/client';
import { BlackboxUserField, UserInfo } from '@server-libs/blackbox-client/api';
import { ContentType } from '@server-libs/http-server/content-type';
import { ContextProvider } from '@server-libs/http-server/options';
import { Request } from 'express';
import { LoggerApi } from '../../node-tools/logger';
import { HttpCode } from '@shared/http/code';

jest.mock('fs/promises');

jest.mock('node-fetch');

const mockWarn = jest.fn();
const mockInfo = jest.fn();
const mockError = jest.fn();

const devPort = 8090;

const logger: LoggerApi = {
    info: mockInfo,
    warn: mockWarn,
    error: mockError,
    fatal: jest.fn(),
    withTag: jest.fn(),
    withTags: jest.fn(),
};

jest.mock('@server-libs/node-tools/string.ts', () => {
    const original = jest.requireActual<Record<string, string>>('@server-libs/node-tools/string');
    return {
        ...original,
        decodeBase64ToUtf: jest.fn(),
    };
});

const mockDecodeBase64ToUtf = <jest.Mock>decodeBase64ToUtf;
const mockFsReadFile = <jest.Mock>readFile;
const mockFetch = fetch as unknown as jest.Mock;

describe('server', () => {
    const contextProvider: ContextProvider<Record<string, unknown>> = () => Promise.resolve({});

    @HttpController('errors')
    class ErrorController {
        @Get('bad1')
        badRequest1(): never {
            throw new SyntaxError('wrong syntax');
        }

        @Get('bad2')
        badRequest2(): never {
            throw new BadRequestError('bad get request');
        }

        @Post('bad2')
        badPostRequest2(): never {
            throw new BadRequestError('bad post request');
        }

        @Get('unauthorized')
        unauthorizedError(): never {
            throw new UnauthorizedError('you are not authorized');
        }

        @Get('forbidden')
        forbiddenError(): never {
            throw new ForbiddenError('you are forbidden');
        }

        @Get('notfound')
        notFoundGetError(): never {
            throw new NotFoundError('you are not found get');
        }

        @Post('notfound')
        notFoundPostError(): never {
            throw new NotFoundError('you are not found post');
        }

        @Get('locked')
        lockedRoomError(): never {
            throw new RuntimeError(LOCKED_ERROR, 'you are locked');
        }

        @Get('defaultError')
        defaultError(): never {
            throw new Error('undefined is not a function');
        }
    }

    beforeEach(() => {
        mockInfo.mockClear();
        mockWarn.mockClear();
        mockError.mockClear();
        mockDecodeBase64ToUtf.mockClear();
        mockFsReadFile.mockClear();
        mockFetch.mockClear();
    });

    describe('routing', () => {
        const mockQualifier = jest.fn();
        const mockCtx = {};

        @HttpController()
        class TestController1 {
            @Get('/test1')
            getTest1(): string {
                return 'test 1';
            }

            @Get('/test1/one')
            getTest1One(): string {
                return 'test 1 one';
            }

            @Post('/test1')
            postTest1(): string {
                return 'post test 1';
            }

            @Put('/test1')
            putTest1(): string {
                return 'put test 1';
            }
        }

        @HttpController('/v2')
        class TestController2 {
            @Post('/test2')
            postTest2(): string {
                return 'post test 2';
            }

            @Get('/test2')
            getTest2(): string {
                return 'test 2';
            }
        }

        @HttpController('v3/test3')
        class TestController3 {
            @Get('/route3')
            getRoute3(): string {
                return 'three';
            }

            @Get('route3/sub/route')
            getSubRoute(): string {
                return 'sub three';
            }

            @Get('/qualified')
            @Qualifier(mockQualifier)
            getWithQualified1(): string {
                return 'qualifier 1';
            }

            @Get('/qualified')
            @Qualifier(mockQualifier)
            getWithQualified2(): string {
                return 'qualifier 2';
            }
        }

        const stage = new ServerTestStage(
            {
                authMode: AuthenticationMode.Disabled,
                controllersGroups: [
                    {
                        controllers: [new TestController1(), new TestController2(), new TestController3()],
                        contextProvider: (): Promise<Record<string, void>> => Promise.resolve(mockCtx),
                    },
                ],
                logger,
            },
            devPort
        );

        beforeEach(() => {
            mockQualifier.mockClear();
        });

        beforeAll(async () => {
            await stage.start();
        });

        afterAll(async () => {
            await stage.stop();
        });

        it('should handle get requests in single controller', async () => {
            const { data: data1 } = await stage.requestText('/test1');
            expect(data1).toBe('test 1');

            const { data: data2 } = await stage.requestText('/test1/one');
            expect(data2).toBe('test 1 one');
        });

        it('should handle get requests in multiple controllers', async () => {
            const { data: data1 } = await stage.requestText('/test1');
            expect(data1).toBe('test 1');

            const { data: data2 } = await stage.requestText('/v2/test2');
            expect(data2).toBe('test 2');
        });

        it('should handle different HTTP methods', async () => {
            const { data: postData } = await stage.requestText('/test1', HttpMethod.Post);
            expect(postData).toBe('post test 1');

            const { data: putData } = await stage.requestText('/test1', HttpMethod.Put);
            expect(putData).toBe('put test 1');

            const { data: postData2 } = await stage.requestText('/v2/test2', HttpMethod.Post);
            expect(postData2).toBe('post test 2');
        });

        it('should consider base controller path in route resolution', async () => {
            const { data: data1 } = await stage.requestText('/v2/test2');
            expect(data1).toBe('test 2');

            const { data: data2 } = await stage.requestText('/v3/test3/route3');
            expect(data2).toBe('three');

            const { data: data3 } = await stage.requestText('/v3/test3/route3/sub/route');
            expect(data3).toBe('sub three');
        });

        it('should consider qualifiers', async () => {
            mockQualifier.mockReturnValueOnce(true).mockReturnValueOnce(false).mockReturnValueOnce(true);

            const { data: data1 } = await stage.requestText('/v3/test3/qualified');
            const { data: data2 } = await stage.requestText('/v3/test3/qualified');

            expect(data1).toBe('qualifier 1');
            expect(data2).toBe('qualifier 2');

            expect(mockQualifier.mock.calls.length).toBe(3);
            mockQualifier.mock.calls.forEach(([qualifierArg]) => {
                expect(qualifierArg).toBe(mockCtx);
            });
        });

        it('should give 404 in case of non existing routes', async () => {
            const { data: data1, code: code1 } = await stage.requestText('/v3/test3/qualifi');
            const { data: data2, code: code2 } = await stage.requestText('/non/existing/route');

            expect(data1).toBe('Not Found');
            expect(data2).toBe(data1);

            expect(code1).toBe(404);
            expect(code2).toBe(code1);
        });
    });

    describe('logs', () => {
        function getInfoLogs(): string[] {
            return mockInfo.mock.calls.map((infoCall: string[]) => {
                expect(infoCall.length).toBe(1);
                return infoCall[0];
            });
        }

        function getWarnLogs(): string[] {
            return mockWarn.mock.calls.map(([warnLog]: string[]) => warnLog);
        }

        function getErrorLogs(): string[] {
            return mockError.mock.calls.map(([errorLog]: string[]) => errorLog);
        }

        @HttpController()
        class TestController1 {
            @Get('/test1')
            getTest1(): string {
                return 'test 1';
            }
        }

        @HttpController('v2')
        class TestController2 {
            @Post('/test2')
            postTest2(): string {
                return 'test 2';
            }

            @Put('/test2')
            putTest2(): string {
                return 'test 2';
            }
        }

        const stage = new ServerTestStage(
            {
                authMode: AuthenticationMode.Disabled,
                controllersGroups: [
                    {
                        controllers: [new TestController1(), new TestController2(), new ErrorController()],
                        contextProvider: (): Promise<Record<string, void>> => Promise.resolve({}),
                    },
                ],
                logger,
                requestLoggerProvider: (): LoggerApi => logger,
            },
            devPort
        );

        beforeAll(async () => {
            await stage.start();
        });

        afterAll(async () => {
            await stage.stop();
        });

        it('should log requests to handlers', async () => {
            function testLogsForHandler(
                logs: string[],
                handlerPath: string,
                handlerName: string,
                method: HttpMethod = HttpMethod.Get
            ): void {
                expect(logs[0]).toBe(`Receive request ${method} ${handlerPath}, invoke handler=${handlerName}`);
                expect(logs[1]).toMatch(new RegExp(`200_OK ${method} ${handlerPath} \\(\\d+ms\\)`));
            }

            await stage.requestText('/test1');
            await stage.requestText('/v2/test2', HttpMethod.Post);
            await stage.requestText('/v2/test2', HttpMethod.Put);

            const logs = getInfoLogs();
            expect(logs.length).toBe(6);

            testLogsForHandler(logs.slice(0, 2), '/test1', 'getTest1');
            testLogsForHandler(logs.slice(2, 4), '/v2/test2', 'postTest2', HttpMethod.Post);
            testLogsForHandler(logs.slice(4, 6), '/v2/test2', 'putTest2', HttpMethod.Put);

            expect(mockError.mock.calls.length).toBe(0);
            expect(mockWarn.mock.calls.length).toBe(0);
        });

        it('should log not found errors', async () => {
            await stage.requestText('/some/route');
            await stage.requestText('/some/other/route', HttpMethod.Put);
            await stage.requestText('/errors/notfound');
            await stage.requestData('/errors/notfound', HttpMethod.Post, { notfound: 1 });

            const warnLogs = getWarnLogs();
            expect(warnLogs.length).toBe(6);

            expect(warnLogs[0]).toBe('404_NOT_FOUND GET /some/route');
            expect(warnLogs[1]).toBe('404_NOT_FOUND PUT /some/other/route');

            expect(warnLogs[2]).toMatch(
                /404_NOT_FOUND GET \/errors\/notfound \(\d+ms\), reason: you are not found get/
            );
            expect(warnLogs[3]).toBe('Req Body: {}');

            expect(warnLogs[4]).toMatch(
                /404_NOT_FOUND POST \/errors\/notfound \(\d+ms\), reason: you are not found post/
            );
            expect(warnLogs[5]).toBe('Req Body: {"notfound":1}');

            expect(getInfoLogs().length).toBe(2);
            expect(getErrorLogs().length).toBe(0);
        });

        it('should log bad request errors', async () => {
            await stage.requestText('/errors/bad1');
            await stage.requestText('/errors/bad2');
            await stage.requestData('/errors/bad2', HttpMethod.Post, { bad: 2 });

            const warnLogs = getWarnLogs();
            expect(warnLogs.length).toBe(5);

            expect(warnLogs[0]).toMatch(/400_BAD_REQUEST GET \/errors\/bad1 \(\d+ms\), reason: wrong syntax/);
            expect(warnLogs[1]).toMatch(
                /400_BAD_REQUEST GET \/errors\/bad2 \(\d+ms\), reason: \[BAD_REQUEST_ERROR\]: bad get request/
            );
            expect(warnLogs[2]).toBe('Req Body: {}');
            expect(warnLogs[3]).toMatch(
                /400_BAD_REQUEST POST \/errors\/bad2 \(\d+ms\), reason: \[BAD_REQUEST_ERROR\]: bad post request/
            );
            expect(warnLogs[4]).toBe('Req Body: {"bad":2}');

            expect(getInfoLogs().length).toBe(3);
            expect(getErrorLogs().length).toBe(0);
        });

        it('should log unauthorized errors', async () => {
            await stage.requestText('/errors/unauthorized');

            const warnLogs = getWarnLogs();
            expect(warnLogs.length).toBe(1);

            expect(warnLogs[0]).toMatch(
                /401_NOT_UNAUTHORIZED GET \/errors\/unauthorized \(\d+ms\), details: you are not authorized/
            );
            expect(getInfoLogs().length).toBe(1);
            expect(getErrorLogs().length).toBe(0);
        });

        it('should log forbidden errors', async () => {
            await stage.requestText('/errors/forbidden');

            const warnLogs = getWarnLogs();
            expect(warnLogs.length).toBe(1);

            expect(warnLogs[0]).toMatch(/403_FORBIDDEN GET \/errors\/forbidden \(\d+ms\), details: you are forbidden/);

            expect(getInfoLogs().length).toBe(1);
            expect(getErrorLogs().length).toBe(0);
        });

        it('should log locked errors', async () => {
            await stage.requestText('/errors/locked');

            const warnLogs = getWarnLogs();
            expect(warnLogs.length).toBe(1);

            expect(warnLogs[0]).toMatch(/423_LOCKED GET \/errors\/locked \(\d+ms\), details: you are locked/);

            expect(getInfoLogs().length).toBe(1);
            expect(getErrorLogs().length).toBe(0);
        });

        it('should log server errors', async () => {
            await stage.requestText('/errors/defaultError');

            const errorLogs = mockError.mock.calls.map((logs: [string, Error]) => logs);
            const [[errorLog1, errorLog2]] = errorLogs;
            expect(errorLogs.length).toBe(1);

            expect(errorLog1).toMatch(/500_INTERNAL_ERROR GET \/errors\/defaultError \(\d+ms\)/);
            expect(errorLog2).toMatch('undefined is not a function');
            expect(errorLog2).toMatch('stack');

            expect(getInfoLogs().length).toBe(1);
            expect(getWarnLogs().length).toBe(0);
        });
    });

    describe('authentication', () => {
        let stage: ServerTestStage;

        @HttpController()
        class AuthController {
            @Get('/')
            getAuth(): string {
                return 'get ok';
            }

            @Post('/')
            postAuth(): string {
                return 'post ok';
            }

            @Get({
                path: '/anonymous',
                isAuthRequired: false,
            })
            getAnonymous(): string {
                return 'anonymous ok';
            }
        }

        const authGetSpy = jest.spyOn(AuthController.prototype, 'getAuth');
        const authPostSpy = jest.spyOn(AuthController.prototype, 'postAuth');
        const authAnonymousSpy = jest.spyOn(AuthController.prototype, 'getAnonymous');
        const tvmCheckServiceSpy = jest.spyOn(TvmClient.prototype, 'checkService');
        const blackboxUserInfoSpy = jest.spyOn(BlackboxClient.prototype, 'getUserInfo');

        const tvmClient = new TvmClient(new URL('http://localhost:8001/tvm'), 'tvmtool-development-access-token');
        const blackboxClient = new BlackboxClient(new URL('https://blackbox-mimino.yandex.net'), tvmClient, '239');

        function getRequestObjects(): HttpRequest[] {
            const calls = authGetSpy.mock.calls
                .concat(authPostSpy.mock.calls)
                .concat(authAnonymousSpy.mock.calls) as HttpRequest[][];

            return calls.map(([req]) => req);
        }

        beforeEach(() => {
            authGetSpy.mockClear();
            authPostSpy.mockClear();
            authAnonymousSpy.mockClear();
            tvmCheckServiceSpy.mockClear();
            blackboxUserInfoSpy.mockClear();
        });

        afterEach(async () => {
            if (stage?.isActive()) {
                await stage.stop();
            }
        });

        it('should disable authentication in disabled mode', async () => {
            stage = new ServerTestStage(
                {
                    authMode: AuthenticationMode.Disabled,
                    controllersGroups: [
                        {
                            controllers: [new AuthController()],
                            contextProvider,
                        },
                    ],
                    logger,
                },
                devPort
            );

            await stage.start();

            const { code, data } = await stage.requestText('/');

            const [req] = getRequestObjects();

            expect(req.auth).toEqual({ isDisabled: true });
            expect(code).toBe(HttpCode.Ok);
            expect(data).toBe('get ok');
        });

        it('should verify Authorization header in basic authentication mode', async () => {
            stage = new ServerTestStage(
                {
                    authMode: AuthenticationMode.Basic,
                    controllersGroups: [
                        {
                            controllers: [new AuthController()],
                            contextProvider,
                        },
                    ],
                    logger,
                },
                devPort
            );

            const ENCODED_HEADER = '84903284938';
            const DECODED_HEADER = '37493749278';

            mockDecodeBase64ToUtf.mockReturnValueOnce(DECODED_HEADER);

            await stage.start();
            await stage.requestText('/', HttpMethod.Get, {
                headers: {
                    [HttpHeader.Authorization]: `Basic ${ENCODED_HEADER}`,
                },
            });

            const [req1] = getRequestObjects();

            expect(mockDecodeBase64ToUtf.mock.calls.length).toBe(1);

            const [[decodeBase64Arg]] = mockDecodeBase64ToUtf.mock.calls as string[][];

            expect(decodeBase64Arg).toBe(ENCODED_HEADER);
            expect(req1.auth).toEqual({ credentials: DECODED_HEADER });
        });

        it('should reject if no or incorrect Authorization header provided in basic authentication mode', async () => {
            stage = new ServerTestStage(
                {
                    authMode: AuthenticationMode.Basic,
                    controllersGroups: [
                        {
                            controllers: [new AuthController()],
                            contextProvider,
                        },
                    ],
                    logger,
                },
                devPort
            );

            await stage.start();

            const { data: data1, code: code1 } = await stage.requestText('/');
            const { data: data2, code: code2 } = await stage.requestText('/', HttpMethod.Post, {
                headers: { Authorization: 'invalid' },
            });

            expect(data1).toBe('Unauthorized');
            expect(data2).toBe('Unauthorized');

            expect(code1).toBe(HttpCode.Unauthorized);
            expect(code2).toBe(HttpCode.Unauthorized);
        });

        it('should allow making request to anonymous handler for basic authentication type', async () => {
            stage = new ServerTestStage(
                {
                    authMode: AuthenticationMode.Basic,
                    controllersGroups: [
                        {
                            controllers: [new AuthController()],
                            contextProvider,
                        },
                    ],
                    logger,
                },
                devPort
            );

            await stage.start();

            const { code, data } = await stage.requestText('/anonymous');

            expect(code).toBe(HttpCode.Ok);
            expect(data).toBe('anonymous ok');
        });

        it('should verify X-Ya-Service-Ticket header in tvm authentication mode', async () => {
            stage = new ServerTestStage(
                {
                    tvmClient,
                    authMode: AuthenticationMode.TvmService,
                    controllersGroups: [
                        {
                            controllers: [new AuthController()],
                            contextProvider,
                        },
                    ],
                    logger,
                },
                devPort
            );

            const TICKET = '12324435435';
            const SERVICE_ID = '08679875432';

            tvmCheckServiceSpy.mockReturnValueOnce(Promise.resolve(SERVICE_ID));

            await stage.start();
            await stage.requestText('/', HttpMethod.Get, {
                headers: {
                    [HttpHeader.XYaServiceTicket]: TICKET,
                },
            });

            const [req] = getRequestObjects();

            expect(req.auth).toEqual({ tvmServiceId: SERVICE_ID });
            expect(tvmCheckServiceSpy.mock.calls.length).toBe(1);
            expect(tvmCheckServiceSpy.mock.calls[0][0]).toBe(TICKET);
        });

        it('should reject if no or incorrect X-Ya-Service-Ticket header provided in tvm authentication mode', async () => {
            stage = new ServerTestStage(
                {
                    tvmClient,
                    authMode: AuthenticationMode.TvmService,
                    controllersGroups: [
                        {
                            controllers: [new AuthController()],
                            contextProvider,
                        },
                    ],
                    logger,
                },
                devPort
            );

            const TICKET = '12324435435';

            await stage.start();
            const { code: code1, data: data1 } = await stage.requestText('/');

            expect(code1).toBe(HttpCode.Unauthorized);
            expect(data1).toBe('Unauthorized');

            tvmCheckServiceSpy.mockImplementationOnce(() => {
                throw new Error('test error');
            });

            const { code: code2, data: data2 } = await stage.requestText('/', HttpMethod.Get, {
                headers: {
                    [HttpHeader.XYaServiceTicket]: TICKET,
                },
            });

            expect(tvmCheckServiceSpy.mock.calls.length).toBe(1);
            expect(tvmCheckServiceSpy.mock.calls[0][0]).toBe(TICKET);
            expect(code2).toBe(HttpCode.Unauthorized);
            expect(data2).toBe('Unauthorized');
        });

        it('should allow making request to anonymous handler for tvm authentication type', async () => {
            stage = new ServerTestStage(
                {
                    tvmClient,
                    authMode: AuthenticationMode.TvmService,
                    controllersGroups: [
                        {
                            controllers: [new AuthController()],
                            contextProvider,
                        },
                    ],
                    logger,
                },
                devPort
            );

            await stage.start();

            const { code, data } = await stage.requestText('/anonymous');

            expect(code).toBe(HttpCode.Ok);
            expect(data).toBe('anonymous ok');
        });

        it('should get user data from blackbox in blackbox authentication mode', async () => {
            stage = new ServerTestStage(
                {
                    tvmClient,
                    isCookieParserEnabled: true,
                    blackboxOptions: {
                        client: blackboxClient,
                        requiredFields: [BlackboxUserField.Login],
                    },
                    authMode: AuthenticationMode.Blackbox,
                    controllersGroups: [
                        {
                            controllers: [new AuthController()],
                            contextProvider,
                        },
                    ],
                    logger,
                },
                devPort
            );

            await stage.start();

            const UID = '623463278';
            const USER_TICKET = '27359843758';
            const LOGIN = '375743587';
            const DISPLAY_NAME = '';

            blackboxUserInfoSpy.mockReturnValueOnce(
                Promise.resolve({
                    currentUid: UID,
                    userTicket: USER_TICKET,
                    accounts: [
                        {
                            uid: UID,
                            displayName: DISPLAY_NAME,
                            requiredFields: new Map<BlackboxUserField, string>([[BlackboxUserField.Login, LOGIN]]),
                        },
                    ],
                } as UserInfo)
            );

            const SESSION_ID = '36463463';
            const SESSION_ID2 = '58934857';

            await stage.requestText('/', HttpMethod.Get, {
                cookies: {
                    Session_id: SESSION_ID,
                    sessionid2: SESSION_ID2,
                },
            });

            const [req] = getRequestObjects();

            expect(blackboxUserInfoSpy.mock.calls.length).toBe(1);

            const [[blackboxUserInfoArg]] = blackboxUserInfoSpy.mock.calls;

            expect(blackboxUserInfoArg.sessionId).toBe(SESSION_ID);
            expect(blackboxUserInfoArg.sessionId2).toBe(SESSION_ID2);
            expect(blackboxUserInfoArg.requiredFields).toEqual([BlackboxUserField.Login]);

            expect(typeof blackboxUserInfoArg.host).toBe('string');
            expect(blackboxUserInfoArg.userIP).toMatch(/\d+\.\d+\.\d+\.\d+$/);

            expect(req.auth).toEqual({
                userInfo: {
                    currentUid: UID,
                    userTicket: USER_TICKET,
                    accounts: [
                        {
                            uid: UID,
                            displayName: DISPLAY_NAME,
                            requiredFields: new Map([[BlackboxUserField.Login, LOGIN]]),
                        },
                    ],
                },
            });
        });

        it('should reject if blackbox cookie is invalid in blackbox authentication mode', async () => {
            stage = new ServerTestStage(
                {
                    tvmClient,
                    isCookieParserEnabled: true,
                    blackboxOptions: {
                        client: blackboxClient,
                        requiredFields: [BlackboxUserField.Login],
                    },
                    authMode: AuthenticationMode.Blackbox,
                    controllersGroups: [
                        {
                            controllers: [new AuthController()],
                            contextProvider,
                        },
                    ],
                    logger,
                },
                devPort
            );

            await stage.start();

            blackboxUserInfoSpy.mockImplementationOnce(() => {
                throw new UnauthorizedError('test error');
            });

            const { code, data } = await stage.requestText('/');

            expect(code).toBe(HttpCode.Unauthorized);
            expect(data).toBe('Unauthorized');
            expect(blackboxUserInfoSpy.mock.calls.length).toBe(1);

            const [[blackboxUserInfoArg]] = blackboxUserInfoSpy.mock.calls;

            expect(blackboxUserInfoArg.sessionId).toBe('');
            expect(blackboxUserInfoArg.sessionId2).toBe(undefined);
            expect(blackboxUserInfoArg.requiredFields).toEqual([BlackboxUserField.Login]);
            expect(typeof blackboxUserInfoArg.host).toBe('string');
            expect(blackboxUserInfoArg.userIP).toMatch(/\d+\.\d+\.\d+\.\d+$/);
        });

        it('should send 500 in case of blackbox errors', async () => {
            stage = new ServerTestStage(
                {
                    tvmClient,
                    isCookieParserEnabled: true,
                    blackboxOptions: {
                        client: blackboxClient,
                        requiredFields: [BlackboxUserField.Login],
                    },
                    authMode: AuthenticationMode.Blackbox,
                    controllersGroups: [
                        {
                            controllers: [new AuthController()],
                            contextProvider,
                        },
                    ],
                    logger,
                },
                devPort
            );

            await stage.start();

            blackboxUserInfoSpy.mockImplementationOnce(() => {
                // not auth error
                throw new Error('test error');
            });

            const { code, data } = await stage.requestText('/');

            expect(code).toBe(HttpCode.InternalError);
            expect(data).toBe('Internal Server Error');
            expect(blackboxUserInfoSpy.mock.calls.length).toBe(1);
        });

        it('should allow making request to anonymous handler for blackbox authentication type', async () => {
            stage = new ServerTestStage(
                {
                    tvmClient,
                    isCookieParserEnabled: true,
                    blackboxOptions: {
                        client: blackboxClient,
                        requiredFields: [BlackboxUserField.Login],
                    },
                    authMode: AuthenticationMode.Blackbox,
                    controllersGroups: [
                        {
                            controllers: [new AuthController()],
                            contextProvider,
                        },
                    ],
                    logger,
                },
                devPort
            );

            await stage.start();

            const { code, data } = await stage.requestText('/anonymous');

            expect(code).toBe(HttpCode.Ok);
            expect(data).toBe('anonymous ok');
        });
    });

    describe('handlers return type', () => {
        const url = new URL('https://api-metrika.yandex.net/stat/v1/data');

        @HttpController()
        class ReturnTypeController {
            @Get('string')
            getString(): string {
                return 'string response';
            }

            @Get('custom')
            getCustom(): CustomResponse {
                return new CustomResponse(ContentType.SVG, '<svg />');
            }

            @Get('static/string')
            getFile(): FileResponse {
                return new FileResponse({ source: '/media/string1' });
            }

            @Get('static/string-content-type')
            getFileContentType(): FileResponse {
                return new FileResponse({
                    source: '/media/string2',
                    contentType: ContentType.ApplicationJavascript,
                });
            }

            @Get('static/url')
            getStaticUrl(): FileResponse {
                return new FileResponse({
                    source: url,
                    contentType: ContentType.TextCss,
                });
            }
        }

        function getContentType(type: ContentType): string {
            return `${type}; charset=utf-8`;
        }

        const stage = new ServerTestStage(
            {
                authMode: AuthenticationMode.Disabled,
                controllersGroups: [
                    {
                        controllers: [new ReturnTypeController()],
                        contextProvider,
                    },
                ],
                logger,
            },
            devPort
        );

        beforeAll(async () => {
            await stage.start();
        });

        afterAll(async () => {
            await stage.stop();
        });

        it('should handle string response type', async () => {
            const { code, data, headers } = await stage.requestText('/string');

            expect(code).toBe(HttpCode.Ok);
            expect(data).toBe('string response');
            expect(headers).toEqual({
                [HttpHeader.ContentType]: getContentType(ContentType.TextHtml),
                [HttpHeader.ContentLength]: '15',
            });
        });

        it('should send custom content-type and body in case of custom response', async () => {
            const { code, data, headers } = await stage.requestText('custom');

            expect(code).toBe(HttpCode.Ok);
            expect(data).toBe('<svg />');
            expect(headers).toEqual({
                [HttpHeader.ContentType]: getContentType(ContentType.SVG),
                [HttpHeader.ContentLength]: '7',
            });
        });

        it('should send file in case of static response', async () => {
            const FILE = 'q42343244sd';

            mockFsReadFile.mockImplementationOnce(() =>
                Promise.resolve({
                    toString() {
                        return FILE;
                    },
                })
            );

            const { code, data, headers } = await stage.requestText('/static/string');

            const [[filePath]] = mockFsReadFile.mock.calls as string[][];

            expect(mockFsReadFile.mock.calls.length).toBe(1);
            expect(filePath).toBe('/media/string1');
            expect(code).toBe(HttpCode.Ok);
            expect(data).toBe(FILE);
            expect(headers).toEqual({
                [HttpHeader.ContentLength]: '11',
                [HttpHeader.ContentType]: getContentType(ContentType.TextHtml),
            });
        });

        it('should allow to set custom content-type in case of static response', async () => {
            await stage.requestText('/static/url');

            // todo ilyakortasov: continue
            expect(mockFetch.mock.calls.length).toBe(1);
        });

        it('should make request in case of url passed to static response', async () => {});

        it('should cache content in case of static response', async () => {
            // todo: URL + readFile
            // todo ilyakortasov: case where we have shouldCache = false
            // todo ilyakortasov: StaticResponse.prototype.processContent
        });

        it('should handle I/O errors in case of static response', async () => {});

        it('should redirect in case of redirect response', async () => {});

        it('should stream data in case of stream response', async () => {});

        it('should send custom content type and body in case of stream response', async () => {});
    });

    describe('errors', () => {
        const stage = new ServerTestStage(
            {
                authMode: AuthenticationMode.Disabled,
                controllersGroups: [
                    {
                        controllers: [new ErrorController()],
                        contextProvider: (): Promise<Record<string, void>> => Promise.resolve({}),
                    },
                ],
                logger,
            },
            devPort
        );

        beforeAll(async () => {
            await stage.start();
        });

        afterAll(async () => {
            await stage.stop();
        });

        it('should send 400 bad request error in case of SyntaxError', async () => {
            const { data: data1, code: code1 } = await stage.requestText('/errors/bad1');
            const { data: data2, code: code2 } = await stage.requestText('/errors/bad2');
            const { data: data3, code: code3 } = await stage.requestData('/errors/bad2', HttpMethod.Post, { bad: 2 });

            [code1, code2, code3].forEach(code => {
                expect(code).toBe(HttpCode.BadRequest);
            });

            expect(JSON.parse(data1)).toEqual({ error: 'wrong syntax' });
            expect(JSON.parse(data2)).toEqual({ error: 'bad get request' });
            expect(data3).toEqual({ error: 'bad post request' });
        });

        it('should send 401 unauthorized in case of authentication error', async () => {
            const { data, code } = await stage.requestText('/errors/unauthorized');

            expect(data).toBe('Unauthorized');
            expect(code).toBe(HttpCode.Unauthorized);
        });

        it('should send 403 forbidden in case of authorization error', async () => {
            const { data, code } = await stage.requestText('/errors/forbidden');

            expect(data).toBe('Forbidden');
            expect(code).toBe(HttpCode.Forbidden);
        });

        it('should send 404 in case of request to non-existent handler', async () => {
            const { data: data1, code: code1 } = await stage.requestText('/some/route');
            const { data: data2, code: code2 } = await stage.requestText('/some/other/route', HttpMethod.Put);

            [data1, data2].forEach(data => {
                expect(data).toBe('Not Found');
            });

            [code1, code2].forEach(code => {
                expect(code).toBe(HttpCode.NotFound);
            });
        });

        it('should send 404 in case of handler throwing 404 error', async () => {
            const { data: data1, code: code1 } = await stage.requestText('/errors/notfound');
            const { data: data2, code: code2 } = await stage.requestData('/errors/notfound', HttpMethod.Post, {
                notfound: 1,
            });

            [code1, code2].forEach(code => {
                expect(code).toBe(HttpCode.NotFound);
            });

            expect(JSON.parse(data1)).toEqual({ error: 'you are not found get' });
            expect(data2).toEqual({ error: 'you are not found post' });
        });

        it('should send 423 locked in case of locked error', async () => {
            const { data, code } = await stage.requestText('/errors/locked');

            expect(code).toBe(HttpCode.LockedError);
            expect(data).toBe('Locked');
        });

        it('should send 500 error in case of server internal error', async () => {
            const { data, code } = await stage.requestText('/errors/defaultError');

            expect(data).toBe('Internal Server Error');
            expect(data).not.toBe('undefined is not a function');
            expect(code).toBe(HttpCode.InternalError);
        });
    });

    describe('file upload', () => {
        it.skip('should receive and write files to disk', () => {});

        it.skip('should pass files to handlers for every request', () => {});
    });

    describe('configuration options', () => {
        @HttpController('v1')
        class TestController {
            @Get('/test')
            getTest(req: Request, ctx: unknown): string {
                return 'test';
            }
        }

        @HttpController('v2')
        class TestController2 {
            @Get('/test2')
            getTest(req: Request, ctx: unknown): string {
                return 'test2';
            }
        }

        const ctx1 = {};
        const ctx2 = {};
        const ctxProviderMock = jest.fn().mockImplementation(() => ctx1);
        const ctxProviderMock2 = jest.fn().mockImplementation(() => ctx2);
        const controller1Spy = jest.spyOn(TestController.prototype, 'getTest');
        const controller2Spy = jest.spyOn(TestController2.prototype, 'getTest');

        const stage = new ServerTestStage(
            {
                authMode: AuthenticationMode.Disabled,
                controllersGroups: [
                    {
                        controllers: [new TestController()],
                        contextProvider: ctxProviderMock,
                    },
                    {
                        controllers: [new TestController2()],
                        contextProvider: ctxProviderMock2,
                    },
                ],
                logger,
            },
            devPort
        );

        beforeAll(async () => {
            ctxProviderMock.mockClear();
            ctxProviderMock2.mockClear();
            controller1Spy.mockClear();
            controller2Spy.mockClear();

            await stage.start();
        });

        afterAll(async () => {
            await stage.stop();
        });

        it.skip('should trigger error if blackbox auth is used and cookie parser disabled', () => {});

        it.skip('should trigger error if there are no qualifiers for handlers with the same path', () => {});

        it.skip('should trigger error if handlers with the same path have different isAuthRequired option', () => {});

        it.skip('should trigger error if handlers require multipart files but hasMultipartFormSupport is false', () => {});

        it('should trigger error if handlers with the same path belongs to diffrent groups of controllers', () => {
            const basePath = 'v1';
            const relativePath = '/test';

            @HttpController(basePath)
            class SamePathTestController {
                @Get(relativePath)
                getTest(): string {
                    return 'test';
                }
            }

            @HttpController(basePath)
            class SamePathTestController2 {
                @Get(relativePath)
                getTest(): string {
                    return 'test2';
                }
            }

            const createState = (): ServerTestStage =>
                new ServerTestStage(
                    {
                        authMode: AuthenticationMode.Disabled,
                        controllersGroups: [
                            {
                                controllers: [new SamePathTestController()],
                                contextProvider: ctxProviderMock,
                            },
                            {
                                controllers: [new SamePathTestController2()],
                                contextProvider: ctxProviderMock,
                            },
                        ],
                        logger,
                    },
                    devPort
                );

            expect(createState).toThrow(
                `invalid controller instance, handlers with the same path must belong to the same set of controllers – /${basePath}${relativePath}`
            );
        });

        it('should invoke context provider once per every request', async () => {
            await stage.requestText('/v1/test');

            expect(ctxProviderMock).toHaveBeenCalledTimes(1);
        });

        it('should invoke controller methods with the corresponded context', async () => {
            await stage.requestText('/v1/test');
            await stage.requestText('/v2/test2');

            expect(controller1Spy.mock.calls[0][1]).toBe(ctx1);
            expect(controller2Spy.mock.calls[0][1]).toBe(ctx2);
        });

        it.skip('should invoke setupRequestLogger per every request', () => {});

        // todo: should throw if handler doesn't have path id:
        // @HttpController('/test1')
        // class TestController1 {
        //     @Get('')
        //     getTest1(): string {
        //         return 'test 1';
        //     }
        // }
    });

    describe('csrf', () => {
        // todo ilyakortasov:
    });

    describe('handler invoke parameters', () => {
        it.skip('should pass request context to handlers for every request', () => {});

        it.skip('should pass logger from setupRequestLogger to handlers for every request', () => {});

        it.skip('should pass cookie data to handlers for every request', () => {});

        it.skip('should correctly parse json request body and pass it to handlers for every request', () => {});
    });

    describe('request id', () => {
        it.skip('should forward request id if X-Request-Id header exists', () => {});

        it.skip("should generate request id if X-Request-Id header doesn't exist", () => {});

        it.skip('should pass request id to handlers for every request', () => {});

        it.skip('should log each request id', () => {});
    });

    describe('ping', () => {
        it.skip('should send server status in response to ping request', () => {});

        it.skip('should stop answering ping requests once the server is stopped', () => {});
    });
});
