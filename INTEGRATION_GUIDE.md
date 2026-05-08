# Guia de Integração: Backend Claude + Frontend Manus

## Resumo Executivo

Este documento descreve como os arquivos gerados pelo Claude (backend em `files/`) foram integrados ao projeto frontend do Manus. A integração cria um fluxo bidirecional limpo:

1. **Frontend** lê logs em tempo real via async generator (streaming nativo)
2. **API de Contato** centralizada em Vercel Edge Function com cache de 1 hora
3. **Lógica de classificação** (current vs history) no browser, validada por contrato com o backend

---

## Arquivos Adicionados

### `client/src/lib/logParser.ts`
Ported from `files/logParser.js` com tipagem TypeScript completa.

**Responsabilidades:**
- Parse de linhas: `[DD/MM/YYYY HH:MM:SS] [LEVEL] [pid:...] [thread:...] [caller:...] message`
- Classificação de seção: se `(siteLoadedAt - lineTimestamp) ≤ 60s` → "current", senão "history"
- Bucketização de nível: WARNING → warning, ERROR → error, resto → info

**Tipos Exportados:**
```typescript
export type LogLevel = "INFO" | "SUCCESS" | "WARNING" | "ERROR";
export type LogSection = "current" | "history";

export interface ParsedLogLine {
  timestamp: Date;
  timestampRaw: string; // formato original para exibição
  level: LogLevel;
  pid: string | null;
  thread: string | null;
  caller: string | null;
  message: string;
}

export function parseLogLine(raw: string): ParsedLogLine | null
export function classifyLogSection(lineTimestamp: Date, siteLoadedAt: Date): LogSection
export function bucketLogLevel(level: LogLevel): "info" | "warning" | "error"
```

### `client/src/lib/logFetcher.ts`
Ported from `files/logFetcher.js` com suporte a AbortSignal para cancelamento limpo.

**Responsabilidades:**
- Streaming fetch com async generator
- Decoding incremental de UTF-8
- Handling de buffers incompletos (quebra em `\n` ou `\r\n`)

**Assinatura:**
```typescript
export async function* fetchLogStream(
  url: string,
  options?: { signal?: AbortSignal }
): AsyncGenerator<string>
```

### `api/contact.js`
Criado como Edge Function Vercel com fallback bidirecional.

**Responsabilidades:**
- Fetch do `contact.json` do portfólio
- Cache CDN por 1 hora com revalidação em background por 5 min
- CORS aberto para consumo do browser

**Endpoint:**
```
GET /api/contact
Returns: { cards: [ { name, iconName, url }, ... ] }
```

---

## Arquivos Modificados

### `client/src/pages/Home.tsx`
**De:** Polling HTTP cada 500ms → Parse regex local  
**Para:** Async generator streaming com timeout centralizado

**Fluxo:**
1. Captura `loadTime` ao montar o componente
2. Abre `AbortController` com timeout de 30s
3. Itera sobre `fetchLogStream()` linha por linha
4. Para cada linha:
   - Parse com `parseLogLine()`
   - Classifica com `classifyLogSection(parsed.timestamp, loadTime)`
   - Faz append em bucket correspondente (info/warning/error/history)
5. Aborts ao receber "End system" ou timeout
6. Retorna `<ErrorState />` se erro ou timeout

**Impacto de Compatibilidade:**
- ✅ Mesmos estados: infoLogs, warningLogs, errorLogs, historyLogs
- ✅ Mesmos componentes: LogContainer, HistoryView
- ✅ Mesma interface LogEntry
- ⚠️ Diferente: Não mais busca a porta 8000 via `/logs` (aquele endpoint foi removido)

### `client/src/components/LogContainer.tsx`
**De:** Props `logs + level` separadas  
**Para:** Props `entries` unificadas + estilos inline gerados

**Mudanças:**
- Removido cálculo de cor no props → agora derive via `getLevelStyles()`
- Suporte a horizontal scroll (logs longos em linha única)
- Badges de nível ao lado de cada log (coloridas)
- Classes Tailwind mais específicas (emerald/amber/red/sky)

**Impacto:**
- ✅ Auto-scroll continua funcionando
- ✅ Pause ao scroll manual continua
- ✅ Sem breaking changes se chamador passar `entries` em vez de `logs`

### `client/src/components/ContactFooter.tsx`
**De:** Fetch direto do GitHub  
**Para:** Fallback com tentativa de `/api/contact` primeiro

**Mudanças:**
- Loop de endpoints: `["/api/contact", "https://raw.githubusercontent.com/..."]`
- Cada endpoint tenta fetch em sequência
- Se um falhar, tenta o próximo
- Styling: Pills ao invés de ícones isolados (agora mostra o nome do contato)

