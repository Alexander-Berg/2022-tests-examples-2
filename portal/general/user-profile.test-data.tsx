import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';

import { UserProfile__page } from '@block/user-profile/user-profile.view';

import logoutData from './mocks/logout.json';
import loginData from './mocks/login.json';
import usersData from './mocks/users.json';
import footerData from './mocks/footer.json';
import notificationsData from './mocks/notifications.json';
import notifierData from './mocks/notifier.json';
import messengerData from './mocks/messenger.json';

const render = (data: Partial<Req3Server>) => {
    return execView(UserProfile__page, {}, mockReq({}, data));
};

export function logout() {
    return render(logoutData as Partial<Req3Server>);
}

export function login() {
    return render(loginData as Partial<Req3Server>);
}

export function users() {
    return render(usersData);
}

export function footer() {
    return render(footerData);
}

export function notifications() {
    return render(notificationsData as Partial<Req3Server>);
}

export function messenger() {
    return render(messengerData as Partial<Req3Server>);
}

export function notifier() {
    return render(notifierData as Partial<Req3Server>);
}
