const El = require('@yandex-int/bem-page-object').Entity;

const PageObjects = {};

PageObjects.layout = new El('[data-t="family:layout"]');
PageObjects.layout.main = new El('[data-t="family:layout:main"]');
PageObjects.layout.invite = new El('[data-t="family:action:layout:invite"]');
PageObjects.layout.redesignInvite = new El('[data-t="family:action:layout:redesign-invite"]');
PageObjects.layout.error = new El('[data-t="family:action:layout:error"]');
PageObjects.layout.limits = new El('[data-t="family:layout:limits"]');

PageObjects.modal = new El('[data-t="modal:family:popup"]');
PageObjects.modalLayout = new El('[data-t="modal:family:popup"] [data-t="family:layout"]');

PageObjects.memberSlots = new El('');
PageObjects.memberSlots.admin = new El(`[data-t="family:slot:user:member:0"]`);
PageObjects.memberSlots.users = new El(`[data-t^="family:slot:user:member"]`);
PageObjects.memberSlots.invites = new El(`[data-t^="family:slot:invite:member"]`);
PageObjects.memberSlots.empty = new El(`[data-t^="family:slot:empty:member"]`);

PageObjects.kiddishSlots = new El('[data-t="family:slots-group:kiddish"]');
PageObjects.kiddishSlots.kiddish = new El(`[data-t^="family:slot:kiddish:kiddish"]`);
PageObjects.kiddishSlots.empty = new El(`[data-t^="family:slot:empty:kiddish"]`);

PageObjects.payLimits = new El('[data-t="family:pay-limits"]');

module.exports = PageObjects;
