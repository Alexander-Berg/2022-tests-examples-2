import { JSDOMWrapper } from '@src/__tests__/utils/jsdom';
import chai from 'chai';
import {
    isForceRecordingEnabled,
    isIgnored,
    isValidInput,
    isPrivateInformationField,
    isObfuscationNeeded,
} from '../inputUtils';

describe('webvisor / input utils', () => {
    const { window } = new JSDOMWrapper();
    const { document } = window;
    const validInput = document.createElement('input');
    validInput.setAttribute('type', 'text');

    it('checks validity of inputs', () => {
        chai.assert(isValidInput(validInput), 'text input valid');

        const invalidInput = {
            nodeName: 'INPUT',
            type: 'some-gay-input-type',
        } as any;
        chai.assert(!isValidInput(invalidInput), 'wrong type input invalid');

        const textarea = document.createElement('textarea');
        chai.assert(isValidInput(textarea), 'textarea valid');
    });

    it('checks if input is ignored', () => {
        const passwordInput = document.createElement('input');
        passwordInput.setAttribute('type', 'password');
        chai.assert(isIgnored(window, passwordInput), 'password is ignored');

        const invalidInput = document.createElement('input');
        invalidInput.setAttribute('class', 'ym-disable-keys');
        chai.assert(isIgnored(window, invalidInput), 'yandex class is ignored');

        chai.assert(
            !isIgnored(window, validInput),
            "plain input isn't ignored",
        );
    });

    it('checks is force recording enabled', () => {
        const forceRecordingInput = document.createElement('input');
        forceRecordingInput.setAttribute('class', 'ym-record-keys');
        chai.assert(
            isForceRecordingEnabled(forceRecordingInput),
            'force record class is enabled',
        );

        chai.assert(
            !isForceRecordingEnabled(validInput),
            'plain input is not force recorded',
        );
    });

    it('checks if input is private information input', () => {
        const somePrivateField = document.createElement('input');
        somePrivateField.setAttribute('class', 'credit-card');
        chai.assert(
            isPrivateInformationField(somePrivateField),
            'credit card is private',
        );

        const emailField = document.createElement('input');
        emailField.setAttribute('type', 'email');
        chai.assert(isPrivateInformationField(emailField), 'email is private');

        const telField = document.createElement('input');
        telField.setAttribute('type', 'tel');
        chai.assert(isPrivateInformationField(telField), 'tel is private');

        const anotherPrivateField = document.createElement('input');
        anotherPrivateField.setAttribute('id', 'phoneNumber');
        chai.assert(
            isPrivateInformationField(anotherPrivateField),
            'phone number is private',
        );

        const andAnotherPrivateField = document.createElement('input');
        andAnotherPrivateField.setAttribute('placeholder', 'фамилия');
        chai.assert(
            isPrivateInformationField(anotherPrivateField),
            'surname is private',
        );

        chai.assert(!isPrivateInformationField(validInput));
    });

    it('checks if obfuscation is needed', () => {
        const somePrivateField = document.createElement('input');
        somePrivateField.setAttribute('class', 'credit-card');

        chai.expect(
            isObfuscationNeeded(window, somePrivateField, true),
            'obfuscate eu private fields',
        ).deep.equal({
            obfuscationNeeded: true,
            isPrivate: true,
            forceRecord: false,
        });
        chai.expect(
            isObfuscationNeeded(window, somePrivateField, false),
            "don't obfuscate non eu private fields",
        ).deep.equal({
            obfuscationNeeded: false,
            isPrivate: true,
            forceRecord: false,
        });
        somePrivateField.setAttribute('type', 'button');
        chai.expect(
            isObfuscationNeeded(window, somePrivateField, true),
            "don't obfuscate button",
        ).to.deep.equal({
            obfuscationNeeded: false,
            isPrivate: false,
            forceRecord: false,
        });

        chai.expect(
            isObfuscationNeeded(window, validInput, true),
            "don't obfuscate non eu plain input",
        ).to.deep.equal({
            obfuscationNeeded: false,
            isPrivate: false,
            forceRecord: false,
        });
        chai.expect(
            isObfuscationNeeded(window, validInput, false),
            "don't obfuscate eu plain input",
        ).to.deep.equal({
            obfuscationNeeded: false,
            isPrivate: false,
            forceRecord: false,
        });

        const forceRecordingInput = document.createElement('input');
        forceRecordingInput.setAttribute('class', 'credit-card ym-record-keys');
        chai.expect(
            isObfuscationNeeded(window, forceRecordingInput, true),
            'force record disables eu obfuscation',
        ).to.deep.equal({
            obfuscationNeeded: false,
            isPrivate: true,
            forceRecord: true,
        });
        chai.expect(
            isObfuscationNeeded(window, forceRecordingInput, false),
            'force record disables non eu obfuscation',
        ).to.deep.equal({
            obfuscationNeeded: false,
            isPrivate: true,
            forceRecord: true,
        });
    });
});
