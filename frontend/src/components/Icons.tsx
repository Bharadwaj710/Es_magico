import { ReactNode } from "react";

type IconProps = { size?: number; className?: string };

function Icon({ children, size = 18, className }: IconProps & { children: ReactNode }) {
  return <svg aria-hidden="true" className={className} fill="none" height={size} viewBox="0 0 24 24" width={size} xmlns="http://www.w3.org/2000/svg">{children}</svg>;
}

export function UploadIcon(props: IconProps) { return <Icon {...props}><path d="M12 16V4m0 0L7.5 8.5M12 4l4.5 4.5M5 16.5v2A1.5 1.5 0 0 0 6.5 20h11a1.5 1.5 0 0 0 1.5-1.5v-2" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" /></Icon>; }
export function StudentsIcon(props: IconProps) { return <Icon {...props}><circle cx="12" cy="12" r="7.5" stroke="currentColor" strokeWidth="1.8" /></Icon>; }
export function SearchIcon(props: IconProps) { return <Icon {...props}><circle cx="10.8" cy="10.8" r="5.8" stroke="currentColor" strokeWidth="1.8" /><path d="m15.2 15.2 4 4" stroke="currentColor" strokeLinecap="round" strokeWidth="1.8" /></Icon>; }
export function ArrowLeftIcon(props: IconProps) { return <Icon {...props}><path d="M19 12H5m0 0 5-5m-5 5 5 5" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" /></Icon>; }
export function ArrowRightIcon(props: IconProps) { return <Icon {...props}><path d="M5 12h14m0 0-5-5m5 5-5 5" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" /></Icon>; }
export function EmptyIcon(props: IconProps) { return <Icon {...props}><circle cx="12" cy="12" r="7.5" stroke="currentColor" strokeWidth="1.8" /><path d="M9 9h.01M15 9h.01M8.5 14.5c1.8 1.5 5.2 1.5 7 0" stroke="currentColor" strokeLinecap="round" strokeWidth="1.8" /></Icon>; }
