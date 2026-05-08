/**
 * Constantes globais da aplicação
 * Centralize valores mágicos aqui para fácil manutenção
 */

// URLs e Endpoints
export const LOG_SERVER_URL = "http://localhost:8000/log.log";
export const CONTACT_API_ENDPOINTS = [
  "/api/contact",
  "https://raw.githubusercontent.com/JLBBARCO/portfolio/main/src/json/areas/contact.json",
] as const;

// Timeouts e Durações
export const LOG_MONITOR_TIMEOUT_MS = 30_000; // 30 segundos
export const LOG_TOLERANCE_MS = 60_000; // 1 minuto de tolerância
export const CONTACT_FETCH_TIMEOUT_MS = 5_000; // 5 segundos

// Mensagens e Textos
export const MESSAGES = {
  LOG_WAITING: "Aguardando logs...",
  LOADING_CONTACTS: "Carregando contatos...",
  CONTACT_ERROR: "Erro ao carregar contatos",
  PORT_ERROR: "Porta 8000 indisponível",
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
