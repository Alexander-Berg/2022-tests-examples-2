describe('Captcha', function() {
    beforeEach(function() {
        this.originalSoundManager = passport.soundManager;

        passport.soundManager = {
            setup: sinon.spy(),
            createSound: sinon.stub().returns({
                duration: 100,
                id: 'someMusic',
                url: 'http://wherever.com/whatever.mp3'
            })
        };

        this.captcha = passport.block('captcha');
        this.captcha.init();
    });

    afterEach(function() {
        passport.soundManager = this.originalSoundManager;
    });

    it('is a control', function() {
        expect(this.captcha).to.be.an('object');
        expect(this.captcha.isControl).to.be(true);
    });

    describe('Initialization', function() {
        it('should start in audioMode if launched over audio layout', function() {
            sinon.stub(this.captcha, '$').returns($('<input value="audio" />'));
            sinon.spy(this.captcha, 'switchMode');
            this.captcha.init();
            expect(this.captcha.switchMode.calledWithExactly(null, true)).to.be(true);
            this.captcha.switchMode.restore();
            this.captcha.$.restore();
        });
    });

    describe('Modes', function() {
        beforeEach(function() {
            this.data = {};
            sinon.stub(passport.api, 'request').returns({done: sinon.stub().callsArgWith(0, this.data)});
        });
        afterEach(function() {
            passport.api.request.restore();
        });

        describe('Switching', function() {
            it('should swith from audio to text modes', function() {
                expect(this.captcha.mode).to.be('text');
                this.captcha.switchMode();
                expect(this.captcha.mode).to.be('audio');
                this.captcha.switchMode();
                expect(this.captcha.mode).to.be('text');
            });

            it('should stop playing sounds when switching from audio to text', function() {
                this.captcha.switchMode();

                sinon.spy(this.captcha, 'stop');
                this.captcha.switchMode();

                expect(this.captcha.stop.calledOnce).to.be(true);
                this.captcha.stop.restore();
            });

            it('should init sound on switch to audio mode if not already initialized', function() {
                expect(this.captcha.mode).to.be('text');

                this.captcha.soundInitialized = false;
                sinon.spy(this.captcha, 'initSound');

                this.captcha.switchMode();
                expect(this.captcha.initSound.called).to.be(true);
                this.captcha.initSound.restore();
            });

            it('should play intro and captcha on switch to audio mode if sound already initialized', function() {
                expect(this.captcha.mode).to.be('text');

                this.captcha.soundInitialized = true;
                this.captcha.audioIntro = {};
                this.captcha.audioCaptcha = {};

                var sound = {
                    isLoaded: new $.Deferred(),
                    play: sinon.spy()
                };

                sound.isLoaded.resolve();
                sinon.stub(this.captcha, 'loadAudio').returns(sound);

                var originalPlay = this.captcha.play;

                this.captcha.play = sinon.spy();

                this.captcha.switchMode();

                expect(this.captcha.play.callCount).to.be(1);
                expect(this.captcha.play.calledWithExactly(sound, sinon.match.func));
                this.captcha.play.firstCall.args[1]();

                expect(this.captcha.play.callCount).to.be(2);
                expect(this.captcha.play.calledWithExactly(sound));

                this.captcha.play = originalPlay;
                this.captcha.loadAudio.restore();
            });

            it('should not play anything if switching with suppressAutoPlay flag', function() {
                expect(this.captcha.mode).to.be('text');

                sinon.spy(this.captcha, 'play');

                //Switch to audio without autoPlay
                this.captcha.switchMode(null, true);

                expect(this.captcha.play.callCount).to.be(0);
                this.captcha.play.restore();
            });

            it('triggers switch_mode event on captcha, when switching', function() {
                expect(this.captcha.mode).to.be('text');

                var originalEmit = this.captcha.emit;

                this.captcha.emit = sinon.spy();

                this.captcha.switchMode();
                expect(this.captcha.emit.calledOnce).to.be(true);
                expect(this.captcha.emit.calledWithExactly('switch_mode', 'audio')).to.be(true);

                this.captcha.switchMode();
                expect(this.captcha.emit.calledTwice).to.be(true);
                expect(this.captcha.emit.calledWithExactly('switch_mode', 'text')).to.be(true);

                this.captcha.emit = originalEmit;
            });
        });

        describe('Audio', function() {
            it('should already initialized sound when entering audio mode', function() {
                this.captcha.switchMode(); //Switch to audio
                expect(this.captcha.soundInitialized).to.be(true);
            });

            describe('initSound', function() {
                it('should start SoundManager', function() {
                    this.captcha.initSound();
                    expect(passport.soundManager.setup.calledOnce).to.be(true);
                });

                it('should call for a new captcha when SoundManager is set up', function() {
                    this.captcha.initSound();

                    expect(passport.soundManager.setup.firstCall.args[0]).to.have.property('onready');

                    // Make sure getNewCode gets called with onready callback
                    sinon
                        .mock(this.captcha, 'getNewCode')
                        .expects('getNewCode')
                        .once();
                    passport.soundManager.setup.firstCall.args[0].onready();
                    this.captcha.getNewCode.restore();
                });

                it('should announce a fail, if loading sound system fails', function() {
                    this.captcha.initSound();

                    expect(passport.soundManager.setup.firstCall.args[0]).to.have.property('ontimeout');

                    // Make sure getNewCode gets called with onready callback
                    sinon
                        .mock(this.captcha, 'audioFailed')
                        .expects('audioFailed')
                        .once();
                    passport.soundManager.setup.firstCall.args[0].onready();
                    this.captcha.audioFailed.restore();
                });

                it('should switch the button state to "loading", when sound is being first initialized', function() {
                    sinon.spy(this.captcha, 'switchButtonMode');
                    this.captcha.soundInitialized = false;
                    this.captcha.initSound();
                    expect(this.captcha.switchButtonMode.calledOnce).to.be(true);
                    expect(this.captcha.switchButtonMode.calledWithExactly('loading'));

                    this.captcha.initSound();
                    expect(this.captcha.switchButtonMode.calledOnce).to.be(true); //Same count, no change
                    this.captcha.switchButtonMode.restore();
                });
            });

            describe('Loading audio', function() {
                it('should load audio by its url', function() {
                    this.captcha.loadAudio('http://someUrl');

                    expect(passport.soundManager.createSound.calledOnce).to.be(true);

                    var firstCallFirstArg = passport.soundManager.createSound.firstCall.args[0];

                    expect(firstCallFirstArg).to.have.property('url', 'http://someUrl');
                    expect(firstCallFirstArg).to.have.property('autoLoad', true);
                    expect(firstCallFirstArg).to.have.property('autoPlay', false);
                    expect(firstCallFirstArg).to.have.property('type', 'audio/mp3');
                });

                it('should attach a deferred to the audio indicating whether the audio has loaded', function() {
                    var returnedAudio = {name: 'someAudio'};

                    passport.soundManager.createSound = sinon.stub().returns(returnedAudio);

                    var actualAudio = this.captcha.loadAudio('http://wherever.com');

                    //Hack to check if isLoaded is a deferred, following doesn't work:
                    //expect(actualAudio.isLoaded).to.be.a($.Deferred);
                    expect(actualAudio.isLoaded.reject).to.be.a('function');
                    expect(actualAudio.isLoaded.resolve).to.be.a('function');

                    returnedAudio.isLoaded = actualAudio.isLoaded; //Apart from that objects should be equal
                    expect(actualAudio).to.eql(returnedAudio);
                });

                it('should trigger audioFailed if file fails to load', function() {
                    var audio = this.captcha.loadAudio('someUrl');

                    sinon.stub(this.captcha, 'audioFailed');

                    audio.isLoaded.reject();
                    expect(this.captcha.audioFailed.calledOnce).to.be(true);
                    this.captcha.audioFailed.restore();
                });
            });

            describe('Playing', function() {
                beforeEach(function() {
                    this.audio = {
                        play: sinon.spy(),
                        stop: sinon.spy(),
                        isLoaded: new $.Deferred(),
                        onfinish: null
                    };
                    this.audio.isLoaded.resolve();
                    this.captcha.soundInitialized = true;
                });

                it("should play file once it's loaded", function() {
                    this.audio.isLoaded = new $.Deferred();

                    this.captcha.play(this.audio);
                    expect(this.audio.play.called).to.be(false);

                    this.audio.isLoaded.resolve();
                    expect(this.audio.play.calledOnce).to.be(true);
                });

                it('should trigger the callback, if given, when done playing', function() {
                    var callback = sinon.spy();

                    this.captcha.play(this.audio, callback);

                    var firstCallArg = this.audio.play.firstCall.args[0];

                    expect(firstCallArg).to.have.property('onfinish');

                    expect(callback.calledOnce).to.not.be(true);
                    firstCallArg.onfinish();
                    expect(callback.calledOnce).to.be(true);
                });

                it('should switch the button state to "playing" once started playing', function() {
                    sinon.spy(this.captcha, 'switchButtonMode');
                    this.captcha.play(this.audio);

                    expect(this.captcha.switchButtonMode.calledWith('playing')).to.be(true);
                    this.captcha.switchButtonMode.restore();
                });

                it('should switch the button state to "play" when done playing', function() {
                    sinon.spy(this.captcha, 'switchButtonMode');
                    this.captcha.play(this.audio);

                    var firstCallArg = this.audio.play.firstCall.args[0];

                    firstCallArg.onfinish();

                    expect(this.captcha.switchButtonMode.calledWith('play')).to.be(true);
                    this.captcha.switchButtonMode.restore();
                });

                it('should stop any sound before playing', function() {
                    sinon.spy(this.captcha, 'stop');
                    this.captcha.play(this.audio);
                    expect(this.captcha.stop.calledBefore(this.audio.play)).to.be(true);
                    this.captcha.stop.restore();
                });
            });

            describe('Stopping', function() {
                beforeEach(function() {
                    this.captcha.audioIntro = {
                        stop: sinon.spy(),
                        isLoaded: new $.Deferred()
                    };
                    this.captcha.audioCaptcha = {
                        stop: sinon.spy(),
                        isLoaded: new $.Deferred()
                    };

                    this.captcha.audioIntro.isLoaded.resolve();
                    this.captcha.audioCaptcha.isLoaded.resolve();
                });

                it('should stop audioCaptcha', function() {
                    this.captcha.stop();
                    expect(this.captcha.audioCaptcha.stop.calledOnce).to.be(true);
                });

                it('should stop intro', function() {
                    this.captcha.stop();
                    expect(this.captcha.audioIntro.stop.calledOnce).to.be(true);
                });

                it('should only stop if sound is loaded', function() {
                    //Reset deferred for intro
                    this.captcha.audioIntro.isLoaded = new $.Deferred();

                    this.captcha.stop();
                    expect(this.captcha.audioIntro.stop.called).to.not.be(true);
                    expect(this.captcha.audioCaptcha.stop.called).to.be(true);
                });

                it('should switch the button mode to "play"', function() {
                    sinon.spy(this.captcha, 'switchButtonMode');
                    this.captcha.stop();
                    expect(this.captcha.switchButtonMode.calledOnce).to.be(true);
                    expect(this.captcha.switchButtonMode.calledWithExactly('play')).to.be(true);
                    this.captcha.switchButtonMode.restore();
                });
            });

            describe('Getting new captcha code', function() {
                beforeEach(function() {
                    this.captcha.switchMode(); //Switch to audio

                    this.responseData = {
                        image_url: 'whatever',
                        key: 'whatsoever',
                        voice: {
                            intro_url: 'audioIntroUrl',
                            url: 'audioCaptchaUrl'
                        }
                    };

                    this.requestDoneCallbacks = sinon.spy();
                    passport.api.request.returns({done: this.requestDoneCallbacks});
                });

                it('should stop whatever is currently playing', function() {
                    sinon.spy(this.captcha, 'stop');
                    this.captcha.getNewAudioCode();

                    expect(this.captcha.stop.calledOnce).to.be(true);
                    this.captcha.stop.restore();
                });

                it('should fetch new captcha with audio', function() {
                    this.captcha.getNewAudioCode();
                    expect(passport.api.request.calledOnce).to.be(true);
                    expect(passport.api.request.calledWith('audiocaptcha')).to.be(true);
                });

                it('should fetch audiocaptcha without cache', function() {
                    this.captcha.getNewAudioCode();
                    expect(passport.api.request.firstCall.args[2]).to.have.property('cache', false);
                });

                it('should load returned audio captcha url', function() {
                    this.captcha.audioIntro = {
                        url: 'audioIntroUrl'
                    };
                    this.captcha.getNewAudioCode();

                    sinon
                        .mock(this.captcha, 'loadAudio')
                        .expects('loadAudio')
                        .withExactArgs('audioCaptchaUrl')
                        .twice()
                        .returns({play: function() {}});

                    //Executing first passed callback
                    this.requestDoneCallbacks.firstCall.args[0](this.responseData);
                    //Check re-executing reloads the this.captcha
                    this.requestDoneCallbacks.firstCall.args[0](this.responseData);

                    this.captcha.loadAudio.restore();
                });

                it('should only load intro if its url had changed from last time', function() {
                    sinon
                        .mock(this.captcha, 'loadAudio')
                        .expects('loadAudio')
                        .withExactArgs(sinon.match('audioCaptchaUrl').or(sinon.match('audioIntroUrl')))
                        .thrice()
                        .returns({url: 'audioIntroUrl', isLoaded: new $.Deferred()});

                    this.captcha.getNewCode();

                    //Executing first passed callback twice
                    this.requestDoneCallbacks.firstCall.args[0](this.responseData);
                    this.requestDoneCallbacks.firstCall.args[0](this.responseData);

                    this.captcha.loadAudio.restore();
                });

                it('should play intro and then plays captcha if intro was changed', function() {
                    var sound = {
                        isLoaded: new $.Deferred(),
                        play: sinon.spy(),
                        stop: sinon.spy()
                    };

                    sound.isLoaded.resolve();

                    sinon.stub(this.captcha, 'loadAudio').returns(sound);
                    sinon.spy(this.captcha, 'play');

                    this.captcha.getNewAudioCode();
                    this.requestDoneCallbacks.firstCall.args[0](this.responseData);

                    expect(this.captcha.play.callCount).to.be(1);
                    expect(this.captcha.play.calledWithExactly(sound, sinon.match.func));
                    this.captcha.play.firstCall.args[1]();

                    expect(this.captcha.play.callCount).to.be(2);
                    expect(this.captcha.play.calledWithExactly(sound));
                    this.captcha.play.restore();
                    this.captcha.loadAudio.restore();
                });

                it('should play captcha without intro if intro has not changed', function() {
                    var sound = {
                        isLoaded: new $.Deferred(),
                        play: sinon.spy(),
                        stop: sinon.spy()
                    };

                    sound.isLoaded.resolve();

                    this.captcha.audioIntro = {
                        url: this.responseData.voice.intro_url
                    };

                    sinon.stub(this.captcha, 'loadAudio').returns(sound);
                    sinon.spy(this.captcha, 'play');

                    this.captcha.getNewAudioCode();
                    this.requestDoneCallbacks.firstCall.args[0](this.responseData);

                    expect(this.captcha.play.callCount).to.be(1);
                    expect(this.captcha.play.calledWithExactly(sound));
                    this.captcha.play.restore();
                    this.captcha.loadAudio.restore();
                });

                it('should switch the button state to "loading"', function() {
                    expect(this.captcha.mode).to.be('audio');

                    sinon.spy(this.captcha, 'switchButtonMode');
                    this.captcha.getNewAudioCode();
                    expect(this.captcha.switchButtonMode.firstCall.calledWithExactly('loading')).to.be(true);
                    this.captcha.switchButtonMode.restore();
                });
            });
        });
        describe('Text', function() {
            describe('Getting new captcha code', function() {
                it('should fetch new captcha without audio', function() {
                    this.captcha.getNewCode();
                    expect(passport.api.request.calledOnce).to.be(true);
                    expect(passport.api.request.calledWith('textcaptcha')).to.be(true);
                });

                it('should fetch new captcha without caching', function() {
                    this.captcha.getNewCode();
                    expect(passport.api.request.firstCall.args[2]).to.have.property('cache', false);
                });
            });
        });
        describe('Getting new captcha code in general', function() {
            beforeEach(function() {
                this.captcha.switchMode(); //Switch to audio

                this.responseData = {
                    image_url: 'imageUrl',
                    key: 'newKey',
                    voice: {
                        intro_url: 'audioIntroUrl',
                        url: 'audioCaptchaUrl'
                    }
                };

                this.requestDoneCallbacks = sinon.stub().callsArgWith(0, this.responseData);
                passport.api.request.returns({done: this.requestDoneCallbacks});
            });

            it('should update the image', function() {
                sinon.spy(this.captcha, 'setImage');
                this.captcha.getNewCode();

                expect(this.captcha.setImage.calledOnce).to.be(true);
                expect(this.captcha.setImage.calledWithExactly('imageUrl')).to.be(true);
                this.captcha.setImage.restore();
            });

            it('should update the captcha key field', function() {
                sinon.spy(this.captcha, 'setKey');
                this.captcha.getNewCode();

                expect(this.captcha.setKey.calledOnce).to.be(true);
                expect(this.captcha.setKey.calledWithExactly('newKey')).to.be(true);
                this.captcha.setKey.restore();
            });

            it('should request new captcha on switch to audio if text-only code was requested before', function() {
                sinon.stub(this.captcha, 'loadAudio').returns({
                    play: sinon.spy(),
                    url: this.responseData.voice.intro_url //Needed so that intro isn't reloaded
                });
                sinon.spy(this.captcha, 'play');
                expect(this.captcha.mode).to.be('audio');

                //Load first captcha
                this.captcha.getNewCode();
                this.requestDoneCallbacks.lastCall.args[0](this.responseData);

                //Switch to test
                this.captcha.switchMode();

                //Request new text-only code, which should invalidate an old one
                this.responseData.voice = {
                    intro_url: 'anotherIntroUrl',
                    url: 'anotherAudioCaptchaUrl'
                };
                this.captcha.getNewCode();
                this.requestDoneCallbacks.lastCall.args[0](this.responseData);
                expect(this.captcha.keyChanged).to.be(true);

                //Switching to audio should reload captcha now
                this.responseData.voice = {
                    intro_url: 'audioIntroUrl',
                    url: 'newAudioCaptchaUrl'
                };
                this.captcha.switchMode();
                this.requestDoneCallbacks.lastCall.args[0](this.responseData);

                expect(this.captcha.loadAudio.lastCall.args[0]).to.be('newAudioCaptchaUrl');
                this.captcha.play.restore();
                this.captcha.loadAudio.restore();
            });
        });
    });
});
