# Agent Guidelines for DeadPartyMedia

## Commands

### Frontend (Next.js)

- **Build**: `pnpm build` (turbo build across workspace)
- **Dev**: `pnpm dev` (turbo dev with turbopack)
- **Lint**: `pnpm lint` (turbo lint with ESLint)
- **Format**: `pnpm format` (Prettier on ts,tsx,md files)
- **Typecheck**: `cd apps/web && pnpm typecheck` (tsc --noEmit)
- **Single test**: No test framework configured yet

### Backend (Django)

- **Dev**: `pnpm backend:dev` (Django dev server)
- **Migrate**: `pnpm backend:migrate` (run migrations)
- **Make migrations**: `pnpm backend:makemigrations` (create migrations)
- **Shell**: `pnpm backend:shell` (Django shell)
- **Collect static**: `pnpm backend:collectstatic` (collect static files)
- **Create superuser**: `pnpm backend:createsuperuser` (create admin user)

## Code Style

### Frontend (TypeScript/React)

- **TypeScript**: Strict mode enabled, noUncheckedIndexedAccess
- **Imports**: ES modules, absolute paths with @ aliases (@/components, @workspace/ui)
- **React**: Functional components with hooks, no prop-types (TypeScript)
- **Styling**: Tailwind CSS with shadcn/ui components, class-variance-authority
- **Naming**: camelCase variables/functions, PascalCase components
- **Error handling**: TypeScript catches most issues, use try/catch for async operations
- **Formatting**: Prettier with ESLint integration

### Backend (Django/Python)

- **Python**: 3.11+, UV package manager
- **Django**: 5.1+, strict settings, PostgreSQL
- **Imports**: Standard Python imports, absolute imports within Django
- **Models**: PascalCase class names, snake_case field names
- **Views**: Class-based views with DRF, descriptive method names
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Error handling**: Try/except blocks, proper exception handling
- **Formatting**: Black, isort for import sorting
