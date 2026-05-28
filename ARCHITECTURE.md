# Architecture & Implementation Guide

## Project Overview

**Programs Manager** é uma aplicação React + TypeScript que monitora logs em tempo real de um servidor local (porta dinâmica no intervalo `9900–9999`), com interface moderna usando Tailwind CSS e Radix UI. O programa comunica a porta selecionada ao site adicionando `?port=NNNN` à URL.

### Stack Técnico

- **Frontend:** React 19.2.1 + Vite 7.1.7
- **Language:** TypeScript 5.6.3 (strict mode)
- **Styling:** Tailwind CSS 4.1.14
- **UI Components:** Radix UI
- **Icons:** Lucide React
- **API:** Vercel Edge Functions

---

## Arquitetura

```tree
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Vite)                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐     │
│  │                    Home Page                        │     │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │     │
│  │  │  LogContainer│ │  LogContainer│ │  LogContainer│ │     │
│  │  │ (Informações)│ │   (Avisos)   │ │   (Erros)    │ │     │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ │     │
│  │  ┌────────────────────────────────────────────────┐ │     │
│  │  │           HistoryView (Expandível)            │ │     │
│  │  └────────────────────────────────────────────────┘ │     │
│  │  ┌────────────────────────────────────────────────┐ │     │
│  │  │            ContactFooter                       │ │     │
│  │  └────────────────────────────────────────────────┘ │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐     │
│  │          Custom Hooks (Business Logic)             │     │
│  │  ┌──────────────────────────────────────────────┐  │     │
│  │  │      useLogMonitor()                        │  │     │
│  │  │ - Stream logs from server                   │  │     │
│  │  │ - Parse and classify                        │  │     │
│  │  │ - Manage state & lifecycle                  │  │     │
│  │  └──────────────────────────────────────────────┘  │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐     │
│  │         Utility Layer (Pure Functions)             │     │
│  │  ┌──────────────────────────────────────────────┐  │     │
│  │  │  logParser.ts                               │  │     │
│  │  │  - parseLogLine()  →  ParsedLogLine         │  │     │
│  │  │  - classifyLogSection()  →  "current"|"his" │  │     │
│  │  │  - bucketLogLevel()  →  "info"|"warn"|"err"│  │     │
│  │  └──────────────────────────────────────────────┘  │     │
│  │  ┌──────────────────────────────────────────────┐  │     │
│  │  │  logFetcher.ts                              │  │     │
│  │  │  - fetchLogStream()  →  AsyncGenerator      │  │     │
│  │  │  - Handles streaming, line buffering        │  │     │
│  │  │  - AbortController support                  │  │     │
│  │  └──────────────────────────────────────────────┘  │     │
│  │  ┌──────────────────────────────────────────────┐  │     │
│  │  │  constants/app.ts                           │  │     │
│  │  │  - All configuration values                 │  │     │
│  │  │  - Messages (i18n ready)                    │  │     │
│  │  │  - Styles & colors                          │  │     │
│  │  └──────────────────────────────────────────────┘  │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
         ↓ (Fetch API with streaming)
┌─────────────────────────────────────────────────────────────┐
│            Backend / Log Server (localhost:99xx)            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  HTTP Server (Python http.server or any static)     │   │
│  │  - Serves: /log.log                                │   │
│  │  - Content-Type: text/plain; charset=utf-8          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         ↓ (Fetch for contact data)
┌─────────────────────────────────────────────────────────────┐
│           External APIs / Vercel Edge Functions             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  api/contact.js (Vercel Edge Function)             │   │
│  │  - Fetches from GitHub (fallback)                  │   │
│  │  - CDN cache: 3600s (stale-while-revalidate 300s)  │   │
│  │  - CORS enabled                                     │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  GitHub Raw Content API                            │   │
│  │  - Fallback endpoint for contact data              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. **Log Streaming Flow**

```tree
useLogMonitor Hook
    ↓
