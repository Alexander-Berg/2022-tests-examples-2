export interface PatchStyles {
    enableNotifications?: true;
    showCopyButtons?: true;
    showAntPickerClear?: true;
    showOptions?: true;
}

export function patchStyles(params: PatchStyles) {
    const {
        enableNotifications = false,
        showCopyButtons = false,
        showAntPickerClear = false,
        showOptions = false
    } = params;

    const disableAnimationStyles = `
        * {
            -o-transition-property: none !important;
            -moz-transition-property: none !important;
            -ms-transition-property: none !important;
            -webkit-transition-property: none !important;
            transition-property: none !important;

            -o-animation-duration: 0s !important;
            -moz-animation-duration: 0s !important;
            -ms-animation-duration: 0s !important;
            -webkit-animation-duration: 0s !important;
            animation-duration: 0s !important;
        }
    `;
    const staticHeaderStyles = `
        [data-testid="header"] {
            position: static !important;
        }
    `;
    const menuWithoutShadowsStyles = `
        [data-testid="more-menu"] {
            box-shadow: none !important;
        }
    `;
    const disableScrollBarsStyles = `
        *::-webkit-scrollbar {
            display: none !important;
        }
    `;
    const disableNotificationsStyles = `
        .ant-notification {
            display: none !important;
        }
    `;
    const showCopyButtonsStyles = `
        .pigeon-copy-button {
            visibility: visible !important;
            opacity: 1 !important;
        }
    `;

    const showAntPickerClearStyles = `
        .ant-picker-clear {
            opacity: 1 !important;
        }
    `;

    const showOptionsStyles = `
        .pigeon-options {
            display: flex;
        }
    `;

    const css = [
        disableAnimationStyles,
        staticHeaderStyles,
        menuWithoutShadowsStyles,
        disableScrollBarsStyles,
        enableNotifications ? undefined : disableNotificationsStyles,
        showCopyButtons ? showCopyButtonsStyles : undefined,
        showAntPickerClear ? showAntPickerClearStyles : undefined,
        showOptions ? showOptionsStyles : undefined
    ].join('');

    const style = document.createElement('style');
    style.innerHTML = css;
    document.head.appendChild(style);
}
