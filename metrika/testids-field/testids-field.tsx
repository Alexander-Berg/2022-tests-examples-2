import React, { useCallback, useRef, useState } from 'react';
import { bem } from '@client-libs/bem/bem';
import { Button } from '@client-libs/mindstorms/components/button/button';
import { ButtonHtmlType, ButtonSize, ButtonView } from '@client-libs/mindstorms/components/button/button-props';
import { TextInput } from '@client-libs/mindstorms/components/text-input/text-input';
import { TextInputSize, TextInputView } from '@client-libs/mindstorms/components/text-input/text-input-props';
import { SvgIconSize } from '@client-libs/mindstorms/components/icon/svg-icon-size';
import { PlusIcon } from '@client-libs/mindstorms/components/icon/plus-icon';
import { TrashIcon } from '@client-libs/mindstorms/components/icon/trash-icon';
import { CrossIcon } from '@client-libs/mindstorms/components/icon/cross-icon';
import { ComponentWidth } from '@client-libs/mindstorms/common-prop-types/component-width';
import { ExpLetter } from '../exp-letter/exp-letter';
import { Box } from '../box/box';
import { TestIdsFieldItemValue, TestIdsFieldProps } from './testids-field-props';
import { getItemDefaultValue } from './testids-field-utils';
import './testids-field.css';

const cls = bem('testids-field');

interface ItemProps extends TestIdsFieldItemValue {
    index: number;
    isDisabled?: boolean;
    onAdd?: () => void;
    onChange: (index: number, value: [string, string][]) => void;
    onRemove: (index: number) => void;
    onTitleChange: (index: number, title: string) => void;
    onFlagsRemove?: (index: number, flagsIndex: number) => void;
}

interface KeyValue {
    index: number;
    name: string;
    value: string;
}

interface KeyValueProps extends KeyValue {
    onClick: () => void;
    onChange: (index: number, value: [string, string]) => void;
    onRemove?: (flagsIndex: number) => void;
    isDisabled?: boolean;
}

const MAX_FLAGS = 20;
const MAX_ITEMS = 26;

const KeyValue: React.FC<KeyValueProps> = props => {
    const { name, index, value, onChange, onRemove } = props;
    const onKeyChange = useCallback(
        (e: React.FocusEvent<HTMLInputElement>) => onChange(index, [e.target.value, value]),
        [onChange, value, index]
    );
    const onValueChange = useCallback(
        (e: React.FocusEvent<HTMLInputElement>) => onChange(index, [name, e.target.value]),
        [onChange, name, index]
    );

    const onClick = useCallback(() => {
        if (onRemove) {
            return onRemove(index);
        }

        props.onClick();
    }, [onRemove, props.onClick, index]);

    return (
        <div className={cls('key-value')}>
            <TextInput
                onBlur={onKeyChange}
                value={props.name}
                view={TextInputView.Default}
                size={TextInputSize.S44}
                isDisabled={props.isDisabled}
                maxLength={20}
            />
            {'='}
            <TextInput
                onBlur={onValueChange}
                value={props.value}
                view={TextInputView.Default}
                size={TextInputSize.S44}
                isDisabled={props.isDisabled}
                maxLength={100}
            />
            <Button
                htmlType={ButtonHtmlType.Button}
                icon={onRemove ? <CrossIcon size={SvgIconSize.S16} /> : <PlusIcon size={SvgIconSize.S18} />}
                view={ButtonView.Contrast}
                size={ButtonSize.S36}
                onClick={onClick}
                isDisabled={props.isDisabled}
            />
        </div>
    );
};