[Initialize state: {info: [], warning: [], error: [], history: []}]
    ↓
[Set 30s timeout timer]
    ↓
fetchLogStream(url, {signal: controller.signal})
    ↓
[For each line received]
    ↓
parseLogLine(line) → ParsedLogLine | null
    ↓
[If null, skip; continue]
    ↓
classifyLogSection(timestamp, siteLoadTime) → "current" | "history"
    ↓
bucketLogLevel(level) → "info" | "warning" | "error"
    ↓
[Append to appropriate state array]
    ↓
[Component re-renders with new entry]
    ↓
[Auto-scroll to bottom if enabled]
    ↓
[On "End system" or timeout/error]
    ↓
[Abort controller, clear timeout, show result]
```

### 2. **Component Update Flow**

```tree
useLogMonitor returns: { info, warning, error, history, isLoading, error }
    ↓
Home.tsx receives hook result
    ↓
[if error: return ErrorState]
[else if isLoading: render Skeletons]
[else: render LogContainers with data]
    ↓
LogContainer receives entries
    ↓
[maps entries to DOM]
    ↓
[applies styles from LOG_LEVEL_STYLES constant]
    ↓
[renders with accessibility attributes]
```

### 3. **Contact Footer Flow**

```tree
ContactFooter mounts
    ↓
[Set loading state]
    ↓
[For each endpoint in CONTACT_API_ENDPOINTS]
    ↓
[Try to fetch with CONTACT_FETCH_TIMEOUT_MS abort]
    ↓
[If success and has data: set contacts, return]
[If fail: continue to next endpoint]
    ↓
[If all fail: set error state]
    ↓
[Render ContactSkeleton while loading]
[Render cards or error message when done]
```

---

## File Organization

### Core Files

#### `client/src/constants/app.ts` (50 linhas)

**Purpose:** Centralized configuration

```ts
// The runtime log server URL includes the chosen port. The site reads `?port=NNNN` or falls back to a default in the 99xx range.
export const LOG_SERVER_URL = "http://localhost:<port>/log.log"
export const LOG_MONITOR_TIMEOUT_MS = 30_000
export const MESSAGES = { ... } // 18 chaves
export const LOG_LEVEL_STYLES = { ... }
export const TIMESTAMP_COLOR = "#808080"
export const ICON_NAMES = { EMAIL, GITHUB, LINKEDIN }
```

#### `client/src/lib/logParser.ts` (110 linhas)

**Purpose:** Parse and classify log lines

```ts
interface ParsedLogLine {
  timestamp: Date;
  timestampRaw: string;
  level: LogLevel;
  message: string;
}

export function parseLogLine(raw: string): ParsedLogLine | null;
export function classifyLogSection(
  timestamp: Date,
  siteLoadedAt: Date
): "current" | "history";
export function bucketLogLevel(level: LogLevel): "info" | "warning" | "error";
```

**Regex Pattern:**

```regex
^\[(\d{2}\/\d{2}\/\d{4} \d{2}:\d{2}:\d{2})\] \[([^\]]+)\].*\] (.+)$
```

#### `client/src/lib/logFetcher.ts` (50 linhas)

**Purpose:** Stream logs from server

```ts
export async function* fetchLogStream(
  url: string,
  options?: { signal: AbortSignal }
): AsyncGenerator<string>

// Implementation:
// 1. fetch(url, { headers, signal })
// 2. response.body.getReader()
// 3. TextDecoder for UTF-8
// 4. Split on \n or \r\n
// 5. Buffer incomplete final line
// 6. Yield only complete lines
```

#### `client/src/hooks/useLogMonitor.ts` (130 linhas)

**Purpose:** Orchestrate log streaming lifecycle

```ts
interface UseLogMonitorResult {
  info: LogEntry[];
  warning: LogEntry[];
  error: LogEntry[];
  history: LogEntry[];
  isLoading: boolean;
  error: Error | null;
}