**Impacto:**
- ✅ Em dev local: usa `/api/contact` (pode falhar, cai para GitHub)
- ✅ Em produção Vercel: usa `/api/contact` com cache
- ✅ Sempre tem fallback para GitHub raw

### `client/src/components/ErrorState.tsx`
**Pequena atualização:**
- Mensagem atualizada: "Conexão não estabelecida" → "Porta 8000 indisponível"
- Instruções: "Verifique se programa está rodando" → "Faça refresh ou reexecute"

### `client/src/components/HistoryView.tsx`
**Ajuste visual:**
- Suporte a horizontal scroll como LogContainer
- Classe `min-w-max` para preservar espaços em logs longos

### `vercel.json`
**Mudança:**
- Removida função `api/logs.js` (o streaming era impossível de Vercel para localhost)
- Mantida função `api/contact.js` com maxDuration=10s

---

## Contrato de Integração

### Browser → Port 8000 (Python App)

```
GET http://localhost:8000/log.log
Headers: Accept: text/plain

Response (streaming):
[DD/MM/YYYY HH:MM:SS] [LEVEL] [pid:...] [thread:...] [caller:...] message
[DD/MM/YYYY HH:MM:SS] [LEVEL] [pid:...] [thread:...] [caller:...] message
...
[DD/MM/YYYY HH:MM:SS] [INFO] End system
```

### Browser → Vercel CDN

```
GET /api/contact
Returns:
{
  "cards": [
    { "name": "Email", "iconName": "email", "url": "mailto:..." },
    { "name": "GitHub", "iconName": "github", "url": "https://github.com/..." },
    { "name": "LinkedIn", "iconName": "linkedin", "url": "https://linkedin.com/..." }
  ]
}
```

---

## Validação Manual

### Teste 1: Parser
```typescript
import { parseLogLine, classifyLogSection } from "@/lib/logParser";

const raw = "[01/06/2026 12:30:45] [SUCCESS] [pid:1234] [thread:Main] System ready";
const parsed = parseLogLine(raw);
// { timestamp: Date(2026,5,1,12,30,45), level: "SUCCESS", message: "System ready", ... }

const siteLoadedAt = new Date("2026-06-01T12:30:50");
const section = classifyLogSection(parsed.timestamp, siteLoadedAt);
// "current" (porque 5s de diferença ≤ 60s)
```

### Teste 2: Streaming Fetch
```typescript
import { fetchLogStream } from "@/lib/logFetcher";

const controller = new AbortController();
for await (const line of fetchLogStream("http://localhost:8000/log.log", {
  signal: controller.signal
})) {
  console.log(line); // cada linha do arquivo
  if (line.toLowerCase().includes("end system")) {
    controller.abort();
  }
}
```

### Teste 3: ContactFooter Fallback
```typescript
// Primeiro tenta /api/contact (Vercel)
// Se falhar (404, network error), tenta GitHub raw
// Se ambos falharem, exibe erro "Erro ao carregar contatos"
```

---

## Impacto de Deploy

### Local Dev (`npm run dev`)
- ✅ Frontend ouve na porta 3000
- ✅ Browser acessa `http://localhost:8000/log.log` diretamente
- ✅ `/api/contact` retorna 404 (não existe endpoint local), cai para GitHub
- ✅ Sem mudanças no workflow

### Vercel Production
- ✅ Frontend + server API bundled e deployado
- ✅ `/api/contact` Edge Function ativa com cache CDN
- ❌ Browser **não consegue** acessar `localhost:8000` do Python app (CORS, firewall)
  - Solução: usuário roda Python app em máquina local, Vercel acessa via proxy reverso configurado no programa (não neste projeto)

---

## Checklist de Validação

- [ ] TypeScript compila sem erros (`npm run check`)
- [ ] Vite dev server roda (`npm run dev`)
- [ ] Home page carrega sem JS errors (DevTools Console)
- [ ] Parser aceita linhas válidas e rejeita inválidas (teste manual)
- [ ] ContactFooter carrega e fallback funciona (inspecionar Network)
- [ ] Logs aparecem em 3 containers (Info, Avisos, Erros)
- [ ] Auto-scroll e pause manual funcionam
- [ ] Histórico aparece se houver logs antigos
- [ ] Timeout de 30s encerra corretamente se porta 8000 não abrir

---

## Arquivos Remanescentes da Pasta `files/`

Os arquivos em `files/` eram templates para backend:
- `files/logFetcher.js` → migrado para `client/src/lib/logFetcher.ts`
- `files/logParser.js` → migrado para `client/src/lib/logParser.ts`
- `files/contact.js` → migrado para `api/contact.js` (Vercel Edge Function)
- `files/logs.js` → descartado (SSE impossível em Vercel para localhost)
- `files/vercel.json` → merged em `vercel.json`

**Ação recomendada:** Manter `files/` para referência histórica, mas não mais necessário em produção.
