# Administrator dashboard

The visitor site is public. Open `/#admin`, or use the **Administrator** link in
the footer, to manage records after signing in with the configured Supabase Auth
account. Database passwords and Supabase dashboard passwords are not app logins.

## Local configuration

1. In Supabase **Authentication → Users**, create the administrator's account
   and confirm its email. Keep its password private.
2. Set `SUPABASE_URL` and the account's `ADMIN_USER_ID` in ignored `backend/.env`.
   The user ID is the Auth account UUID, not an email address or database user.
3. In **Project Settings → API Keys**, copy the existing **Publishable key**.
   Do not use a secret/service-role key and do not create another key unnecessarily.
4. From `backend`, run the optional private setup window:

   ```powershell
   .venv/Scripts/python.exe -m app.configure_admin
   ```

   Paste the publishable key there. It checks the configured project's Auth
   settings over HTTPS and stores the key only in ignored `backend/.env`.
   It never asks for or saves the administrator password. Alternatively, configure
   `SUPABASE_PUBLISHABLE_KEY` directly in the private environment file.
5. Restart the backend. Environment variables override `.env`; remove any
   temporary empty Auth variable overrides before starting the real preview.
6. Open `/#admin` and sign in. The backend verifies the access token with Supabase
   and grants writes only to the configured user ID. Other accounts cannot edit.

For hosted use, configure these same settings privately on the backend host.
The frontend needs only `VITE_API_BASE_URL`. Hosting configuration and deployment
are separate steps; local setup does not update Render or Vercel.

## Use the dashboard

- **Shops:** add names/locations, edit existing shops, or delete empty shops.
- **Menu items:** add a meal and select its shop, price, category, optional
  description and availability. Edit those fields later as information changes.
- **Filter by shop:** review only that shop's items; new items default to the
  selected shop. Search further narrows the list.
- **Delete:** first shows a confirmation. Cancelling keeps the record. A shop
  with menu items cannot be deleted; move/delete its items first.
- **Visitor view:** refresh it to see saved changes. After a failed network
  request, refresh the admin list before retrying so you do not create duplicates.

Names/locations cannot be blank or contain only spaces. Prices must be greater
than zero and at most PHP 10,000, with no more than two decimal places. Server
validation is authoritative. A failed save keeps the form available for correction.

## Sessions and availability

Access tokens are kept in component memory, not localStorage/sessionStorage.
Reloading, leaving the admin page, signing out, or reaching token expiry requires
sign-in again. Invalid or unauthorized sessions cannot write. Password fields
are cleared after a sign-in attempt.

"Listed as available" is an administrator-maintained label. The app does not
detect live stock. Regular meals and verified prices should be maintained; actual
availability can vary at the shop.

## Data and verification

The selected-shop local preview has five real shop records and zero menu items.
Do not attach fictional dishes or prices to these shops while the dataset is
pending. `python -m app.shop_catalog` adds missing shop records without adding
meals or overwriting later location edits.

Browser CRUD verification uses separate disposable SQL tables and fictional
test shops. Only Supabase's identity responses are mocked for that test; writes,
reads, validation, relationships and delete conflicts use the real FastAPI routes.
Real-account login must also be checked after project-key configuration.
