/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_API_TIMEOUT: string;
  readonly VITE_SCRIPTS_PATH: string;
  readonly VITE_APP_NAME: string;
  readonly VITE_APP_VERSION: string;
  readonly VITE_APP_ENV: string;
  readonly VITE_ENABLE_ANALYTICS: string;
  readonly VITE_ENABLE_DARK_MODE: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