export function useLogMonitor(): UseLogMonitorResult;

// Features:
// - Auto-timeout after 30s
// - Stops on "End system" message
// - Separates current vs history logs
// - Cleanup: abort + clear timeout on unmount
// - Type-safe with TypeScript
```

#### `client/src/components/Skeletons.tsx` (30 linhas)

**Purpose:** Loading placeholders

```ts
export function LogContainerSkeleton(): JSX.Element;
export function ContactSkeleton(): JSX.Element;

// Uses Tailwind: animate-pulse, h-4 w-full rounded bg-muted
```

### Component Files

#### `client/src/pages/Home.tsx` (60 linhas)

**Purpose:** Main application page

```ts
// Uses: useLogMonitor, LogContainer, HistoryView, ContactFooter, ErrorState
// Flow:
// 1. Call hook
// 2. If error → ErrorState
// 3. If loading → Skeletons
// 4. Else → Containers with data
// 5. Render footer
```

#### `client/src/components/LogContainer.tsx` (120 linhas)

**Purpose:** Display single log bucket with auto-scroll

```ts
interface LogContainerProps {
  title: string;
  entries: LogEntry[];
}

// Features:
// - Auto-scroll to bottom
// - Manual scroll pauses auto-scroll
// - Resumable when scrolled to bottom
// - Hover effects
// - Accessibility: role, aria-live, aria-label
```

#### `client/src/components/HistoryView.tsx` (100 linhas)

**Purpose:** Expandible history section

```ts
interface HistoryViewProps {
  historyLogs: LogEntry[];
}

// Features:
// - Collapsible accordion style
// - Shows log count
// - Max-height with scroll
// - Uses same styles as LogContainer
```

#### `client/src/components/ContactFooter.tsx` (80 linhas)

**Purpose:** Display contact cards with fallback

```ts
interface ContactCard {
  name: string;
  iconName: string;
  url: string;
}

// Features:
// - Dual endpoint fallback
// - Timeout handling
// - Icon mapping
// - Loading skeletons
// - Error state
```

#### `client/src/components/ErrorState.tsx` (50 linhas)

**Purpose:** Error UI for connection failures

```ts
interface ErrorStateProps {
  onRefresh: () => void;
}

// Features:
// - Clear error message
// - Retry button
// - Server URL instructions
// - Links to troubleshooting
```

### Backend Files

#### `api/contact.js` (40 linhas)

**Purpose:** Vercel Edge Function for contact data

```js
export default async function handler(request) {
  // 1. Fetch from GitHub raw
  // 2. Cache headers: s-maxage=3600, stale-while-revalidate=300
  // 3. CORS headers
  // 4. Error fallback
}
```

### Configuration Files

#### `tsconfig.json`

**Changes:** Removed deprecated `baseUrl`

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "strict": true,
    "jsx": "react-jsx",
    "moduleResolution": "bundler",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

---

## SOLID Principles Applied

### ✅ Single Responsibility

- `logParser.ts` → Only parsing
- `logFetcher.ts` → Only fetching
- `useLogMonitor` → Only orchestration
- `LogContainer` → Only display one bucket
- `ContactFooter` → Only contact display
- `ErrorState` → Only error display

### ✅ Open/Closed

- New log levels → Add to constants
- New messages → Add to MESSAGES object
- New styles → Add to LOG_LEVEL_STYLES

### ✅ Liskov Substitution

- All components follow React component contract
- Hook follows standard React hook contract

### ✅ Interface Segregation

- `LogEntry` has only needed fields
- `UseLogMonitorResult` returns only what's needed
- `ContactCard` is minimal interface

### ✅ Dependency Inversion

- Components depend on constants, not hardcoded values
- Hook depends on abstractions (parser, fetcher)

---

## Performance Optimizations

### Build Time

- TypeScript strict mode → Catches errors early
- Vite fast refresh → <100ms recompile
- esbuild production → Tree-shaking unused code

### Runtime

- Async generator → Memory efficient streaming
- AbortController → Cancellable requests
- TextDecoder → Incremental UTF-8 parsing
- useLogMonitor memoization → Prevents re-renders

### Network

- CDN caching → 3600s stale-while-revalidate 300s
- Content-Type negotiation → Bandwidth efficient
- Accept headers → Server optimization

---

## Type Safety

### TypeScript Configuration

- **Mode:** `strict`
- **Target:** ES2020
- **Module:** ES2020 (native import/export)

### Custom Types

```ts
type LogLevel = "INFO" | "SUCCESS" | "WARNING" | "ERROR";

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
}

