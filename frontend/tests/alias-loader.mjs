// Minimal ESM loader to map Vite-style alias '@client/*' to our local test stub.
// This allows Node's test runner to import components that reference '@client/index'.
export async function resolve(specifier, context, defaultResolve) {
  if (specifier === '@client' || specifier.startsWith('@client/')) {
    const url = new URL('./stubs/client.mjs', import.meta.url);
    return { url: url.href, shortCircuit: true };
  }
  return defaultResolve(specifier, context, defaultResolve);
}
