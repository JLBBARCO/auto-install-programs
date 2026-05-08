import { useCallback, useEffect, useRef, useState } from "react";
import {
  LOG_MONITOR_TIMEOUT_MS,
  LOG_SERVER_URL,
  LOG_TOLERANCE_MS,
} from "@/constants/app";
import { fetchLogStream } from "@/lib/logFetcher";
import {
  bucketLogLevel,
  classifyLogSection,
  parseLogLine,
  type LogLevel,
} from "@/lib/logParser";

export interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
}

export interface LogBuckets {
  info: LogEntry[];
  warning: LogEntry[];
  error: LogEntry[];
  history: LogEntry[];
}

interface UseLogMonitorResult extends LogBuckets {
  isLoading: boolean;
  monitorError: Error | null;
}

/**
 * Hook customizado para monitorar logs em tempo real
 *
 * Responsabilidades:
 * - Conectar ao servidor de logs via streaming
 * - Fazer parse das linhas
 * - Classificar e bucketizar os logs
 * - Gerenciar timeout e cancelamento
 * - Retornar estado atualizado
 *
 * @returns Estado dos logs e status do monitoramento
 */
export function useLogMonitor(): UseLogMonitorResult {
  const [info, setInfo] = useState<LogEntry[]>([]);
  const [warning, setWarning] = useState<LogEntry[]>([]);
  const [error, setError] = useState<LogEntry[]>([]);
  const [history, setHistory] = useState<LogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [monitorError, setMonitorError] = useState<Error | null>(null);

  // Refs para lifecycle seguro
  const controllerRef = useRef<AbortController | null>(null);
  const timeoutIdRef = useRef<NodeJS.Timeout | null>(null);
  const loadTimeRef = useRef(new Date());

  // Função pura para bucketizar log
  const appendLog = useCallback(
    (entry: LogEntry, section: "current" | "history") => {
      if (section === "history") {
        setHistory(prev => [...prev, entry]);
        return;
      }

      const bucket = bucketLogLevel(entry.level);

      if (bucket === "warning") {
        setWarning(prev => [...prev, entry]);
        return;
      }

      if (bucket === "error") {
        setError(prev => [...prev, entry]);
        return;
      }

      setInfo(prev => [...prev, entry]);
    },
    []
  );

  useEffect(() => {
    const controller = new AbortController();
    controllerRef.current = controller;

    let didTimeout = false;

    const timeoutId = window.setTimeout(() => {
      didTimeout = true;
      setIsLoading(false);
      setMonitorError(new Error("Timeout ao conectar na porta 8000"));
      controller.abort();
    }, LOG_MONITOR_TIMEOUT_MS);

    timeoutIdRef.current = timeoutId;

    const monitorLogs = async () => {
      try {
        for await (const rawLine of fetchLogStream(LOG_SERVER_URL, {
          signal: controller.signal,
        })) {
          const parsed = parseLogLine(rawLine);

          if (!parsed) {
            continue;
          }

          const section = classifyLogSection(
            parsed.timestamp,
            loadTimeRef.current
          );
          const entry: LogEntry = {
            timestamp: parsed.timestampRaw,
            level: parsed.level,
            message: parsed.message,
          };

          appendLog(entry, section);
          setIsLoading(false);

          if (parsed.message.trim().toLowerCase() === "end system") {
            controller.abort();
            window.clearTimeout(timeoutId);
            return;
          }
        }
      } catch (err) {
        if (!controller.signal.aborted && !didTimeout) {
          setMonitorError(
            err instanceof Error
              ? err
              : new Error("Erro desconhecido ao monitorar logs")
          );
          setIsLoading(false);
        }
      }
    };

    void monitorLogs();

    // Cleanup
    return () => {
      window.clearTimeout(timeoutId);
      controller.abort();
      controllerRef.current = null;
      timeoutIdRef.current = null;
    };
  }, [appendLog]);

  return {
    info,
    warning,
    error,
    history,
    isLoading,
    monitorError,
  };
}
