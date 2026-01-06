import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import { useGoogleLogin, googleLogout } from '@react-oauth/google';
import { jwtDecode } from 'jwt-decode';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000/api';
const ALLOWED_EMAIL = import.meta.env.VITE_ALLOWED_EMAIL;

interface User {
  email: string;
  name: string;
  picture: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: () => void;
  logout: () => void;
}

interface JWTPayload {
  email: string;
  name: string;
  picture: string;
  exp: number;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Verificar token existente al cargar
  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token');
    if (storedToken) {
      try {
        const decoded = jwtDecode<JWTPayload>(storedToken);

        // Verificar si el token no ha expirado
        if (decoded.exp * 1000 > Date.now()) {
          setToken(storedToken);
          setUser({
            email: decoded.email,
            name: decoded.name,
            picture: decoded.picture,
          });
        } else {
          localStorage.removeItem('auth_token');
        }
      } catch {
        localStorage.removeItem('auth_token');
      }
    }
    setIsLoading(false);
  }, []);

  const handleGoogleSuccess = useCallback(async (accessToken: string) => {
    try {
      // Obtener info del usuario de Google
      const userInfoResponse = await fetch(
        'https://www.googleapis.com/oauth2/v3/userinfo',
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );
      const userInfo = await userInfoResponse.json();

      // Verificar email permitido (frontend check)
      if (ALLOWED_EMAIL && userInfo.email !== ALLOWED_EMAIL) {
        throw new Error('Email no autorizado');
      }

      // Obtener el id_token para enviar al backend
      const tokenResponse = await fetch(
        `https://oauth2.googleapis.com/tokeninfo?access_token=${accessToken}`
      );
      const tokenInfo = await tokenResponse.json();

      // Autenticar con el backend
      const response = await fetch(`${API_URL}/auth/google`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: accessToken }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Error de autenticación');
      }

      const data = await response.json();

      // Guardar token y usuario
      localStorage.setItem('auth_token', data.token);
      setToken(data.token);
      setUser(data.user);
    } catch (error) {
      console.error('Error en autenticación:', error);
      logout();
      throw error;
    }
  }, []);

  const googleLogin = useGoogleLogin({
    onSuccess: (response) => handleGoogleSuccess(response.access_token),
    onError: (error) => console.error('Error de Google Login:', error),
  });

  const login = useCallback(() => {
    googleLogin();
  }, [googleLogin]);

  const logout = useCallback(() => {
    googleLogout();
    localStorage.removeItem('auth_token');
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user && !!token,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de un AuthProvider');
  }
  return context;
}
