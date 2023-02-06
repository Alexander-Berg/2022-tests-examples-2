export interface CheckTestidProps {
    index: number;
    name: string;
    onClick: (index: number) => void;
    error?: {
        title?: string;
        message: string;
    };
    className?: string;
}
