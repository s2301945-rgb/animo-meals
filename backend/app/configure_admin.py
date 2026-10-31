"""Private local setup window for the Supabase public key; never asks for a password."""
import argparse
import json
from pathlib import Path
import threading
import tkinter as tk
from tkinter import ttk

import httpx
from dotenv import set_key
from pydantic import SecretStr

from app.auth import auth_config
from app.config import BACKEND_DIR, settings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--status-file', type=Path)
    args = parser.parse_args()
    root = tk.Tk()
    root.title('AnimoMeals — Connect admin sign-in')
    root.geometry('670x370')
    root.resizable(False, False)
    root.configure(background='#f5f7f1')
    frame = ttk.Frame(root, padding=24)
    frame.pack(fill='both', expand=True)
    ttk.Label(frame, text='Connect your administrator account',
              font=('Segoe UI', 16, 'bold')).pack(anchor='w', pady=(0, 14))
    ttk.Label(frame, text=(
        'In Supabase: Project Settings → API Keys → Publishable key.\n'
        'Copy the existing key, then paste it below. Do not create a new key.\n'
        'This field is NOT for your password or a secret/service-role key.'
    ), wraplength=600, font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 15))
    entry = ttk.Entry(frame, show='*', width=77)
    entry.pack(fill='x', pady=(0, 15))
    message = tk.StringVar(value='Your password stays private. Only the public project key is saved locally.')
    status = ttk.Label(frame, textvariable=message, wraplength=600)
    status.pack(anchor='w', pady=(0, 12))

    def finish(success, text):
        message.set(text)
        entry.delete(0, tk.END)
        entry.configure(state='normal' if not success else 'disabled')
        button.configure(state='normal' if not success else 'disabled')
        if success and args.status_file:
            args.status_file.write_text(json.dumps({'status': 'configured'}), encoding='utf-8')

    def verify(value):
        try:
            settings.supabase_publishable_key = SecretStr(value)
            url, key = auth_config()
            response = httpx.get(f'{url}/auth/v1/settings', headers={'apikey': key}, timeout=20)
            if response.status_code != 200:
                raise ValueError('Public key was rejected')
            set_key(BACKEND_DIR / '.env', 'SUPABASE_PUBLISHABLE_KEY', value)
        except Exception:
            root.after(0, finish, False,
                       'Could not verify the key. Use the publishable key from this Supabase project and try again. No new key was saved.')
            return
        root.after(0, finish, True,
                   'Connected! The public key was verified and saved in ignored backend/.env. You can close this window and tell Codex: connected.')

    def save():
        value = entry.get().strip()
        if not value.startswith('sb_publishable_'):
            message.set('Use the Publishable key beginning sb_publishable_. Do not enter a password or secret key.')
            entry.delete(0, tk.END)
            return
        entry.configure(state='disabled')
        button.configure(state='disabled')
        message.set('Verifying your public project key…')
        threading.Thread(target=verify, args=(value,), daemon=True).start()

    button = ttk.Button(frame, text='Verify and save public key', command=save)
    button.pack(anchor='w')
    entry.focus()
    root.mainloop()


if __name__ == '__main__':
    main()
