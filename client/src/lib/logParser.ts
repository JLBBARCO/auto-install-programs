export type LogLevel = "INFO" | "SUCCESS" | "WARNING" | "ERROR";

export type LogSection = "current" | "history";

const LINE_RE =
  /^\[(\d{2}\/\d{2}\/\d{4} \d{2}:\d{2}:\d{2})\] \[(\w+)\](?: \[pid:(\d+)\])?(?: \[thread:([^\]]+)\])?(?: \[caller:([^\]]+)\])? ?(.*)$/;

function parseBrDate(raw: string) {
  const [datePart, timePart] = raw.split(" ");
  const [day, month, year] = datePart.split("/").map(Number);
  const [hour, minute, second] = timePart.split(":").map(Number);

  return new Date(year, month - 1, day, hour, minute, second);
}

export interface ParsedLogLine {
  timestamp: Date;
  timestampRaw: string;
  level: LogLevel;
  pid: string | null;
  thread: string | null;
  caller: string | null;
  message: string;
}

export function parseLogLine(raw: string): ParsedLogLine | null {
  const line = raw.trim();
  if (!line) {
    return null;
  }

  const match = line.match(LINE_RE);
  if (!match) {
    return null;
  }

  const [, dateRaw, level, pid, thread, caller, message] = match;

  return {
    timestamp: parseBrDate(dateRaw),
    timestampRaw: dateRaw,
    level: level.toUpperCase() as LogLevel,
    pid: pid ?? null,
    thread: thread ?? null,
    caller: caller ?? null,
    message: message.trim(),
  };
}

export function classifyLogSection(
  lineTimestamp: Date,
  siteLoadedAt: Date,
): LogSection {
  const diffMs = siteLoadedAt.getTime() - lineTimestamp.getTime();
  return diffMs <= 60_000 ? "current" : "history";
}

export function bucketLogLevel(level: LogLevel) {
  if (level === "WARNING") {
    return "warning" as const;
  }

  if (level === "ERROR") {
    return "error" as const;
  }

  return "info" as const;
}