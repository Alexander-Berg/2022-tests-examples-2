const El = require('../Entity');

NotifWrap = new El({ block: 'NotifWrap' });
//touch NotifWrap-Button_action_delete-all
NotifWrap.TouchButton = new El({ block: 'NotifWrap-Button' });
NotifWrap.TouchButtonRead = NotifWrap.TouchButton.mods({ read: true });
NotifWrap.TouchButtonReadAll = NotifWrap.TouchButton.mods({ 'read-all': true });
NotifWrap.TouchButtonDelete = NotifWrap.TouchButton.mods({ delete: true });
NotifWrap.TouchButtonDeleteAll = NotifWrap.TouchButton.mods({ 'delete-all': true });
//desktop NotifControl-button_delete
NotifControl = new El({ block: 'NotifControl' });
NotifControl.Button = new El({ block: 'NotifControl-button' });
NotifWrap.DesktopButton = NotifControl.Button;
NotifWrap.DesktopButtonRead = NotifControl.Button.mods({ read: true });
NotifWrap.DesktopButtonReadAll = NotifControl.Button.mods({ 'read-all': true });
NotifWrap.DesktopButtonDelete = NotifControl.Button.mods({ delete: true });
NotifWrap.DesktopButtonDeleteAll = NotifControl.Button.mods({ 'delete-all': true });

NotifWrap.Slider = new El({ block: 'NotifWrap-Slider' });
NotifWrap.Notification = new El({ block: 'Notification' });
NotifWrap.forId = id => NotifWrap.mods({ [`id_${id}`]: true });
module.exports = NotifWrap;

//.NotifWrap.NotifWrap_id_rcnt0 .NotifControl-Button .NotifControl-Button.NotifControl-Button_delete