interface ParsedLogLine {
  timestamp: Date;
  timestampRaw: string;
  level: LogLevel;
  message: string;
}

interface UseLogMonitorResult {
  info: LogEntry[];
  warning: LogEntry[];
  error: LogEntry[];
  history: LogEntry[];
  isLoading: boolean;
  error: Error | null;
}
```

---

## Accessibility Features

### ARIA Attributes

- `role="region"` on log containers
- `aria-live="polite"` for updates
- `aria-label` for context
- `aria-atomic="false"` for performance

### Semantic HTML

- `<time>` for timestamps
- `<button>` for interactive elements
- `<header>` for app title

### Keyboard Navigation

- Tab order logical
- Focus indicators visible
- Button activation with Space/Enter

---

## Testing Strategy

### Unit Tests (Ready to implement)

```ts
// parseLogLine.test.ts
test("parses valid log line", () => {
  const result = parseLogLine("[01/01/2024 10:00:00] [INFO] [...] message");
  expect(result?.level).toBe("INFO");
});

// classifyLogSection.test.ts
test("classifies recent logs as current", () => {
  const now = new Date();
  const result = classifyLogSection(now, now);
  expect(result).toBe("current");
});
```

### Integration Tests (Manual)

- See TESTING_CHECKLIST.md

### E2E Tests (With Playwright)

```ts
test("loads logs on page load", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("text=Informações")).toBeVisible();
});
```

---

## Deployment

### Development

```bash
npm run dev              # Vite dev server + HMR
npm run type-check     # TypeScript check
npm run lint           # ESLint (if configured)
```

### Production

```bash
npm run build          # TypeScript → JavaScript → Bundled
npm run preview        # Vite preview (local prod simulation)
```

### Vercel

- `/` → Next.js / Static site
- `/api/contact` → Edge Function

---

## Environment Variables

None currently (all hardcoded in constants).

**To add:**

```ts
// .env.local
VITE_LOG_SERVER_URL=http://localhost:<port>/log.log
VITE_LOG_MONITOR_TIMEOUT_MS=30000
```

---

## Troubleshooting

| Issue                 | Cause              | Solution                                                     |
| --------------------- | ------------------ | ------------------------------------------------------------ |
| "Cannot GET /log.log" | Server not running | Start: `python -m http.server <port>` (use a port in `99xx`) |
| "Porta indisponível"  | Timeout after 30s  | Check server (port in `99xx`), increase timeout              |
| Blank page            | JavaScript error   | Open console (F12), check errors                             |
| Logs not streaming    | Wrong file path    | Verify `/log.log` exists and is readable                     |
| Contact cards fail    | GitHub API down    | Check internet, API rate limit                               |

---

## References

- [React 19 Docs](https://react.dev)
- [Vite Docs](https://vitejs.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)
- [Radix UI](https://www.radix-ui.com)
- [Tailwind CSS](https://tailwindcss.com)
- [Vercel Edge Functions](https://vercel.com/docs/edge-functions)

---

## Contributors

- **Claude (Anthropic)** - Backend utilities, architecture
- **Manus** - React UI components
- **Developer** - Integration, refactoring, optimization

---

## License

Same as parent project (see LICENSE file)

---

**Version:** 1.0.0 (Refactored)
**Last Updated:** 2024
**Status:** Production Ready ✅
