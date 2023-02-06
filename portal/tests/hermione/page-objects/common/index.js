const El = require('../Entity');
const NotifWrap = require('./NotifWrap');
const elems = {};
elems.NotifWrap = NotifWrap;

elems.Application = new El({ block: 'Application' });
elems.Header = new El({ block: 'Header' });

elems.Button = new El({ block: 'Button2' });

elems.Menu = new El({ block: 'Menu' });
elems.MenuItem = new El({ block: 'Menu-Item' });

elems.Popup = new El({ block: 'Popup2' });
elems.Popup.Menu = elems.Menu.copy();
elems.Popup.MenuItem = elems.MenuItem.copy();
elems.Popup.firstMenuItem = elems.MenuItem.firstChild();
elems.Popup.lastMenuItem = elems.MenuItem.lastChild();

elems.More = new El({ block: 'More' });
elems.More_disabled = elems.More.mix(elems.Select_disabled);
elems.More.Popup = elems.Popup.copy();

elems.Select = new El({ block: 'Select' });
elems.Select_disabled = elems.Select.mods({ disabled: true });

elems.Header.More = elems.More.copy();
elems.Header.More_disabled = elems.Header.More.mix(elems.Select_disabled);

elems.Notifications = new El({ block: 'Notifications' });
elems.Notifications.TabsMenuTab = new El({ block: 'TabsMenu-Tab' });
elems.Notifications.importantTab = elems.Notifications.TabsMenuTab.firstChild();
elems.Notifications.servicesTab = elems.Notifications.TabsMenuTab.lastChild();

elems.NotificationsListItem = new El({ block: 'NotificationsList-Item' });
elems.NotificationsListItem.More = new El({ block: 'Notification-More' });

elems.NotificationsListItem_unread = elems.NotificationsListItem.mods({ unread: true });

elems.NotificationTitle = new El({ block: 'Notification-Title' });

elems.DateTime = new El({ block: 'DateTime' });

elems.NotificationPile = new El({ block: 'NotificationPile' });
elems.NotificationPile.NotifWrap = elems.NotifWrap.copy();
elems.NotificationPile.Trigger = new El({ block: 'NotificationPile-Trigger' });
elems.NotificationPile.ShowMore = new El({ block: 'NotificationPile-ShowMore' });
elems.NotificationPile.deletePile;
NotifControl = new El({ block: 'NotifControl' });
NotifControl.Button = new El({ block: 'NotifControl-button' });
elems.NotificationPile.Header = new El({ block: 'NotificationPile-Header' });
elems.NotificationPile.HeaderCounter = new El({ block: 'NotificationPile-Header-Counter' });
elems.NotificationPile.Header.ButtonCollapse = NotifControl.Button.mods({ collapse: true });
elems.NotificationPile.Header.ButtonReadAll = NotifControl.Button.mods({ 'read-all': true });
elems.NotificationPile.Header.ButtonDeleteAll = NotifControl.Button.mods({ 'delete-all': true });
elems.NotificationPile.readAll;
elems.NotificationPile.forServiceID = serviceID => elems.NotificationPile.mods({ [`service_${serviceID}`]: true });
elems.NotificationPile.NotificaitonZero = new El({ block: 'NotificationZero' });
elems.NotificationPile.NotificaitonZero.readAll;
elems.NotificationPile.NotificaitonZero.deleteAll;
// data-test-id="portal"
// Section Settings-Service
elems.Settings = {};
elems.Settings.SectionService = new El({ block: 'Section' });
elems.Settings.SectionService.SectionControlls = new El({ block: 'Section-Controls' });
elems.Settings.ForServiceID = serviceID => elems.Settings.SectionService.mods({ [`service_${serviceID}`]: true });
elems.Settings.ButtonClose = new El({ block: 'Header-Button' });
module.exports = elems;
