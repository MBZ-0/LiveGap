import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "another.ai",
  description: "Reality check for browser agents",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <script src="https://cdn.tailwindcss.com"></script>
      </head>
      <body className="bg-slate-950 text-slate-50">{children}</body>
    </html>
  );
}
