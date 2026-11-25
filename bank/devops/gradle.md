# Gradle

## Q: Gradle vs Maven: why would a team switch, and what makes Gradle fast?
### Solution
Gradle builds are code (Groovy or **Kotlin DSL**), so custom logic is easy, while Maven is declarative XML with a fixed lifecycle. Gradle is faster because of:
- **Incremental builds:** tasks declare inputs and outputs, and up-to-date tasks are skipped.
- **Build cache** (local/remote): reuses task outputs across machines and CI.
- The **Gradle Daemon** keeps a warm JVM between builds.
- **Configuration cache** and parallel project execution.

Trade-offs: more flexibility means more ways to make a build unmaintainable; Maven's rigidity is predictable. For large multi-module repos Gradle usually wins on build time.

## Q: What's the difference between `implementation`, `api`, `compileOnly` and `runtimeOnly`?
### Solution
- `implementation`: on your compile classpath but **not exposed** to consumers of your library. Changing it doesn't force consumers to recompile. This is the default choice.
- `api` (needs the `java-library` plugin): exposed transitively. Use it when the dependency's types appear in your public API.
- `compileOnly`: needed only at compile time and not packaged (e.g. Lombok, annotations provided by the runtime).
- `runtimeOnly`: needed only at runtime (e.g. a JDBC driver, an SLF4J binding).
- `testImplementation`: test-only dependencies.

Version alignment: use `platform(...)` BOMs and **version catalogs** (`libs.versions.toml`); resolve conflicts with `dependencyInsight --dependency jackson-databind`.
