# UI Modernization + Feature Additions

Complete redesign of the Inventory Management System UI with a premium dark theme and
several missing features added across all views.

## Design System

| Token | Value | Usage |
|---|---|---|
| `bg` | `#08080F` | Window backgrounds |
| `sidebar` | `#0C0C1A` | Side navigation |
| `card` | `#131325` | Cards, table rows |
| `card_alt` | `#1C1C35` | Alternate rows, inputs |
| `primary` | `#6C63FF` | CTA buttons, accents |
| `secondary` | `#00D4AA` | Positive values, success |
| `danger` | `#FF6B6B` | Delete/error actions |
| `warning` | `#FFB347` | Low stock, pending |
| `text` | `#E8E8F0` | Primary text |
| `text_dim` | `#7A7A9A` | Labels, hints |

Font: **Segoe UI** throughout (available on all Windows machines).

---

## New Features Added

| Feature | Where |
|---|---|
| Search / filter bar | Inventory, Orders, Users, History |
| Edit inventory item dialog | Inventory (admin) |
| Delete inventory item | Inventory (admin) |
| Low-stock alerts on dashboard | Dashboard (cards + alert strip) |
| Total revenue card | Dashboard |
| Recent-orders quick view | Dashboard |
| Mark order Paid / Pending | Orders page |
| Delete user | Users page (admin) |
| Export to CSV | Inventory, Orders, History |
| Cart item merge (add same item again) | Shop |
| Revenue strip on dashboard | Dashboard |
| Active sidebar indicator | All pages |
| Color-coded status in tables | Orders, History |

---

## Proposed Changes

### utils.py — update `add_graphs`

#### [MODIFY] [utils.py](file:///c:/Gravity/Inventory-Management-System-Customtinkter/utils.py)
- Add `bar_pos=(30, 10)` and `pie_pos=(760, 10)` parameters so the dashboard
  can control where charts land inside a correctly-sized frame.
- Tighten up the figure sizes slightly so they fit the new layout.
- Update facecolors to match the new dark palette (`#131325`).

---

### login.py — complete rewrite

#### [MODIFY] [login.py](file:///c:/Gravity/Inventory-Management-System-Customtinkter/login.py)
- **Split-panel layout** — 440 px dark left panel + 440 px form panel.
- Left panel: app icon (📦), name "InvenTrack", tagline, feature bullets, accent strips at top/bottom.
- Right panel: clean stacked form with uppercase field labels, styled entries, primary CTA button.
- Login ↔ Register toggling rebuilds only the form (no full window rebuild).
- **No bg2.jpg dependency** — all rendered with CTk/tkinter widgets.
- Public API unchanged: `self.window`, `self.user`, `self.login_window()`, `self.register_window()`.

---

### menu.py — complete rewrite

#### [MODIFY] [menu.py](file:///c:/Gravity/Inventory-Management-System-Customtinkter/menu.py)
- **Sidebar** (220 px): logo, nav buttons with PNG icons + active highlight, user badge, logout.
- **Content area**: `_clear_content()` rebuilds each page fresh; no leftover widgets.
- **Dashboard**: 4 stat cards (Sales Today, Total Orders, Products, Low Stock) + Revenue strip + optional low-stock pill strip + charts.
- **Inventory**: search bar + low-stock checkbox filter + table + Add / Edit / Delete (admin) + CSV export.
- **Orders**: search + table with color-coded status + Mark Paid / Mark Pending + CSV export.
- **Users** (admin): search + table + Delete User.
- **Shop**: improved cart — Add Item dialog with product info preview, quantity validation, duplicate-item merge, running total label.
- **History**: search + table + CSV export.
- All dialogs use a shared `_dialog()` helper.
- `self.logout` flag still set correctly for `main.py`.

---

## Verification Plan

### Manual Verification
- Run `python main.py` and confirm the login screen renders without bg2.jpg.
- Log in as Admin; check all 4 pages (Dashboard, Inventory, Orders, Users).
- Log in as a regular user; check Dashboard, Inventory, Shop, History.
- Test search bars filter live.
- Test Add / Edit / Delete product.
- Test Mark Paid / Pending on orders.
- Test CSV export opens a save dialog.
- Test logout → login flow loops correctly.
