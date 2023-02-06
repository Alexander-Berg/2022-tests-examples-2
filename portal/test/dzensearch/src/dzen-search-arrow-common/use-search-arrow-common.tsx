/* eslint-disable */

import {useCallback, useRef, useState} from 'react';
import {useEffectOnce} from 'react-use';
import { throttle } from '../utils/throttle';

const SCROLL_THROTTLE = 100;

export enum Platform {
    desktop = 'desktop',
    mobile = 'mobile',
}

type Props = {
    platform: Platform;
    block: string;
    iframeTimeout: number;
    autoscroll: boolean;
};

const log = (block: string, message: string) => {
    try {
        console.log('rum log', {
            level: 'info',
            message,
            block,
        });
        /*Ya.Rum.logError({
            level: 'info',
            message,
            block,
        });*/
    } catch (e) {
        // Нет Ya.Rum?
    }
};

const showSuggest = () => {
    document.body.classList.add('body_search_yes');
    setTimeout(() => {
        window.scrollTo(window.pageXOffset, 0);
    }, 100);
};

const hideSuggest = () => {
    document.body.classList.remove('body_search_yes');
    setTimeout(() => {
        window.scrollTo(window.pageXOffset, 0);
    }, 100);
};

export const useSearchArrowCommon = (props: Props) => {
    const frameRef = useRef<HTMLIFrameElement>(null);
    const loadTimeoutRef = useRef<ReturnType<typeof setTimeout>>();
    const [frameHeight, setFrameHeight] = useState<number>();
    const [hasValue, setHasValue] = useState<boolean>(false);
    const [hasFocus, setHasFocus] = useState<boolean>(false);
    const hasFocusRef = useRef(hasFocus);
    const [hasFrameError, setFrameError] = useState<boolean>(false);
    const [isFrameLoaded, setFrameLoaded] = useState<boolean>(false);

    const sendMessage = useCallback((msg: any) => {
        if (frameRef.current) {
            try {
                frameRef.current.contentWindow?.postMessage(msg, '*');
            } catch (err) {
                // cross-domain issues
            }
        }
    }, []);

    useEffectOnce(() => {
        const onMessage = (event: MessageEvent) => {
            if (!frameRef.current || event.source !== frameRef.current.contentWindow) {
                return;
            }

            try {
                if (!(event.data && 'type' in event.data)) {
                    return;
                }

                switch (event.data.type) {
                    case 'suggestFrameHeight':
                        setFrameHeight(event.data.height);
                        break;
                    case 'suggestHasValue':
                        setHasValue(event.data.hasValue);
                        break;
                    case 'suggestInited':
                        setFrameLoaded(true);
                        if (loadTimeoutRef.current) {
                            clearTimeout(loadTimeoutRef.current);
                            loadTimeoutRef.current = undefined;
                        }
                        sendMessage({
                            type: 'suggestSuccessfullyInited',
                        });
                        log(props.block, 'Iframe loaded');
                        break;
                    case 'suggestFocus':
                        if (props.autoscroll) {
                            if (event.data.focused) {
                                showSuggest();
                            } else {
                                hideSuggest();
                            }
                        }
                        break;
                    case 'suggestManualFocus':
                        setHasFocus(event.data.focused);
                        hasFocusRef.current = event.data.focused;
                        break;
                }
            } catch (err) {
                // unknown event
            }
        };

        const onScroll = throttle(() => {
            if (!frameRef.current) {
                return;
            }
            const bbox = frameRef.current.getBoundingClientRect();
            if (hasFocusRef.current && bbox.bottom < 0) {
                sendMessage({
                    type: 'suggestClosePopup',
                });
                if (frameRef.current === document.activeElement) {
                    frameRef.current.blur();
                }
            }
        }, SCROLL_THROTTLE);

        window.addEventListener('message', onMessage);
        window.addEventListener('scroll', onScroll);

        loadTimeoutRef.current = setTimeout(() => {
            setFrameError(true);
            log(props.block, 'Iframe timed out');
        }, props.iframeTimeout);

        sendMessage({
            type: 'suggestPing',
        });

        return () => {
            window.removeEventListener('message', onMessage);
            window.removeEventListener('scroll', onScroll);

            if (loadTimeoutRef.current) {
                clearTimeout(loadTimeoutRef.current);
                loadTimeoutRef.current = undefined;
            }
        };
    });

    const onButtonClick = useCallback(() => {
        sendMessage({
            type: 'suggestSubmitted',
        });
    }, [sendMessage]);

    const onFrameError = useCallback(() => {
        setFrameError(true);
        log(props.block, 'Iframe loaded with error');
        if (loadTimeoutRef.current) {
            clearTimeout(loadTimeoutRef.current);
            loadTimeoutRef.current = undefined;
        }
    }, [props.block]);

    const onOverlayTouchStart = useCallback(() => {
        sendMessage({
            type: 'suggestClosePopup',
        });
    }, [sendMessage]);

    const onSubmit = useCallback(
        (event) => {
            if (!hasFrameError) {
                event.preventDefault();
            }
        },
        [hasFrameError],
    );

    const onLogoTouchStart = useCallback(
        (event) => {
            event.preventDefault();

            sendMessage({
                type: hasFocus ? 'suggestClosePopup' : 'suggestFocusInput',
            });
        },
        [hasFocus, sendMessage],
    );

    const onLogoTouchEnd = useCallback((event) => {
        event.preventDefault();
    }, []);

    return {
        frameHeight,
        frameRef,
        hasFrameError,
        hasValue,
        onButtonClick,
        onFrameError,
        onOverlayTouchStart,
        isFrameLoaded,
        hasFocus,
        onSubmit,
        onLogoTouchStart,
        onLogoTouchEnd,
    };
};
