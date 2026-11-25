# Maven

## Q: You have a dependency conflict (e.g. two versions of Jackson). How do you find and fix it?
### Solution
Maven resolves conflicts with **"nearest wins"**: the version closest to your POM in the dependency tree wins; when depths tie, the first declaration wins. That can silently pick an old version and cause `NoSuchMethodError` at runtime.

Find it: `mvn dependency:tree -Dverbose -Dincludes=com.fasterxml.jackson.core`.
Fix it:
- Pin versions centrally in `<dependencyManagement>`, ideally by importing a **BOM** (`jackson-bom`, `spring-boot-dependencies`, AWS SDK BOM).
- `<exclusions>` on the transitive dependency that drags in the wrong version.
- Enforce: the `maven-enforcer-plugin` with `dependencyConvergence` / `requireUpperBoundDeps` fails the build on conflicts.

## Q: Explain the Maven lifecycle and the difference between `install` and `deploy`.
### Solution
The default lifecycle phases run in order: `validate → compile → test → package → verify → install → deploy`. Running a phase runs all the earlier ones too. Plugin goals are bound to phases (e.g. surefire `test` to `test`, failsafe integration tests to `integration-test`/`verify`).

- `install` copies the artifact into your **local** `~/.m2/repository`, so other local builds can use it.
- `deploy` uploads it to a **remote** repository (Nexus/Artifactory/CodeArtifact) configured in `<distributionManagement>`, for other teams and CI.

Other useful commands: `-pl module -am` builds one module plus the modules it depends on; `-T 1C` builds in parallel; `-o` runs offline; `mvn versions:display-dependency-updates` lists available upgrades.
