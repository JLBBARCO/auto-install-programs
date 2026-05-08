import { useEffect, useRef, useState } from "react";
import { LOG_LEVEL_STYLES, MESSAGES, TIMESTAMP_COLOR } from "@/constants/app";

interface LogEntry {
  timestamp: string;
  level: "INFO" | "SUCCESS" | "WARNING" | "ERROR";
  message: string;
}

interface LogContainerProps {
  title: string;
  entries: LogEntry[];
}

function getLevelStyles(level: LogEntry["level"]) {
  return LOG_LEVEL_STYLES[level] || LOG_LEVEL_STYLES.INFO;
}

export function LogContainer({ title, entries }: LogContainerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isAutoScrolling, setIsAutoScrolling] = useState(true);

  useEffect(() => {
    if (isAutoScrolling && containerRef.current) {
      const scrollTimeout = setTimeout(() => {
        if (containerRef.current) {
          containerRef.current.scrollTop = containerRef.current.scrollHeight;
          containerRef.current.scrollLeft = containerRef.current.scrollWidth;
        }
      }, 100);
      return () => clearTimeout(scrollTimeout);
    }
  }, [entries, isAutoScrolling]);

  const handleScroll = () => {
    if (!containerRef.current) return;

    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 10;

    if (!isAtBottom && isAutoScrolling) {
      setIsAutoScrolling(false);
    } else if (isAtBottom && !isAutoScrolling) {
      setIsAutoScrolling(true);
    }
  };

  return (
    <div className="flex flex-col h-full gap-2">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-display font-bold text-foreground">
          {title}
        </h2>
        {!isAutoScrolling && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground" aria-live="polite">
              {MESSAGES.PAUSED_INDICATOR}
            </span>
            <div
              className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"
              aria-hidden="true"
            ></div>
          </div>
        )}
      </div>

      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="log-container flex-1 overflow-auto border border-border rounded-lg bg-card shadow-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
        role="region"
        aria-label={`${title} logs`}
        aria-live="polite"
        aria-atomic="false"
      >
        {entries.length === 0 ? (
          <div
            className="flex items-center justify-center h-full text-muted-foreground text-sm"
            role="status"
          >
            {MESSAGES.LOG_WAITING}
          </div>
        ) : (
          <div className="divide-y divide-border/50 min-w-max">
            {entries.map((log, index) => {
              const styles = getLevelStyles(log.level);

              return (
                <div
                  key={`${log.timestamp}-${index}`}
                  className={`flex items-start gap-3 border-l-4 ${styles.border} px-3 py-2 transition-all duration-200 hover:bg-muted/30`}
                >
                  <div className="min-w-max">
                    <div className="flex items-center gap-2 whitespace-nowrap">
                      <time
                        className="text-xs font-mono"
                        style={{ color: TIMESTAMP_COLOR }}
                      >
                        {log.timestamp}
                      </time>
                      <span className="text-foreground/50">|</span>
                      <span className="text-foreground">{log.message}</span>
                    </div>
                  </div>
                  <span
                    className={`rounded-full px-2 py-0.5 text-[10px] font-semibold tracking-wide ${styles.badge} whitespace-nowrap`}
                    aria-label={`Log level: ${log.level}`}
                  >
                    {log.level}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {isAutoScrolling && entries.length > 0 && (
        <div
          className="text-xs text-muted-foreground text-center"
          aria-live="polite"
        >
          {MESSAGES.AUTO_SCROLL_ENABLED}
        </div>
      )}
    </div>
  );
}
