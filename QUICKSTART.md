# Quick Start Guide 🚀

## Setup Local (5 minutos)

### 1️⃣ Install

```bash
npm install
# Instala todas as dependências
```

### 2️⃣ Dev Server

```bash
# Terminal 1: App
npm run dev
# → Abre em http://localhost:5173

# Terminal 2: Log Server
cd client/public
python -m http.server 8000
# → Log server em http://localhost:8000
```

### 3️⃣ Abrir Navegador

- [x] Vá para `http://localhost:5173`
- [x] Se não houver logs, crie `client/public/log.log`

---

## Build & Deploy

### Build Local

```bash
npm run build
# → Saída em dist/
```

### Deploy Vercel (automático)

```bash
git push origin main
# → Deploy automático via GitHub
```

---

## Arquivos Importantes

### 📄 Ler Primeiro

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Arquitetura técnica

### 🧪 Antes de Mergear

1. **[TESTING_CHECKLIST.md](./TESTING_CHECKLIST.md)** - Guia de testes

### 💻 Para Developers

1. `client/src/constants/app.ts` - Config centralizada
2. `client/src/hooks/useLogMonitor.ts` - Custom hook
3. `client/src/lib/logParser.ts` - Parse logic
4. `client/src/lib/logFetcher.ts` - Fetch logic

---

## Estrutura Rápida

```
Home.tsx (60 linhas)
├── useLogMonitor() hook
├── LogContainer (info/warning/error)
├── HistoryView (seção histórico)
└── ContactFooter (footer)

useLogMonitor (130 linhas)
├── Usa logFetcher (streaming)
├── Usa logParser (parse + classify)
├── Gerencia estado (info/warning/error/history)
└── Cleanup on unmount

Constants (50 linhas)
├── URLs, timeouts
├── Mensagens (i18n ready)
├── Cores/estilos
└── Icon names
```

---

## Próximas Tarefas

### Imediato

- [ ] Executar checklist de testes (TESTING_CHECKLIST.md)
- [ ] Code review com team
- [ ] Deploy em staging

### Curto Prazo

- [ ] Unit tests (Jest)
- [ ] E2E tests (Playwright)
- [ ] CI/CD pipeline

### Futuro

- [ ] i18n (tradução - MESSAGES pronto)
- [ ] Dark mode
- [ ] WebSocket real-time

---

## Troubleshooting

| Problema                  | Solução                                           |
| ------------------------- | ------------------------------------------------- |
| Página em branco          | Abra console (F12), check logs                    |
| "Porta 8000 indisponível" | Inicie: `python -m http.server 8000`              |
| TypeScript error          | Rode: `npm run type-check`                        |
| Build falha               | Limpe: `rm -rf node_modules dist` → `npm install` |

---

## Contato

Para dúvidas:

1. Leia a documentação relevante (veja acima)
2. Consulte ARCHITECTURE.md para detalhes técnicos
3. Abra issue no GitHub com contexto

---

## Validação Final

```bash
# Tudo OK?
npm run type-check    # ✅ Zero errors
npm run build         # ✅ Success
npm run dev           # ✅ Running at localhost:5173
```

**Status:** ✅ **PRONTO PARA USAR**

---

**Que comece a diversão! 🎉**
