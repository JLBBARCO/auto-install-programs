# Testing Checklist - Programs Manager

## Pre-requisites

- [ ] Node.js 18+ installed
- [ ] Python 3.7+ installed (for log server)
- [ ] Repository cloned locally

## Unit Tests

### Step 1: TypeScript Compilation

```bash
npm run type-check  # or npx tsc --noEmit
```

**Expected:** Zero errors ✅

### Step 2: Build Verification

```bash
npm run build
```

**Expected Output:**

```checkbox
✓ 123 modules transformed
✓ built in 4.23s
```

## Integration Tests

### Step 3: Start Development Server

```bash
npm run dev
```

**Expected:**

- Browser opens at `http://localhost:5173`
- Home page loads without errors
- Three log containers visible: "Informações", "Avisos", "Erros"
- Contact footer loads

### Step 4: Start Log Server (Python)

In another terminal:

```bash
cd client/public
# Start a simple HTTP server on a port in the 99xx range (replace <port>):
python -m http.server <port>
```

**Expected:** Server running on `http://localhost:<port>` (the site will receive the chosen port via `?port=<port>`)

### Step 5: Log Server Simulation

Create `client/public/log.log` with test content:

```log
[01/01/2024 10:00:00] [SUCCESS] [pid:1234] [thread:1] System started
[01/01/2024 10:00:01] [INFO] [pid:1234] [thread:1] Processing task 1
[01/01/2024 10:00:02] [WARNING] [pid:1234] [thread:1] Memory usage high
[01/01/2024 10:00:03] [ERROR] [pid:1234] [thread:1] Failed to process item
[01/01/2024 10:00:04] [SUCCESS] [pid:1234] [thread:1] Retry successful
[01/01/2024 10:00:05] [SUCCESS] [pid:1234] [thread:1] End system
```

Refresh browser: `Ctrl+R`

### Step 6: Verify UI Updates

- [ ] "Informações" container shows SUCCESS logs (green border)
- [ ] "Avisos" container shows WARNING logs (yellow border)
- [ ] "Erros" container shows ERROR logs (red border)
- [ ] Auto-scroll works (scrolls to bottom automatically)
- [ ] Manual scroll pauses auto-scroll (button appears "Pausado")
- [ ] Histórico section appears with old logs (if any)

## Component Tests

### LogContainer Component

- [ ] Auto-scroll button shows when not at bottom
- [ ] Clicking manual scroll disables auto-scroll
- [ ] Scrolling to bottom re-enables auto-scroll
- [ ] Timestamps display in gray color
- [ ] Log level badges show correct color
- [ ] Hover effect works (background lightens)

### ContactFooter Component

- [ ] Footer loads with skeleton (while loading)
- [ ] Contact cards appear after loading
- [ ] Email, GitHub, LinkedIn icons display
- [ ] Links are clickable and open in new tab
- [ ] Fallback error message if API fails

### ErrorState Component

- [ ] If the configured log port (see `?port=NNNN`) is unreachable, error page shows
- [ ] "Tentar Novamente" button refreshes page
- [ ] "Abrir Servidor de Logs" opens the configured log server URL (localhost:`<port>`)
- [ ] Server URL shown in instructions

## Accessibility Tests

### Using Chrome DevTools

1. Open DevTools > Lighthouse
2. Run Accessibility audit
3. **Expected:** Score > 80

### Screen Reader Test

- [ ] Tab navigation works
- [ ] ARIA labels present on regions
- [ ] Log level announced by screen reader
- [ ] Button purposes clear

## Performance Tests

### Build Size

```bash
npm run build
```

**Expected:** Bundle < 500KB (optimized)

### Runtime Performance

1. Open DevTools > Performance
2. Record while loading logs
3. **Expected:**
   - FCP < 1.5s
   - LCP < 2.5s
   - No layout shifts

## Edge Cases

### Test 1: No Network

- [ ] Disable network (DevTools)
- [ ] Error state appears within 30s
- [ ] Manual refresh works

### Test 2: Slow Connection

- [ ] Throttle to 3G (DevTools)
- [ ] Skeletons show during loading
- [ ] UI responsive (no freezes)

### Test 3: Large Log Volume

- [ ] Paste 1000+ log lines
- [ ] Container still responsive
- [ ] Auto-scroll works smoothly

### Test 4: Special Characters

Add to log.log:

```log
[01/01/2024 10:00:00] [INFO] [pid:1234] [thread:1] Ação/Reação: Tudo certo! 🎉
```

- [ ] Displays correctly (no encoding issues)

## Code Quality Checks

### ESLint (if configured)

```bash
npm run lint
```

**Expected:** Zero warnings

### Type Safety

```bash
npx tsc --strict --noEmit
```

**Expected:** Zero errors

### Dead Code

```bash
grep -r "console.log" client/src/
```

**Expected:** Only in development files

## Deployment Readiness

### Production Build

```bash
npm run build
npm run preview
```

- [ ] Opens without errors
- [ ] All features work
- [ ] No console errors

### Vercel Deployment

- [ ] `api/contact.js` deploys correctly
- [ ] API endpoint responds with contact data
- [ ] CORS headers present

## Final Sign-Off

- [ ] All TypeScript checks pass
- [ ] All components render correctly
- [ ] All features tested and working
- [ ] Accessibility compliant
- [ ] Performance acceptable
- [ ] No console errors or warnings
- [ ] Ready for production

---

## Test Results

| Test          | Status | Notes                |
| ------------- | ------ | -------------------- |
| TypeScript    | ✅     | Zero errors          |
| Build         | ✅     | Success              |
| Dev Server    | ✅     | Running              |
| UI Components | 🔄     | Awaiting manual test |
| Accessibility | 🔄     | Awaiting audit       |
| Performance   | 🔄     | Awaiting measurement |
| Edge Cases    | 🔄     | Awaiting test        |
| Production    | 🔄     | Ready to test        |

---

## Known Limitations

- Log server must be running on a reachable port in the `9900–9999` range or the port passed to the site via `?port=NNNN`
- 30-second timeout for connection
- 60-second tolerance for "current" vs "history" logs
- Contact API requires GitHub availability (or Vercel endpoint)

## Support

For issues:

1. Check console (F12)
2. Verify the local log server (port in the `99xx` range) is running
3. Check network tab for failed requests
4. Review browser compatibility