const Item: React.FC<ItemProps> = props => {
    const { description, value, index, onChange, onTitleChange, onRemove, isDisabled } = props;

    const inputRef = useRef<HTMLInputElement>(null);
    const [editMode, setEditMode] = useState(false);
    const [name, setName] = useState(props.name);
    const onFlagsChange = useCallback(
        (valIndex: number, val: [string, string]) => {
            (value || [])[valIndex] = val;
            onChange(index, value || []);
        },
        [onChange, index, value]
    );

    const onFlagsRemove = useCallback(
        (valIndex: number) => props.onFlagsRemove?.(index, valIndex),
        [props.onFlagsRemove, index]
    );

    const onAdd = useCallback(() => onChange(index, (value || []).concat([['', '']])), [onChange, index, value]);
    const onRemoveClick = useCallback(() => onRemove(index), [onRemove, index]);
    const onChangeTitle = useCallback((val: string) => setName(val.trim()), []);
    const onBlur = useCallback(() => {
        setEditMode(false);

        if (name) {
            onTitleChange(index, name);
        } else {
            const defaultName = getItemDefaultValue(index).name;

            onTitleChange(index, defaultName);
            setName(defaultName);
        }
    }, [name, onTitleChange, index, props.name]);
    const onEditClick = useCallback(() => {
        setEditMode(true);
        setTimeout(() => inputRef.current?.focus(), 1);
    }, [inputRef]);

    return (
        <div className={cls('item')}>
            <div className={cls('item-title')}>
                <ExpLetter className={cls('letter')} index={index} />
                {editMode ? (
                    <TextInput
                        ref={inputRef}
                        className={cls('item-title-edit')}
                        onChange={onChangeTitle}
                        onBlur={onBlur}
                        size={TextInputSize.S44}
                        view={TextInputView.Default}
                        value={name}
                    />
                ) : (
                    <div className={cls('item-name')}>
                        <span className={cls('item-name-text')} onClick={onEditClick}>
                            {props.name}
                        </span>
                    </div>
                )}
                <div className={cls('item-buttons')}>
                    <Button
                        htmlType={ButtonHtmlType.Button}
                        icon={<TrashIcon size={SvgIconSize.S24} />}
                        view={ButtonView.Contrast}
                        size={ButtonSize.S36}
                        onClick={onRemoveClick}
                        isDisabled={isDisabled || index < 2}
                    />
                </div>
            </div>
            {description && <div className={cls('item-description')}>{description}</div>}
            {value && (
                <>
                    {value.map(([key, val], valIndex) => (
                        <KeyValue
                            index={valIndex}
                            onClick={onAdd}
                            onRemove={
                                valIndex < value.length - 1 || valIndex === MAX_FLAGS - 1 ? onFlagsRemove : undefined
                            }
                            onChange={onFlagsChange}
                            key={valIndex}
                            name={key}
                            value={val}
                            isDisabled={isDisabled}
                        />
                    ))}
                </>
            )}
            {value || isDisabled ? null : (
                <div className={cls('add-flags')} onClick={onAdd}>
                    Добавить флаги
                </div>
            )}
        </div>
    );
};

export const TestIdsField: React.FC<TestIdsFieldProps> = props => {
    const { onChange, value } = props.input;
    const isDisabled = props.isDisabled;

    const onAdd = useCallback(() => onChange(value.concat(getItemDefaultValue(value.length))), [onChange, value]);

    const onRemove = useCallback(index => onChange(value.filter((_, idx) => idx !== index)), [onChange, value]);

    const onItemChange = useCallback(
        (index: number, val: Partial<TestIdsFieldItemValue>) => {
            const copy = [...value];

            copy[index] = {
                ...copy[index],
                ...val,
            };

            onChange(copy);
        },
        [value, onChange]
    );

    const onFlagsRemove = useCallback(
        (index: number, flagsIndex: number) => {
            const copy = [...value];
            const itemCopy = (copy[index] = { ...copy[index] });
            const flagsCopy = (itemCopy.value = itemCopy.value?.slice() ?? []);

            flagsCopy.splice(flagsIndex, 1);

            onChange(copy);
        },
        [onChange, value]
    );

    const onFlagsChange = useCallback(
        (index: number, val: [string, string][]) => onItemChange(index, { value: val }),
        [onItemChange]
    );

    const onTitleChange = useCallback((index: number, name: string) => onItemChange(index, { name }), [onItemChange]);

    return (
        <div className={cls()}>
            {(value || []).map((item, idx) => (
                <Box key={idx}>
                    <Item
                        {...item}
                        onChange={onFlagsChange}
                        onFlagsRemove={onFlagsRemove}
                        onRemove={onRemove}
                        onTitleChange={onTitleChange}
                        index={idx}
                        isDisabled={isDisabled}
                    />
                </Box>
            ))}
            {isDisabled || value.length >= MAX_ITEMS ? null : (
                <Button
                    key="button"
                    htmlType={ButtonHtmlType.Button}
                    size={ButtonSize.S44}
                    view={ButtonView.Contrast}
                    onClick={onAdd}
                    width={ComponentWidth.Max}
                >
                    Добавить вариант
                </Button>
            )}
        </div>
    );
};
