# Dependency Injection (Dagger, Guice)

## Q: Compare Spring DI, Guice and Dagger.
### Solution
| | Spring | Guice | Dagger 2 |
|---|---|---|---|
| Wiring | Runtime, reflection + classpath scanning | Runtime, reflection, explicit `Module`s | **Compile time**, annotation processor generates code |
| Errors found | At startup | At injector creation | **At compile time** |
| Startup cost | Highest | Medium | Near zero |
| Scope | Full framework | DI only | DI only |

Dagger suits Android, Lambda and CLI tools where startup matters and you want missing bindings to be compile errors. Guice is lightweight DI for non-Spring services. Spring wins on ecosystem. All of them use JSR-330 annotations (`@Inject`, `@Singleton`, `@Named`).

## Q: Constructor vs field injection: which do you use, and how do you handle circular dependencies?
### Solution
**Constructor injection:** dependencies are explicit, fields can be `final` (immutable), the object is never half-built, and it's testable without a container (`new Service(mockRepo)`). A long constructor is also a useful smell that the class does too much. Field injection hides dependencies and needs reflection to test.

**Circular dependencies:** with constructor injection Spring fails fast (and Boot 2.6+ forbids cycles by default). That's a good thing, because a cycle usually signals a design problem. Fix it by extracting the shared logic into a third bean, using events, or, as a last resort, injecting `ObjectProvider<T>`/`@Lazy` (in Guice, a `Provider<T>`) to defer the lookup.
