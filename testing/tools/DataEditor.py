# -*- coding: utf-8 -*-
import json
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ----------------------------
# SCHEMAS  (used for validation & Fix Schema)
# Runtime copies live on the App instance so the Schema Editor can mutate them.
# These module-level dicts are only used as the initial seed.
# ----------------------------

_INITIAL_SCHEMAS = {
    "foods": {
        "id": str,
        "display_name": str,
        "ingredients": list,
        "required_customer_permits": list,
        "required_cafe_licenses": list,
    },
    "religions": {
        "id": str,
        "display_name": str,
        "prohibited_tags": list,
        "lore": str,
    },
    "nationalities": {
        "id": str,
        "display_name": str,
        "preferred_tags": list,
        "prohibited_tags": list,
        "social_faux_pas_tags": list,
        "lore": str,
    },
}

_INITIAL_SPECIES_SCHEMA = {
    "display_name": str,
    "forbidden_tags": list,
    "required_tags": list,
    "description": str,
}

# ingredients schema is implicit (display_name:str, tags:list) – stored inline
_INITIAL_INGREDIENTS_SCHEMA = {
    "display_name": str,
    "tags": list,
}

def _initial_defaults():
    """Return a fresh DEFAULTS dict derived from the initial schemas."""
    return {
        "foods": {
            "id": "new_food",
            "display_name": "",
            "ingredients": [],
            "required_customer_permits": [],
            "required_cafe_licenses": [],
        },
        "ingredients": {"display_name": "", "tags": []},
        "religions": {
            "id": "new_religion",
            "display_name": "",
            "prohibited_tags": [],
            "lore": "",
        },
        "nationalities": {
            "id": "new_nationality",
            "display_name": "",
            "preferred_tags": [],
            "prohibited_tags": [],
            "social_faux_pas_tags": [],
            "lore": "",
        },
        "species": {
            "display_name": "",
            "forbidden_tags": [],
            "required_tags": [],
            "description": "",
        },
    }

LIST_TABS = {"foods", "religions", "nationalities"}
DICT_TABS = {"ingredients", "species"}
TAB_NAMES = ["foods", "ingredients", "religions", "nationalities", "species"]

# Maps tab name → the schema dict key to use for validation
_ALL_SCHEMA_KEYS = list(_INITIAL_SCHEMAS.keys()) + ["ingredients", "species"]

# ----------------------------
# LOAD / SAVE JSON
# ----------------------------

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Failed to load {path}: {e}")
        return None


def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent="\t", ensure_ascii=False)
        return True
    except Exception as e:
        messagebox.showerror("Save Error", str(e))
        return False

# ----------------------------
# VALIDATION
# ----------------------------

def validate_foods_ingredients(foods, ingredients):
    errors = []
    ing_set = set(ingredients.keys())
    for food in foods.get("foods", []):
        for ing in food.get("ingredients", []):
            if ing not in ing_set:
                errors.append(f"[foods] '{food.get('id')}' uses unknown ingredient '{ing}'")
    return errors


def validate_list_schema(data_list, schema, tab_name):
    errors = []
    for i, item in enumerate(data_list):
        label = item.get("id", f"#{i}")
        for key, expected_type in schema.items():
            if key not in item:
                errors.append(f"[{tab_name}] '{label}' missing field '{key}'")
                continue
            if not isinstance(item[key], expected_type):
                actual = type(item[key]).__name__
                errors.append(
                    f"[{tab_name}] '{label}' field '{key}' "
                    f"expected {expected_type.__name__}, got {actual}"
                )
    return errors


def validate_dict_schema(data_dict, schema, tab_name):
    errors = []
    for key, item in data_dict.items():
        if not isinstance(item, dict):
            errors.append(f"[{tab_name}] '{key}' is not an object")
            continue
        for field, expected_type in schema.items():
            if field not in item:
                errors.append(f"[{tab_name}] '{key}' missing field '{field}'")
                continue
            if not isinstance(item[field], expected_type):
                actual = type(item[field]).__name__
                errors.append(
                    f"[{tab_name}] '{key}' field '{field}' "
                    f"expected {expected_type.__name__}, got {actual}"
                )
    return errors

