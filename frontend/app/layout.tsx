import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Afriova AI - Tableau de bord',
  description: 'Gestion des agents IA pour entreprises africaines',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black text-white">
          {children}
        </div>
      </body>
    </html>
  )
}