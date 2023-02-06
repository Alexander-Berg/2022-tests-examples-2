import React, { useRef } from 'react';
import { bem } from '@client-libs/bem/bem';
import { Link } from '@client-libs/mindstorms/components/link/link';
import { LinkView } from '@client-libs/mindstorms/components/link/link-props';
import { Tooltip } from '@client-libs/mindstorms/components/tooltip/tooltip';
import { TooltipSize, TooltipView } from '@client-libs/mindstorms/components/tooltip/tooltip-props';
import { Axis, InversedAxisType } from '@client-libs/mindstorms/components/popup/popup-props';
import { InfoIcon } from '@client-libs/mindstorms/components/icon/info-icon';
import { SvgIconSize } from '@client-libs/mindstorms/components/icon/svg-icon-size';
import { ExpLetter } from '../exp-letter/exp-letter';
import { CheckTestidProps } from './check-testid-props';

import './check-testid.css';

const cls = bem('check-testid');

export const CheckTestid: React.FC<CheckTestidProps> = props => {
    const onClick = React.useCallback(() => {
        props.onClick(props.index);
    }, [props.onClick, props.index]);

    const ref = useRef(null);

    return (
        <div className={cls({ mix: props.className })}>
            <ExpLetter className={cls('letter')} index={props.index} />
            <span className={cls('name')}>{props.name}</span>
            <Link ref={ref} view={LinkView.Base} onClick={onClick}>
                Проверить
            </Link>
            {props.error && (
                <Tooltip
                    size={TooltipSize.M}
                    isVisible
                    view={TooltipView.Dark}
                    anchorPosition={{
                        mainAxis: Axis.Bottom,
                        inversedAxis: InversedAxisType.Center,
                    }}
                    icon={<InfoIcon className={cls('error-icon')} size={SvgIconSize.S20} />}
                    title={props.error.title}
                    description={props.error.message}
                    anchorTarget={ref}
                />
            )}
        </div>
    );
};
