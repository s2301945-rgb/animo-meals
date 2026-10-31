export default function StagingBanner() {
  return import.meta.env.VITE_APP_ENV === "staging" ? (
    <aside className="staging-banner" role="note">
      STAGING · Test environment — changes here do not affect live menus.
    </aside>
  ) : null;
}

export async function verifyStagingEnvironment(api, signal) {
  if (import.meta.env.VITE_APP_ENV !== "staging") return;
  const response = await fetch(`${api}/api/environment`, { signal });
  if (!response.ok || (await response.json()).environment !== "staging") {
    throw new Error(
      "Staging is not connected to its isolated backend. Check the staging configuration.",
    );
  }
}
