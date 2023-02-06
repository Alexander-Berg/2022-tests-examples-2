/* eslint-disable */

import React, {FC} from 'react';
import cn from 'classnames';
import { Platform, useSearchArrowCommon } from './use-search-arrow-common';

type Props = {
    platform: Platform;
};

export const DzenSearchArrowCommon: FC<Props> = ({platform}) => {
    const isMobile = platform === Platform.mobile;

    const {
        frameRef,
        frameHeight,
        hasValue,
        hasFrameError,
        isFrameLoaded,
        hasFocus,
        onFrameError,
        onOverlayTouchStart,
        onButtonClick,
        onSubmit,
        onLogoTouchStart,
        onLogoTouchEnd,
    } = useSearchArrowCommon({
        platform,
        block: `dzen-search-arrow-${isMobile ? 'mobile' : 'desktop'}`,
        iframeTimeout: 5000,
        autoscroll: isMobile,
    });

    const frameUrl = '/portal/dzensearch/' + (isMobile ? 'touch' : 'desktop');

    const input = hasFrameError ? (
        <input
            className="dzen-search-arrow-common__input"
            type="text"
            name="text"
            placeholder="поиск в Яндексе"
            autoComplete="off"
            autoCorrect="off"
            autoCapitalize="off"
            spellCheck="false"
            maxLength={400}
        />
    ) : (
        <iframe
            ref={frameRef}
            style={{height: frameHeight}}
            className={cn('dzen-search-arrow-common__frame', {['dzen-search-arrow-common__visible']: isFrameLoaded})}
            src={frameUrl}
            onError={onFrameError}
            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-ignore
            fetchpriority="high"
            loading="eager"
        ></iframe>
    );

    return (
        <form
            action="https://yandex.ru/search"
            className={cn('dzen-search-arrow-common__arrow', {
                'dzen-search-arrow-common__mobile': isMobile,
                'dzen-search-arrow-common__desktop': !isMobile,
            })}
            onSubmit={onSubmit}
        >
            <div
                className={cn('dzen-search-arrow-common__overlay', {['dzen-search-arrow-common__visible']: hasFocus})}
                onTouchStart={onOverlayTouchStart}
                onClick={onOverlayTouchStart}
            ></div>
            <div className={cn('dzen-search-arrow-common__bg')}></div>
            {input}
            <div className={cn('dzen-search-arrow-common__border')}>
                <div
                    className={cn('dzen-search-arrow-common__logo', {['dzen-search-arrow-common__hasFocus']: hasFocus})}
                    onTouchStart={onLogoTouchStart}
                    onTouchEnd={onLogoTouchEnd}
                ></div>
                {!hasValue && !hasFrameError && (
                    <div className={cn('dzen-search-arrow-common__placeholder',
                        {['dzen-search-arrow-common__hasFocus']: hasFocus})}>
                        поиск в Яндексе
                    </div>
                )}
                <button className={cn('dzen-search-arrow-common__button')} type="submit" onClick={onButtonClick}>
                    Найти
                </button>
            </div>
        </form>
    );
};
