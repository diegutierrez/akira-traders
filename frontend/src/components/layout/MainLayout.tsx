import { Outlet, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'

const navigation = [
  { name: 'Dashboard', href: '/dashboard' },
  { name: 'Traders', href: '/traders' },
  { name: 'Nueva Evaluación', href: '/evaluations/new' },
  { name: 'Analytics', href: '/analytics' },
]

export function MainLayout() {
  const { user, logout } = useAuth()
  const location = useLocation()

  const userEmail = user?.email
  const userName = user?.user_metadata?.full_name || user?.user_metadata?.name
  const userPicture = user?.user_metadata?.avatar_url || user?.user_metadata?.picture

  return (
    <div className="min-h-screen bg-bg-primary">
      {/* Header */}
      <header className="bg-bg-secondary border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/dashboard" className="flex items-center gap-2">
              <span className="text-xl font-bold text-primary">Akira</span>
              <span className="text-xl font-bold text-text-primary">Traders</span>
            </Link>

            {/* Navigation */}
            <nav className="hidden md:flex items-center gap-1">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-bg-tertiary text-primary'
                        : 'text-text-secondary hover:text-text-primary hover:bg-bg-tertiary'
                    }`}
                  >
                    {item.name}
                  </Link>
                )
              })}
            </nav>

            {/* User Menu */}
            <div className="flex items-center gap-3">
              {user && (
                <>
                  <div className="hidden sm:flex items-center gap-2">
                    {userPicture && (
                      <img
                        src={userPicture}
                        alt={userName || userEmail || ''}
                        className="w-8 h-8 rounded-full"
                      />
                    )}
                    <span className="text-sm text-text-secondary">
                      {userName || userEmail}
                    </span>
                  </div>
                  <button
                    onClick={() => logout()}
                    className="px-3 py-1.5 text-sm text-text-secondary hover:text-danger transition-colors"
                  >
                    Salir
                  </button>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        <nav className="md:hidden border-t border-border px-4 py-2 flex gap-1 overflow-x-auto">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                  isActive
                    ? 'bg-bg-tertiary text-primary'
                    : 'text-text-secondary hover:text-text-primary'
                }`}
              >
                {item.name}
              </Link>
            )
          })}
        </nav>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <Outlet />
      </main>
    </div>
  )
}