# ----------------------------
# APP
# ----------------------------

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Monster Café Data Editor")

        self.folder = None
        self.dirty  = False

        self.data = {
            "foods":         {"foods": []},
            "ingredients":   {},
            "religions":     {"religions": []},
            "nationalities": {"nationalities": []},
            "species":       {},
        }

        # --- runtime schema copies (mutable via Schema Editor) ---
        self.schemas            = {k: dict(v) for k, v in _INITIAL_SCHEMAS.items()}
        self.species_schema     = dict(_INITIAL_SPECIES_SCHEMA)
        self.ingredients_schema = dict(_INITIAL_INGREDIENTS_SCHEMA)
        self.defaults           = _initial_defaults()

        self.current_tab   = "foods"
        self.current_index = None
        # fields: ordered list of [key, entry_widget, was_list]
        self.field_rows = []

        self.build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ================================================================
    # UI BUILD
    # ================================================================

    def build_ui(self):
        toolbar = tk.Frame(self.root, bd=1, relief="raised")
        toolbar.pack(fill="x")

        tk.Button(toolbar, text="📂 Open Folder", command=self.select_folder).pack(side="left", padx=2, pady=2)
        tk.Button(toolbar, text="💾 Save All",    command=self.save_all).pack(side="left", padx=2, pady=2)
        tk.Button(toolbar, text="🔍 Validate",    command=self.refresh_validation).pack(side="left", padx=2, pady=2)
        tk.Button(toolbar, text="⚙ Schemas",     command=self.open_schema_editor).pack(side="left", padx=2, pady=2)

        self.title_label = tk.Label(toolbar, text="No folder loaded", fg="grey")
        self.title_label.pack(side="left", padx=8)

        self.tabs   = ttk.Notebook(self.root)
        self.frames = {}

        for name in TAB_NAMES:
            frame = tk.PanedWindow(self.tabs, orient=tk.HORIZONTAL)
            self.tabs.add(frame, text=name)
            self.frames[name] = frame

        self.tabs.pack(fill="both", expand=True)
        self.tabs.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        for name in TAB_NAMES:
            self._build_tab(name)

        self.validation = tk.Text(
            self.root, height=8, bg="#111", fg="#00ff88",
            font=("Consolas", 9), state="disabled"
        )
        self.validation.pack(fill="x")

    def _build_tab(self, name):
        frame = self.frames[name]

        # ---- LEFT panel ----
        left = tk.Frame(frame, width=220)
        frame.add(left, minsize=180)

        btn_frame = tk.Frame(left)
        btn_frame.pack(fill="x")
        tk.Button(btn_frame, text="➕ Add",        command=lambda n=name: self.add_item(n)).pack(side="left", fill="x", expand=True)
        tk.Button(btn_frame, text="🗑 Delete",     command=lambda n=name: self.delete_item(n)).pack(side="left", fill="x", expand=True)
        tk.Button(btn_frame, text="🧹 Fix Schema", command=lambda n=name: self.fix_schema(n)).pack(side="left", fill="x", expand=True)

        # move-up / move-down buttons
        move_frame = tk.Frame(left)
        move_frame.pack(fill="x")
        tk.Button(move_frame, text="▲ Move Up",   command=lambda n=name: self.move_item(n, -1)).pack(side="left", fill="x", expand=True)
        tk.Button(move_frame, text="▼ Move Down", command=lambda n=name: self.move_item(n, +1)).pack(side="left", fill="x", expand=True)

        # filter
        filter_var = tk.StringVar()
        filter_entry = tk.Entry(left, textvariable=filter_var)
        filter_entry.pack(fill="x", padx=2, pady=2)
        filter_entry.insert(0, "🔎 filter...")
        filter_entry.bind("<FocusIn>",  lambda e, fe=filter_entry: fe.delete(0, tk.END) if fe.get().startswith("🔎") else None)
        filter_entry.bind("<FocusOut>", lambda e, fe=filter_entry: fe.insert(0, "🔎 filter...") if not fe.get() else None)
        filter_var.trace_add("write", lambda *a, n=name, fv=filter_var: self._apply_filter(n, fv.get()))

        listbox = tk.Listbox(left, selectmode="browse", activestyle="dotbox")
        scroll  = tk.Scrollbar(left, orient="vertical", command=listbox.yview)
        listbox.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        listbox.pack(fill="both", expand=True)
        listbox.bind("<<ListboxSelect>>", lambda e, n=name: self.on_select(n))

        # ---- RIGHT panel (scrollable form) ----
        right = tk.Frame(frame)
        frame.add(right, minsize=450)

        canvas  = tk.Canvas(right, borderwidth=0, highlightthickness=0)
        vscroll = tk.Scrollbar(right, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        form = tk.Frame(canvas)
        fw   = canvas.create_window((0, 0), window=form, anchor="nw")

        form.bind("<Configure>",   lambda e, c=canvas:     c.configure(scrollregion=c.bbox("all")))
        canvas.bind("<Configure>", lambda e, c=canvas, f=fw: c.itemconfig(f, width=e.width))
        canvas.bind_all("<MouseWheel>", lambda e, c=canvas: c.yview_scroll(int(-1*(e.delta/120)), "units"))

        setattr(self, f"{name}_list",       listbox)
        setattr(self, f"{name}_form",       form)
        setattr(self, f"{name}_filter_var", filter_var)
        setattr(self, f"{name}_all_ids",    [])

    # ================================================================
    # OPEN / SAVE
    # ================================================================

    def select_folder(self):
        if self.dirty:
            if not messagebox.askyesno("Unsaved Changes", "You have unsaved changes. Load a new folder anyway?"):
                return

        folder = filedialog.askdirectory()
        if not folder:
            return

        self.folder = folder
        missing = []
        file_map = {
            "foods":         "foods.json",
            "ingredients":   "ingredients.json",
            "religions":     "religions.json",
            "nationalities": "nationalities.json",
            "species":       "species.json",
        }
        defaults = {
            "foods":         {"foods": []},
            "ingredients":   {},
            "religions":     {"religions": []},
            "nationalities": {"nationalities": []},
            "species":       {},
        }
        for key, filename in file_map.items():
            result = load_json(os.path.join(folder, filename))
            if result is None:
                missing.append(filename)
                self.data[key] = defaults[key]
            else:
                self.data[key] = result

        self.title_label.config(text=os.path.basename(folder), fg="black")
        self._set_dirty(False)
        self.refresh_all()
        self.refresh_validation()

        if missing:
            self._log(f"⚠ Not found (using empty): {', '.join(missing)}", color="#ffaa00")

    def save_all(self):
        if not self.folder:
            messagebox.showwarning("No Folder", "Open a data folder first.")
            return
        file_map = {
            "foods":         "foods.json",
            "ingredients":   "ingredients.json",
            "religions":     "religions.json",
            "nationalities": "nationalities.json",
            "species":       "species.json",
        }
        ok = all(save_json(os.path.join(self.folder, fn), self.data[k]) for k, fn in file_map.items())
        if ok:
            self._set_dirty(False)
            self._log("✔ Saved successfully")

    def on_close(self):
        if self.dirty:
            answer = messagebox.askyesnocancel("Unsaved Changes", "Save before closing?")
            if answer is None:
                return
            if answer:
                self.save_all()
        self.root.destroy()

    def _set_dirty(self, dirty: bool):
        self.dirty = dirty
        base = "Monster Café Data Editor"
        self.root.title(f"* {base}" if dirty else base)

    # ================================================================
    # REFRESH / LIST
    # ================================================================

    def refresh_all(self):
        for name in TAB_NAMES:
            self._load_list(name)

    def _get_list_data(self, name):
        if name in LIST_TABS:
            items = self.data[name].get(name, [])
            return [(item.get("id", f"#{i}"), i) for i, item in enumerate(items)]
        else:
            return [(k, i) for i, k in enumerate(self.data[name].keys())]

    def _load_list(self, name, filter_text=""):
        lb      = getattr(self, f"{name}_list")
        all_ids = [lbl for lbl, _ in self._get_list_data(name)]
        setattr(self, f"{name}_all_ids", all_ids)

        lb.delete(0, tk.END)
        clean = filter_text.replace("🔎 filter...", "").strip().lower()
        for lbl in all_ids:
            if not clean or clean in lbl.lower():
                lb.insert(tk.END, lbl)

    def _apply_filter(self, name, text):
        self._load_list(name, text)

    # ================================================================
    # SELECTION
    # ================================================================

    def _on_tab_changed(self, _event):
        self.current_index = None
        self.field_rows    = []

    def on_select(self, name):
        lb = getattr(self, f"{name}_list")
        if not lb.curselection():
            return
        label      = lb.get(lb.curselection()[0])
        real_index = self._label_to_index(name, label)
        if real_index is None:
            return
        self.current_tab   = name
        self.current_index = real_index
        self._build_form(name, self._get_item(name, real_index))

    def _label_to_index(self, name, label):
        for lbl, idx in self._get_list_data(name):
            if lbl == label:
                return idx
        return None

    def _get_item(self, name, i):
        if name in LIST_TABS:
            return self.data[name][name][i]
        k = list(self.data[name].keys())[i]
        return {"id": k, **self.data[name][k]}

    # ================================================================
    # FORM  (with per-row reorder + remove, and add-field footer)
    # ================================================================

    def _clear_frame(self, frame):
        for w in frame.winfo_children():
            w.destroy()

    def _build_form(self, name, item):
        frame = getattr(self, f"{name}_form")
        self._clear_frame(frame)
        self.field_rows = []   # list of [key, Entry, was_list]

        # Determine which keys are schema-required (protect from remove)
        if name in self.schemas:
            protected = set(self.schemas[name].keys())
        elif name == "species":
            protected = set(self.species_schema.keys())
        elif name == "ingredients":
            protected = set(self.ingredients_schema.keys())
        else:
            protected = set()
        # 'id' is always protected for dict tabs (it IS the key)
        if name in DICT_TABS:
            protected.add("id")

        fields_frame = tk.Frame(frame)
        fields_frame.pack(fill="x", expand=False)

        for k, v in item.items():
            self._add_field_row(fields_frame, k, v, protected, name)

        # ---- footer: add new field ----
        sep = tk.Frame(frame, height=2, bg="#444")
        sep.pack(fill="x", pady=4)

        footer = tk.Frame(frame)
        footer.pack(fill="x", padx=4, pady=2)

        tk.Label(footer, text="New field:", font=("Consolas", 9)).pack(side="left")

        new_key_var = tk.StringVar()
        tk.Entry(footer, textvariable=new_key_var, width=18, font=("Consolas", 9)).pack(side="left", padx=4)

        type_var = tk.StringVar(value="str")
        tk.OptionMenu(footer, type_var, "str", "list").pack(side="left")

        tk.Button(
            footer, text="➕ Add Field",
            command=lambda ff=fields_frame, nkv=new_key_var, tv=type_var, p=protected, n=name:
                self._add_custom_field(ff, nkv, tv, p, n)
        ).pack(side="left", padx=4)

        # ---- apply button ----
        tk.Button(frame, text="✔ Apply", command=self.apply,
                  bg="#2a7a2a", fg="white", font=("Consolas", 10, "bold")).pack(pady=6)

        # store ref to fields frame for row-reorder redraws
        setattr(self, f"{name}_fields_frame", fields_frame)

    def _add_field_row(self, fields_frame, key, value, protected, tab_name, index=None):
        """Render one key-value row with ▲▼ reorder and optional ✕ remove."""
        row = tk.Frame(fields_frame, bd=1, relief="flat")
        row.pack(fill="x", padx=2, pady=1)

        # ▲ ▼ reorder buttons
        nav = tk.Frame(row)
        nav.pack(side="left")
        tk.Button(nav, text="▲", width=2, font=("Consolas", 7),
                  command=lambda: self._move_field(fields_frame, row, -1, protected, tab_name)
                  ).pack()
        tk.Button(nav, text="▼", width=2, font=("Consolas", 7),
                  command=lambda: self._move_field(fields_frame, row, +1, protected, tab_name)
                  ).pack()

        # key label
        tk.Label(row, text=key, width=24, anchor="w", font=("Consolas", 9)).pack(side="left")

        # value entry
        e = tk.Entry(row, font=("Consolas", 9))
        e.pack(side="left", fill="x", expand=True)

        is_list = isinstance(value, list)
        if is_list:
            e.insert(0, ", ".join(str(x) for x in value))
        else:
            e.insert(0, str(value))

        # ✕ remove button (hidden for protected keys)
        if key not in protected:
            tk.Button(row, text="✕", fg="red", width=2,
                      command=lambda r=row, k=key: self._remove_field_row(r, k)
                      ).pack(side="right")

        row_data = [key, e, is_list]
        if index is not None:
            self.field_rows.insert(index, row_data)
        else:
            self.field_rows.append(row_data)

    def _remove_field_row(self, row_widget, key):
        """Remove a field row from the form (does not touch data until Apply)."""
        self.field_rows = [r for r in self.field_rows if r[0] != key]
        row_widget.destroy()

    def _move_field(self, fields_frame, row_widget, direction, protected, tab_name):
        """Swap a row up or down in field_rows and redraw."""
        # Find the row in field_rows by its Entry widget
        row_widgets = [w for w in fields_frame.winfo_children()]
        if row_widget not in row_widgets:
            return
        idx = row_widgets.index(row_widget)
        new_idx = idx + direction
        if new_idx < 0 or new_idx >= len(row_widgets):
            return

        # Swap in field_rows list too
        if idx < len(self.field_rows) and new_idx < len(self.field_rows):
            self.field_rows[idx], self.field_rows[new_idx] = \
                self.field_rows[new_idx], self.field_rows[idx]

        # Repack: lift or lower in tk stacking order
        if direction == -1:
            row_widget.pack_forget()
            row_widgets[new_idx].pack_forget()
            row_widget.pack(fill="x", padx=2, pady=1,
                            before=row_widgets[new_idx])
            row_widgets[new_idx].pack(fill="x", padx=2, pady=1)
        else:
            next_w = row_widgets[new_idx]
            next_w.pack_forget()
            row_widget.pack_forget()
            next_w.pack(fill="x", padx=2, pady=1,
                        before=row_widget if new_idx < idx else None)
            row_widget.pack(fill="x", padx=2, pady=1)

        # Simplest correct approach: rebuild order from current pack order
        self._sync_field_rows_from_widgets(fields_frame)

    def _sync_field_rows_from_widgets(self, fields_frame):
        """Re-sync self.field_rows to match current widget pack order."""
        key_to_row = {r[0]: r for r in self.field_rows}
        new_order  = []
        for w in fields_frame.winfo_children():
            # Each child frame contains label then entry; label text = key
            for child in w.winfo_children():
                if isinstance(child, tk.Label) and child.cget("width") == 24:
                    k = child.cget("text")
                    if k in key_to_row:
                        new_order.append(key_to_row[k])
                    break
        self.field_rows = new_order

    def _add_custom_field(self, fields_frame, key_var, type_var, protected, tab_name):
        key = key_var.get().strip()
        if not key:
            messagebox.showwarning("Add Field", "Enter a field name.")
            return
        # Check for duplicate
        if any(r[0] == key for r in self.field_rows):
            messagebox.showwarning("Add Field", f"Field '{key}' already exists.")
            return
        default_val = [] if type_var.get() == "list" else ""
        self._add_field_row(fields_frame, key, default_val, protected, tab_name)
        key_var.set("")

    # ================================================================
    # APPLY  (reads field_rows in current order)
    # ================================================================

    def apply(self):
        name = self.current_tab
        i    = self.current_index
        if i is None:
            return

        # Sync widget order one last time
        ff_attr = f"{name}_fields_frame"
        if hasattr(self, ff_attr):
            self._sync_field_rows_from_widgets(getattr(self, ff_attr))

        data = {}
        for key, entry, was_list in self.field_rows:
            raw = entry.get().strip()
            if was_list:
                data[key] = [x.strip() for x in raw.split(",") if x.strip()] if raw else []
            else:
                data[key] = raw

        if name in LIST_TABS:
            self.data[name][name][i] = data
        else:
            old_key = list(self.data[name].keys())[i]
            new_key = data.pop("id", old_key)
            payload = data

            if new_key != old_key:
                rebuilt = {}
                for k, v in self.data[name].items():
                    rebuilt[new_key if k == old_key else k] = payload if k == old_key else v
                self.data[name] = rebuilt
            else:
                self.data[name][old_key] = payload

        self._set_dirty(True)
        self.refresh_all()
        self.refresh_validation()

        label = data.get("id") if name in LIST_TABS else (new_key if name in DICT_TABS else None)
        if label:
            self._reselect(name, label)

    def _reselect(self, name, label):
        if not label:
            return
        lb = getattr(self, f"{name}_list")
        for i in range(lb.size()):
            if lb.get(i) == label:
                lb.selection_clear(0, tk.END)
                lb.selection_set(i)
                lb.see(i)
                break

    # ================================================================
    # ADD ITEM
    # ================================================================

    def add_item(self, name):
        if name in LIST_TABS:
            new_item  = {k: (list(v) if isinstance(v, list) else v) for k, v in self.defaults[name].items()}
            self.data[name][name].append(new_item)
            new_label = new_item["id"]
        else:
            base = f"new_{name.rstrip('s')}"
            key  = base
            n    = 1
            while key in self.data[name]:
                key = f"{base}_{n}"; n += 1
            self.data[name][key] = {k: (list(v) if isinstance(v, list) else v)
                                    for k, v in self.defaults[name].items()}
            new_label = key

        self._set_dirty(True)
        self.refresh_all()
        self._reselect(name, new_label)
        self.current_tab   = name
        self.current_index = self._label_to_index(name, new_label)
        if self.current_index is not None:
            self._build_form(name, self._get_item(name, self.current_index))

    # ================================================================
    # DELETE ITEM
    # ================================================================

    def delete_item(self, name):
        lb = getattr(self, f"{name}_list")
        if not lb.curselection():
            return
        label = lb.get(lb.curselection()[0])
        idx   = self._label_to_index(name, label)
        if idx is None:
            return
        if not messagebox.askyesno("Confirm Delete", f"Delete '{label}'?"):
            return

        if name in LIST_TABS:
            self.data[name][name].pop(idx)
        else:
            del self.data[name][list(self.data[name].keys())[idx]]

        self.current_index = None
        self.field_rows    = []
        self._clear_frame(getattr(self, f"{name}_form"))
        self._set_dirty(True)
        self.refresh_all()
        self.refresh_validation()

    # ================================================================
    # MOVE ITEM (reorder in list)
    # ================================================================

    def move_item(self, name, direction):
        lb = getattr(self, f"{name}_list")
        if not lb.curselection():
            return

        label = lb.get(lb.curselection()[0])
        idx   = self._label_to_index(name, label)
        if idx is None:
            return

        if name in LIST_TABS:
            lst = self.data[name][name]
            new_idx = idx + direction
            if new_idx < 0 or new_idx >= len(lst):
                return
            lst[idx], lst[new_idx] = lst[new_idx], lst[idx]
            new_label = lst[new_idx].get("id", label)
        else:
            keys = list(self.data[name].keys())
            new_idx = idx + direction
            if new_idx < 0 or new_idx >= len(keys):
                return
            keys[idx], keys[new_idx] = keys[new_idx], keys[idx]
            self.data[name] = {k: self.data[name][k] for k in keys}
            new_label = keys[new_idx]

        self._set_dirty(True)
        self.current_index = new_idx
        self.refresh_all()
        self._reselect(name, new_label)

    # ================================================================
    # SCHEMA FIX
    # ================================================================

    def fix_schema(self, name):
        if name in LIST_TABS:
            for item in self.data[name][name]:
                for k, v in self.defaults[name].items():
                    item.setdefault(k, list(v) if isinstance(v, list) else v)

        elif name == "ingredients":
            fixed = {}
            for k, v in self.data[name].items():
                if not isinstance(v, dict):
                    v = {}
                for fk, fv in self.defaults["ingredients"].items():
                    v.setdefault(fk, list(fv) if isinstance(fv, list) else fv)
                fixed[k] = v
            self.data[name] = fixed

        elif name == "species":
            for k, v in self.data[name].items():
                if not isinstance(v, dict):
                    self.data[name][k] = {}
                    v = self.data[name][k]
                for fk, fv in self.defaults["species"].items():
                    v.setdefault(fk, list(fv) if isinstance(fv, list) else fv)

        self._set_dirty(True)
        self.refresh_all()
        self.refresh_validation()

    # ================================================================
    # VALIDATION
    # ================================================================

    def refresh_validation(self):
        errors = []
        errors += validate_foods_ingredients(self.data["foods"], self.data["ingredients"])
        for tab_name, schema in self.schemas.items():
            errors += validate_list_schema(self.data[tab_name].get(tab_name, []), schema, tab_name)
        errors += validate_dict_schema(self.data["species"],     self.species_schema,     "species")
        errors += validate_dict_schema(self.data["ingredients"], self.ingredients_schema, "ingredients")

        self.validation.configure(state="normal")
        self.validation.delete("1.0", tk.END)
        if not errors:
            self._log("✔ No errors")
        else:
            self._log(f"⚠ {len(errors)} error(s) found:", color="#ffaa00")
            for e in errors:
                self._log("  " + e, color="#ff6666")
        self.validation.configure(state="disabled")

    def _log(self, msg, color="#00ff88"):
        self.validation.configure(state="normal")
        self.validation.insert(tk.END, msg + "\n", color)
        self.validation.tag_config(color, foreground=color)
        self.validation.configure(state="disabled")


    # ================================================================
    # SCHEMA EDITOR
    # ================================================================

    def open_schema_editor(self):
        """Open a Toplevel window to add/remove/rename/reorder schema fields."""
        win = tk.Toplevel(self.root)
        win.title("Schema Editor")
        win.geometry("700x560")
        win.grab_set()          # modal

        # ---- tab selector ----
        tab_frame = tk.Frame(win)
        tab_frame.pack(fill="x", padx=6, pady=4)

        tk.Label(tab_frame, text="Schema:", font=("Consolas", 10, "bold")).pack(side="left")

        schema_names = list(self.schemas.keys()) + ["ingredients", "species"]
        sel_var = tk.StringVar(value=schema_names[0])

        # Content area (rebuilt when tab changes)
        content = tk.Frame(win)
        content.pack(fill="both", expand=True, padx=6, pady=2)

        def show_schema(sname):
            sel_var.set(sname)
            for w in content.winfo_children():
                w.destroy()
            self._build_schema_editor_panel(content, sname, win)

        for sname in schema_names:
            tk.Button(
                tab_frame, text=sname,
                command=lambda s=sname: show_schema(s),
                relief="groove", padx=4
            ).pack(side="left", padx=2)

        # bottom buttons
        btn_row = tk.Frame(win)
        btn_row.pack(fill="x", padx=6, pady=6)
        tk.Button(btn_row, text="Close", command=win.destroy).pack(side="right")
        tk.Button(
            btn_row, text="Reset All to Defaults",
            fg="red",
            command=lambda: self._reset_schemas_to_defaults(win, show_schema, sel_var)
        ).pack(side="left")

        show_schema(schema_names[0])

    def _get_schema_for(self, name):
        """Return the live schema dict for a given tab name."""
        if name == "species":
            return self.species_schema
        if name == "ingredients":
            return self.ingredients_schema
        return self.schemas[name]

    def _build_schema_editor_panel(self, parent, schema_name, win):
        """Build the field-list editor for one schema inside `parent`."""
        schema = self._get_schema_for(schema_name)

        # header
        hdr = tk.Frame(parent)
        hdr.pack(fill="x", pady=2)
        tk.Label(hdr, text=f"Fields for  '{schema_name}'",
                 font=("Consolas", 10, "bold")).pack(side="left")
        tk.Label(hdr, text="  (changes apply immediately to validation & Fix Schema)",
                 font=("Consolas", 8), fg="grey").pack(side="left")

        # scrollable list of rows
        canvas  = tk.Canvas(parent, borderwidth=0, highlightthickness=0)
        vscroll = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        rows_frame = tk.Frame(canvas)
        fw = canvas.create_window((0, 0), window=rows_frame, anchor="nw")
        rows_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",     lambda e: canvas.itemconfig(fw, width=e.width))

        # column headers
        col_hdr = tk.Frame(rows_frame, bg="#333")
        col_hdr.pack(fill="x")
        for txt, w in [("", 5), ("Field Name", 24), ("Type", 8), ("Default Value", 20), ("", 6)]:
            tk.Label(col_hdr, text=txt, width=w, bg="#333", fg="white",
                     font=("Consolas", 9, "bold"), anchor="w").pack(side="left")

        # list of [field_name, type_var, default_var, row_frame]
        schema_rows = []

        def rebuild_rows():
            for w in rows_frame.winfo_children():
                if w is not col_hdr:
                    w.destroy()
            schema_rows.clear()
            for fname, ftype in schema.items():
                _add_schema_row(fname, ftype)

        def _add_schema_row(fname, ftype, at_end=False):
            row = tk.Frame(rows_frame, bd=1, relief="groove")
            row.pack(fill="x", padx=2, pady=1)

            # ▲▼ move
            nav = tk.Frame(row)
            nav.pack(side="left")
            tk.Button(nav, text="▲", width=2, font=("Consolas", 7),
                      command=lambda r=row: _move_row(r, -1)).pack()
            tk.Button(nav, text="▼", width=2, font=("Consolas", 7),
                      command=lambda r=row: _move_row(r, +1)).pack()

            # field name entry
            name_var = tk.StringVar(value=fname)
            tk.Entry(row, textvariable=name_var, width=22,
                     font=("Consolas", 9)).pack(side="left", padx=2)

            # type selector
            type_var = tk.StringVar(value="list" if ftype is list else "str")
            tk.OptionMenu(row, type_var, "str", "list").pack(side="left", padx=2)

            # default value entry
            cur_default = self.defaults.get(schema_name, {}).get(fname, "" if ftype is str else [])
            def_str = ", ".join(cur_default) if isinstance(cur_default, list) else str(cur_default)
            default_var = tk.StringVar(value=def_str)
            tk.Entry(row, textvariable=default_var, width=18,
                     font=("Consolas", 9)).pack(side="left", padx=2, fill="x", expand=True)

            # ✕ remove (protect 'id' for list-tabs)
            is_protected = (fname == "id" and schema_name in LIST_TABS)
            if not is_protected:
                tk.Button(row, text="✕", fg="red", width=2,
                          command=lambda r=row, fn=fname: _remove_row(r, fn)).pack(side="right")

            schema_rows.append([name_var, type_var, default_var, row])

        def _move_row(row_widget, direction):
            children = [w for w in rows_frame.winfo_children() if w is not col_hdr]
            if row_widget not in children:
                return
            idx = children.index(row_widget)
            new_idx = idx + direction
            if new_idx < 0 or new_idx >= len(children):
                return
            _commit_schema(schema_name)
            # rebuild with new order
            keys  = list(schema.keys())
            types = list(schema.values())
            keys[idx],  keys[new_idx]  = keys[new_idx],  keys[idx]
            types[idx], types[new_idx] = types[new_idx], types[idx]
            schema.clear()
            for k, t in zip(keys, types):
                schema[k] = t
            rebuild_rows()

        def _remove_row(row_widget, field_name):
            if not messagebox.askyesno("Remove Field",
                                       f"Remove field '{field_name}' from the '{schema_name}' schema?\n"
                                       "This won't delete existing data — just stops treating it as required.",
                                       parent=win):
                return
            schema.pop(field_name, None)
            self.defaults.get(schema_name, {}).pop(field_name, None)
            row_widget.destroy()
            schema_rows[:] = [r for r in schema_rows if r[3] is not row_widget]

        rebuild_rows()

        # ---- add new field footer ----
        sep = tk.Frame(parent, height=2, bg="#444")
        sep.pack(fill="x", pady=3)

        add_row = tk.Frame(parent)
        add_row.pack(fill="x", padx=4, pady=2)

        tk.Label(add_row, text="New field:", font=("Consolas", 9)).pack(side="left")
        new_name_var = tk.StringVar()
        tk.Entry(add_row, textvariable=new_name_var, width=18,
                 font=("Consolas", 9)).pack(side="left", padx=4)
        new_type_var = tk.StringVar(value="str")
        tk.OptionMenu(add_row, new_type_var, "str", "list").pack(side="left")
        new_default_var = tk.StringVar()
        tk.Entry(add_row, textvariable=new_default_var, width=14,
                 font=("Consolas", 9)).pack(side="left", padx=4)
        tk.Label(add_row, text="(default)", font=("Consolas", 8), fg="grey").pack(side="left")

        def _do_add_field():
            fname = new_name_var.get().strip()
            if not fname:
                messagebox.showwarning("Add Field", "Enter a field name.", parent=win)
                return
            if fname in schema:
                messagebox.showwarning("Add Field", f"'{fname}' already exists.", parent=win)
                return
            ftype = list if new_type_var.get() == "list" else str
            schema[fname] = ftype
            # update defaults
            raw = new_default_var.get().strip()
            if ftype is list:
                default_val = [x.strip() for x in raw.split(",") if x.strip()] if raw else []
            else:
                default_val = raw
            self.defaults.setdefault(schema_name, {})[fname] = default_val
            new_name_var.set("")
            new_default_var.set("")
            _add_schema_row(fname, ftype)

        tk.Button(add_row, text="➕ Add Field", command=_do_add_field).pack(side="left", padx=4)

        # ---- apply button ----
        tk.Button(parent, text="✔ Apply Changes",
                  bg="#2a5a8a", fg="white", font=("Consolas", 10, "bold"),
                  command=lambda: _commit_schema(schema_name)).pack(pady=4)

        def _commit_schema(sname):
            """Read current widget values back into the live schema + defaults."""
            new_schema   = {}
            new_defaults = {}
            for name_var, type_var, default_var, row in schema_rows:
                fname = name_var.get().strip()
                if not fname:
                    continue
                ftype = list if type_var.get() == "list" else str
                new_schema[fname] = ftype
                raw = default_var.get().strip()
                if ftype is list:
                    new_defaults[fname] = [x.strip() for x in raw.split(",") if x.strip()] if raw else []
                else:
                    new_defaults[fname] = raw

            # Write back into the correct live dict
            if sname == "species":
                self.species_schema.clear()
                self.species_schema.update(new_schema)
            elif sname == "ingredients":
                self.ingredients_schema.clear()
                self.ingredients_schema.update(new_schema)
            else:
                self.schemas[sname].clear()
                self.schemas[sname].update(new_schema)

            self.defaults[sname] = new_defaults
            self.refresh_validation()
            self._log(f"✔ Schema '{sname}' updated")

    def _reset_schemas_to_defaults(self, win, show_fn, sel_var):
        if not messagebox.askyesno("Reset Schemas",
                                   "Reset ALL schemas to their built-in defaults?\n"
                                   "This cannot be undone.", parent=win):
            return
        self.schemas            = {k: dict(v) for k, v in _INITIAL_SCHEMAS.items()}
        self.species_schema     = dict(_INITIAL_SPECIES_SCHEMA)
        self.ingredients_schema = dict(_INITIAL_INGREDIENTS_SCHEMA)
        self.defaults           = _initial_defaults()
        self.refresh_validation()
        show_fn(sel_var.get())
        self._log("✔ Schemas reset to defaults")


# ----------------------------
# RUN
# ----------------------------

root = tk.Tk()
root.geometry("1200x750")

app = App(root)

root.mainloop()
