import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Theta AI | AI-Powered Fact Verification by TeraMind",
  description:
    "Theta is an AI research entity by TeraMind, a lab of TService. It verifies viral social media posts using real-time search grounding.",
  keywords: [
    "AI",
    "fact-checking",
    "LLM",
    "TeraMind",
    "Theta",
    "machine learning",
    "misinformation",
  ],
  authors: [{ name: "TeraMind — a TService Lab" }],
  openGraph: {
    title: "Theta AI | AI Fact Verification by TeraMind",
    description:
      "An AI research entity by TeraMind that verifies viral social media posts in real-time.",
    url: "https://theta.tservice.tech",
    siteName: "Theta LLM",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
