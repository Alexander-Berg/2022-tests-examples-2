const {ATTRIBUTES, getUserinfo} = require('./api/blackbox/userinfo');

const DEFAULT_PASSWORD = 'simple123456';
const DEFAULT_FIRSTNAME = 'Default-Имя';
const DEFAULT_LASTNAME = 'Default Фамилия';

class User {
    constructor({
        type,
        uid,
        login,
        password,
        firstname = DEFAULT_FIRSTNAME,
        lastname = DEFAULT_LASTNAME,
        phones,
        emails
    } = {}) {
        this.accountTypeValue = type;
        this.uidValue = uid;
        this.loginValue = login;
        this.passwordValue = password;
        this.firstnameValue = firstname;
        this.lastnameValue = lastname;
        this.phonesValue = phones;
        this.emailsValue = emails;
    }

    async fetchUserinfo() {
        const userinfo = await getUserinfo(this);
        const toUpdateData = {
            uid: userinfo.id,
            login: userinfo.login,
            hasPassword: userinfo.hasPassword,
            firstname: userinfo.attributes[ATTRIBUTES.FIRSTNAME],
            lastname: userinfo.attributes[ATTRIBUTES.LASTNAME],
            aliases: userinfo.aliases,
            attributes: userinfo.attributes,
            userinfo: userinfo
        };

        this.update(toUpdateData);
        return this;
    }

    update({type, uid, login, hasPassword, firstname, lastname, aliases, attributes, userinfo} = {}) {
        if (type) {
            this.accountTypeValue = type;
        }
        if (uid) {
            this.uidValue = uid;
        }
        if (login) {
            this.loginValue = login;
        }
        if (hasPassword !== null) {
            this.hasPasswordValue = hasPassword;
        }
        if (firstname) {
            this.firstnameValue = firstname;
        }
        if (lastname) {
            this.lastnameValue = lastname;
        }
        if (aliases) {
            this.aliasesValue = aliases;
        }
        if (attributes) {
            this.attributesValue = attributes;
        }
        if (userinfo) {
            this.userinfoValue = userinfo;
        }
        return this;
    }

    set accountType(type) {
        this.type = type;
    }

    get accountType() {
        return this.type;
    }

    set uid(uid) {
        this.uidValue = uid;
    }

    get uid() {
        return this.uidValue;
    }

    set login(login) {
        this.loginValue = login;
    }

    get login() {
        return this.loginValue;
    }

    set password(password) {
        this.passwordValue = password;
    }

    get password() {
        return this.passwordValue;
    }

    set firstname(firstname) {
        this.firstnameValue = firstname;
    }

    get firstname() {
        return this.firstnameValue;
    }

    set lastname(lastname) {
        this.lastnameValue = lastname;
    }

    get lastname() {
        return this.lastnameValue;
    }

    set controlQuestion(question) {
        this.controlQuestionValue = question;
    }

    get controlQuestion() {
        return this.controlQuestionValue;
    }

    set controlAnswer(answer) {
        this.controlAnswerValue = answer;
    }

    get controlAnswer() {
        return this.controlAnswerValue;
    }

    setSecurePhone(phone) {
        if (this.phonesValue) {
            this.phonesValue.secure = phone;
        }
        this.phonesValue = {secure: phone};
    }

    get phones() {
        return this.phonesValue;
    }
}

function userWithLoginPassword(login, password) {
    return new User({login: login, password: password});
}

function userWithLogin(login) {
    return userWithLoginPassword(login, DEFAULT_PASSWORD);
}

function userWithUid(uid) {
    return new User({uid: uid, password: null});
}

module.exports = {
    userWithLoginPassword,
    userWithLogin,
    userWithUid,
    User
};
