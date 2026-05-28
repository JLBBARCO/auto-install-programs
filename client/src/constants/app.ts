/**
 * Constantes globais da aplicação
 * Centralize valores mágicos aqui para fácil manutenção
 */

export const MIN_DYNAMIC_LOG_SERVER_PORT = 9900;
export const MAX_DYNAMIC_LOG_SERVER_PORT = 9999;
export const DEFAULT_LOG_SERVER_PORT = 9999;
export const LOG_SERVER_PATH = "/log.log";
export const DEFAULT_PROGRAMS_MANAGER_SITE_URL =
  "https://jlbbarco.github.io/programs-manager";
export const FALLBACK_PROGRAMS_MANAGER_SITE_URL =
  "https://passwords-manager-jlbbarco.vercel.app";

// URLs e Endpoints
export const CONTACT_API_ENDPOINTS = [
  "/api/contact",
  "https://raw.githubusercontent.com/JLBBARCO/portfolio/main/src/json/areas/contact.json",
] as const;

export function getConfiguredLogServerPort(): number {
  const searchParams =
    typeof window === "undefined"
      ? new URLSearchParams("")
      : new URLSearchParams(window.location.search);

  const rawPort = searchParams.get("port");
  const parsedPort = Number.parseInt(rawPort ?? "", 10);

  if (
    Number.isInteger(parsedPort) &&
    parsedPort >= MIN_DYNAMIC_LOG_SERVER_PORT &&
    parsedPort <= MAX_DYNAMIC_LOG_SERVER_PORT
  ) {
    return parsedPort;
  }

  return DEFAULT_LOG_SERVER_PORT;
}

export function getLogServerPortFromUrl(url: string): number {
  const parsedPort = Number.parseInt(new URL(url).port || "", 10);

  if (
    Number.isInteger(parsedPort) &&
    parsedPort >= MIN_DYNAMIC_LOG_SERVER_PORT &&
    parsedPort <= MAX_DYNAMIC_LOG_SERVER_PORT
  ) {
    return parsedPort;
  }

  return getConfiguredLogServerPort();
}

export function getLogServerUrl(port = getConfiguredLogServerPort()): string {
  return `http://localhost:${port}${LOG_SERVER_PATH}`;
}

export function getProgramsManagerSiteUrl(
  port = getConfiguredLogServerPort(),
  baseUrl = import.meta.env.VITE_PROGRAMS_MANAGER_SITE_URL ??
    DEFAULT_PROGRAMS_MANAGER_SITE_URL
): string {
  const siteUrl = new URL(baseUrl);
  siteUrl.searchParams.set("port", String(port));
  return siteUrl.toString();
}

export function getFallbackProgramsManagerSiteUrl(
  port = getConfiguredLogServerPort(),
  baseUrl = import.meta.env.VITE_PROGRAMS_MANAGER_SITE_FALLBACK_URL ??
    FALLBACK_PROGRAMS_MANAGER_SITE_URL
): string {
  const siteUrl = new URL(baseUrl);
  siteUrl.searchParams.set("port", String(port));
  return siteUrl.toString();
}

export function getLogServerDisplay(port = getConfiguredLogServerPort()) {
  return {
    port,
    portError: `Porta ${port} indisponível`,
    timeout: `Timeout ao conectar na porta ${port}`,
    troubleshootingHint: `Verifique se o servidor está rodando em: ${getLogServerUrl(port)}`,
  };
}

// Timeouts e Durações
export const LOG_MONITOR_TIMEOUT_MS = 30_000; // 30 segundos
export const LOG_TOLERANCE_MS = 60_000; // 1 minuto de tolerância
export const CONTACT_FETCH_TIMEOUT_MS = 5_000; // 5 segundos

// Mensagens e Textos
export const MESSAGES = {
  LOG_WAITING: "Aguardando logs...",
  LOADING_CONTACTS: "Carregando contatos...",
  CONTACT_ERROR: "Erro ao carregar contatos",
  PORT_ERROR: "Porta indisponível",
  CONNECTION_ERROR: "Conexão Recusada",
  PORT_ERROR_HINT:
    "Faça refresh na página ou reexecute o programa para tentar novamente.",
  PORT_ERROR_TIMEOUT: "Timeout: 30 segundos de monitoramento",
  AUTO_SCROLL_ENABLED: "Auto-scroll ativado",
  PAUSED_INDICATOR: "Pausado",
  HISTORY_TITLE: "Histórico de Execuções",
  APP_TITLE: "Programs Manager",
  APP_SUBTITLE: "Monitoramento em tempo real de execução de programas",
  RETRY_BUTTON: "Tentar Novamente",
  OPEN_LOG_SERVER: "Abrir Servidor de Logs",
  TROUBLESHOOTING_HINT: "Verifique se o servidor está rodando em:",
} as const;

// Cores e Estilos
export const LOG_LEVEL_STYLES = {
  SUCCESS: {
    border: "border-l-emerald-500",
    badge: "bg-emerald-500/10 text-emerald-700",
  },
  WARNING: {
    border: "border-l-amber-500",
    badge: "bg-amber-500/10 text-amber-700",
  },
  ERROR: {
    border: "border-l-red-500",
    badge: "bg-red-500/10 text-red-700",
  },
  INFO: {
    border: "border-l-sky-500",
    badge: "bg-sky-500/10 text-sky-700",
  },
} as const;

export const TIMESTAMP_COLOR = "#808080";

// Ícones de Contato
export const ICON_NAMES = {
  EMAIL: "email",
  GITHUB: "github",
  LINKEDIN: "linkedin",
} as const;
