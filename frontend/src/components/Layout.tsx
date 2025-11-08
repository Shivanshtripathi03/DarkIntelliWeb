import { ReactNode } from 'react';

interface LayoutProps {
  children: ReactNode;
}

export const Layout = ({ children }: LayoutProps) => {
  return (
    <div className="min-h-screen bg-black">
      <div className="container mx-auto px-4 py-8">
        {children}
      </div>
    </div>
  );
};
