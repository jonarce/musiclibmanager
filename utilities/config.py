#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re
import platform


class CustomConfigParser:
    """
    Parser di configurazione personalizzato che gestisce i commenti inline.

    Questa classe implementa un parser simile a ConfigParser ma separando
    completamente i valori dai commenti inline.
    """

    def __init__(self, comment_prefixes=('#', ';')):
        """
        Inizializza un parser di configurazione personalizzato.

        Args:
            comment_prefixes: Caratteri che identificano l'inizio di un commento
        """
        self._sections = {}
        self.inline_comments = {}
        self.comment_prefixes = comment_prefixes

    def add_section(self, section):
        """
        Aggiunge una nuova sezione al parser.

        Args:
            section: Il nome della sezione da aggiungere
        """
        if section not in self._sections:
            self._sections[section] = {}
            self.inline_comments[section] = {}

    def set(self, section, key, value):
        """
        Imposta un valore per una chiave in una sezione.

        Args:
            section: La sezione in cui aggiungere la chiave
            key: La chiave da aggiungere
            value: Il valore da associare alla chiave
        """
        if section not in self._sections:
            self.add_section(section)
        self._sections[section][key] = value

    def get(self, section, key, fallback=None):
        """
        Ottiene un valore da una sezione/chiave.

        Args:
            section: La sezione da cui ottenere il valore
            key: La chiave di cui ottenere il valore
            fallback: Valore di default se la chiave non esiste

        Returns:
            Il valore associato alla chiave o il fallback
        """
        if section in self._sections and key in self._sections[section]:
            return self._sections[section][key]
        return fallback

    def remove_option(self, section, key):
        """
        Rimuove una chiave da una sezione.

        Args:
            section: La sezione da cui rimuovere la chiave
            key: La chiave da rimuovere

        Returns:
            True se la chiave è stata rimossa, False altrimenti
        """
        if section in self._sections and key in self._sections[section]:
            del self._sections[section][key]
            if section in self.inline_comments and key in self.inline_comments[section]:
                del self.inline_comments[section][key]
            return True
        return False

    def remove_section(self, section):
        """
        Rimuove una sezione dal parser.

        Args:
            section: La sezione da rimuovere

        Returns:
            True se la sezione è stata rimossa, False altrimenti
        """
        if section in self._sections:
            del self._sections[section]
            if section in self.inline_comments:
                del self.inline_comments[section]
            return True
        return False

    def has_section(self, section):
        """
        Verifica se una sezione esiste.

        Args:
            section: La sezione da verificare

        Returns:
            True se la sezione esiste, False altrimenti
        """
        return section in self._sections

    def has_option(self, section, key):
        """
        Verifica se una chiave esiste in una sezione.

        Args:
            section: La sezione in cui cercare la chiave
            key: La chiave da verificare

        Returns:
            True se la chiave esiste nella sezione, False altrimenti
        """
        return section in self._sections and key in self._sections[section]

    def get_sections(self):
        """
        Restituisce l'elenco delle sezioni.

        Returns:
            Lista delle sezioni presenti nel parser
        """
        return list(self._sections.keys())

    def items(self, section):
        """
        Restituisce tutte le coppie chiave-valore di una sezione.

        Args:
            section: La sezione di cui ottenere le coppie

        Returns:
            Dizionario con le coppie chiave-valore della sezione
        """
        if section in self._sections:
            return self._sections[section].items()
        return []

    def __contains__(self, section):
        """
        Verifica se una sezione esiste utilizzando l'operatore 'in'.

        Args:
            section: La sezione da verificare

        Returns:
            True se la sezione esiste, False altrimenti
        """
        return section in self._sections

    def __getitem__(self, section):
        """
        Accede a una sezione utilizzando la notazione a parentesi quadre.

        Args:
            section: La sezione da ottenere

        Returns:
            Dizionario con le coppie chiave-valore della sezione

        Raises:
            KeyError: Se la sezione non esiste
        """
        if section in self._sections:
            return self._sections[section]
        raise KeyError(section)

    def get_inline_comment(self, section, key):
        """
        Restituisce il commento inline per una chiave specifica.

        Args:
            section: La sezione del file .ini
            key: La chiave di cui recuperare il commento

        Returns:
            Il commento inline o una stringa vuota se non presente
        """
        if section in self.inline_comments and key in self.inline_comments[section]:
            return self.inline_comments[section][key]
        return ""

    def set_inline_comment(self, section, key, comment):
        """
        Imposta il commento inline per una chiave specifica.

        Args:
            section: La sezione del file .ini
            key: La chiave a cui associare il commento
            comment: Il commento da salvare
        """
        if section not in self.inline_comments:
            self.inline_comments[section] = {}
        self.inline_comments[section][key] = comment

    def read(self, filename, encoding='utf-8'):
        """
        Legge un file .ini.

        Args:
            filename: Il percorso del file da leggere
            encoding: La codifica del file

        Returns:
            Lista contenente il nome del file se la lettura è riuscita
        """
        try:
            with open(filename, 'r', encoding=encoding) as f:
                self._parse(f)
            return [filename]
        except Exception as e:
            print(f"Errore nella lettura del file: {e}")
            return []

    def _parse(self, file_obj):
        """
        Analizza il contenuto di un file .ini.

        Args:
            file_obj: Un oggetto file da cui leggere
        """
        current_section = None

        for line in file_obj:
            line = line.strip()

            # Ignora linee vuote
            if not line:
                continue

            # Ignora linee di solo commento
            if any(line.startswith(prefix) for prefix in self.comment_prefixes):
                continue

            # Controlla se è una sezione
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1].strip()
                self.add_section(current_section)
                continue

            # Se non abbiamo una sezione attiva, salta
            if current_section is None:
                continue

            # Cerca il delimitatore chiave-valore
            key_value_match = re.match(r'^([^=]+)=(.*)$', line)
            if key_value_match:
                key = key_value_match.group(1).strip()
                full_value = key_value_match.group(2).strip()

                # Cerca il primo carattere di commento non in una stringa
                comment_pos = -1
                in_quote = False
                quote_char = None

                for i, char in enumerate(full_value):
                    if char in ['"', "'"]:
                        if not in_quote:
                            in_quote = True
                            quote_char = char
                        elif char == quote_char:
                            in_quote = False

                    if not in_quote and char in self.comment_prefixes:
                        comment_pos = i
                        break

                # Estrai il valore effettivo e il commento
                if comment_pos > -1:
                    value = full_value[:comment_pos].strip()
                    comment = full_value[comment_pos:].strip()
                else:
                    value = full_value
                    comment = ""

                # Salva il valore e il commento
                self.set(current_section, key, value)
                if comment:
                    self.set_inline_comment(current_section, key, comment)

    def write(self, file_obj):
        """
        Scrive il contenuto del parser in un file .ini.

        Args:
            file_obj: Un oggetto file su cui scrivere
        """
        for section in self._sections:
            file_obj.write(f"[{section}]\n")

            for key, value in self._sections[section].items():
                line = f"{key}={value}"
                comment = self.get_inline_comment(section, key)
                if comment:
                    line += f" {comment}"
                file_obj.write(f"{line}\n")

            # Aggiungi una linea vuota dopo ogni sezione
            file_obj.write("\n")


class IniEditorApp:
    """
    Applicazione per visualizzare e modificare file .ini con interfaccia grafica.

    Questa classe implementa un'interfaccia utente che permette di:
    - Aprire file .ini esistenti
    - Visualizzare e modificare sezioni, valori e commenti inline
    - Salvare le modifiche su file
    - Creare nuove sezioni e coppie chiave-valore
    """

    def __init__(self, root):
        """
        Inizializza l'applicazione di editing dei file .ini.

        Args:
            root: L'elemento radice Tkinter per l'applicazione
        """
        self.root = root
        self.root.title("Editor File INI")
        self.root.geometry("900x600")

        self.config = CustomConfigParser(comment_prefixes=('#', ';'))
        self.current_file = None
        self.current_section = None  # Aggiungiamo una variabile per tenere traccia della sezione corrente

        # Configura scorciatoie da tastiera
        self.setup_keyboard_shortcuts()

        self._create_menu()
        self._create_ui()

    def setup_keyboard_shortcuts(self):
        """Configura le scorciatoie da tastiera dell'applicazione."""
        # Ctrl+S per salvare (Cmd+S su macOS)
        self.root.bind('<Control-s>', lambda event: self.save_file())
        if platform.system() == 'Darwin':  # macOS
            self.root.bind('<Command-s>', lambda event: self.save_file())

    def center_window(self, window, width=None, height=None):
        """
        Centra una finestra di dialogo rispetto alla finestra principale.

        Args:
            window: La finestra di dialogo da centrare
            width: Larghezza della finestra (opzionale)
            height: Altezza della finestra (opzionale)
        """
        if width is not None and height is not None:
            window.geometry(f"{width}x{height}")

        window.withdraw()
        window.update_idletasks()

        # Ottiene le dimensioni della finestra
        win_width = window.winfo_width()
        win_height = window.winfo_height()

        # Ottiene le dimensioni dello schermo
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Ottiene la posizione della finestra principale
        main_x = self.root.winfo_rootx()
        main_y = self.root.winfo_rooty()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()

        # Calcola la posizione centrata
        x = main_x + (main_width - win_width) // 2
        y = main_y + (main_height - win_height) // 2

        # Verifica che la finestra sia visibile nello schermo
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x + win_width > screen_width:
            x = screen_width - win_width
        if y + win_height > screen_height:
            y = screen_height - win_height

        # Imposta la posizione della finestra
        window.geometry(f"{win_width}x{win_height}+{x}+{y}")
        window.deiconify()

    def _create_menu(self):
        """Crea la barra del menu per l'applicazione."""
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Nuovo", command=self.new_file)
        file_menu.add_command(label="Apri", command=self.open_file)
        file_menu.add_command(label="Salva", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Salva con nome", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Esci", command=self.root.quit)

        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

    def _create_ui(self):
        """Crea gli elementi dell'interfaccia utente."""
        # Frame principale con divisore
        self.main_frame = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame sinistro con lista sezioni
        self.left_frame = ttk.Frame(self.main_frame)
        self.main_frame.add(self.left_frame, weight=1)

        # Label e bottoni per sezioni
        ttk.Label(self.left_frame, text="Sezioni:").pack(anchor=tk.W)

        section_buttons = ttk.Frame(self.left_frame)
        section_buttons.pack(fill=tk.X, pady=5)

        ttk.Button(section_buttons, text="Aggiungi", command=self.add_section).pack(side=tk.LEFT, padx=2)
        ttk.Button(section_buttons, text="Rimuovi", command=self.remove_section).pack(side=tk.LEFT, padx=2)

        # Contenitore con scrollbar per la lista sezioni
        section_container = ttk.Frame(self.left_frame)
        section_container.pack(fill=tk.BOTH, expand=True)

        # Scrollbar per la lista sezioni
        section_scrollbar = ttk.Scrollbar(section_container)
        section_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Lista sezioni
        self.section_listbox = tk.Listbox(section_container, yscrollcommand=section_scrollbar.set)
        self.section_listbox.pack(fill=tk.BOTH, expand=True)
        section_scrollbar.config(command=self.section_listbox.yview)
        self.section_listbox.bind('<<ListboxSelect>>', self.on_section_select)

        # Frame destro con proprietà
        self.right_frame = ttk.Frame(self.main_frame)
        self.main_frame.add(self.right_frame, weight=3)

        # Label per mostrare la sezione corrente
        self.section_label_var = tk.StringVar(value="Nessuna sezione selezionata")
        self.section_label = ttk.Label(self.right_frame, textvariable=self.section_label_var, font=("", 10, "bold"))
        self.section_label.pack(anchor=tk.W, pady=(0, 5))

        # Label e bottoni per proprietà
        ttk.Label(self.right_frame, text="Proprietà:").pack(anchor=tk.W)

        prop_buttons = ttk.Frame(self.right_frame)
        prop_buttons.pack(fill=tk.X, pady=5)

        ttk.Button(prop_buttons, text="Aggiungi", command=self.add_property).pack(side=tk.LEFT, padx=2)
        ttk.Button(prop_buttons, text="Rimuovi", command=self.remove_property).pack(side=tk.LEFT, padx=2)

        # Contenitore per la tabella proprietà con scrollbar
        tree_container = ttk.Frame(self.right_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        # Scrollbar verticale e orizzontale per la tabella
        y_scrollbar = ttk.Scrollbar(tree_container)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        x_scrollbar = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Tabella proprietà
        columns = ("Chiave", "Valore", "Note")
        self.property_tree = ttk.Treeview(tree_container, columns=columns, show="headings",
                                          yscrollcommand=y_scrollbar.set,
                                          xscrollcommand=x_scrollbar.set)

        # Configura le scrollbar
        y_scrollbar.config(command=self.property_tree.yview)
        x_scrollbar.config(command=self.property_tree.xview)

        # Configura le colonne
        self.property_tree.heading("Chiave", text="Chiave")
        self.property_tree.heading("Valore", text="Valore")
        self.property_tree.heading("Note", text="Note")

        self.property_tree.column("Chiave", width=150, minwidth=100)
        self.property_tree.column("Valore", width=200, minwidth=100)
        self.property_tree.column("Note", width=350, minwidth=150)

        self.property_tree.pack(fill=tk.BOTH, expand=True)
        self.property_tree.bind("<Double-1>", self.on_property_double_click)

        # Barra di stato
        self.status_var = tk.StringVar()
        self.status_var.set("Pronto")
        ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).pack(
            side=tk.BOTTOM, fill=tk.X)

    def new_file(self):
        """Crea un nuovo file .ini vuoto."""
        self.config = CustomConfigParser(comment_prefixes=('#', ';'))
        self.current_file = None
        self.current_section = None
        self.section_label_var.set("Nessuna sezione selezionata")
        self.update_section_list()
        self.property_tree.delete(*self.property_tree.get_children())
        self.status_var.set("Nuovo file creato")

    def open_file(self):
        """Apre un file .ini esistente."""
        filepath = filedialog.askopenfilename(
            filetypes=[("INI files", "*.ini"), ("Tutti i file", "*.*")]
        )

        if not filepath:
            return

        try:
            self.config = CustomConfigParser(comment_prefixes=('#', ';'))
            self.config.read(filepath, encoding='utf-8')
            self.current_file = filepath
            self.current_section = None
            self.section_label_var.set("Nessuna sezione selezionata")
            self.update_section_list()
            self.property_tree.delete(*self.property_tree.get_children())
            self.status_var.set(f"File aperto: {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile aprire il file:\n{str(e)}")

    def save_file(self, event=None):
        """
        Salva il file .ini corrente.

        Args:
            event: Evento della tastiera (opzionale)
        """
        if not self.current_file:
            self.save_file_as()
            return

        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
            self.status_var.set(f"File salvato: {os.path.basename(self.current_file)}")
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile salvare il file:\n{str(e)}")

    def save_file_as(self):
        """Salva il file .ini corrente con un nuovo nome."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".ini",
            filetypes=[("INI files", "*.ini"), ("Tutti i file", "*.*")]
        )

        if not filepath:
            return

        self.current_file = filepath
        self.save_file()

    def update_section_list(self):
        """Aggiorna la lista delle sezioni nell'interfaccia."""
        self.section_listbox.delete(0, tk.END)
        for section in self.config.get_sections():
            self.section_listbox.insert(tk.END, section)

    def update_property_list(self, section):
        """
        Aggiorna la lista delle proprietà per la sezione selezionata.

        Args:
            section: Il nome della sezione di cui visualizzare le proprietà
        """
        self.property_tree.delete(*self.property_tree.get_children())
        if section in self.config:
            for key, value in self.config[section].items():
                # Ottiene il commento inline associato
                comment = self.config.get_inline_comment(section, key)
                self.property_tree.insert("", tk.END, values=(key, value, comment))

    def on_section_select(self, event):
        """Gestisce la selezione di una sezione dalla lista."""
        selection = self.section_listbox.curselection()
        if selection:
            section = self.section_listbox.get(selection[0])
            self.current_section = section  # Aggiorna la sezione corrente
            self.section_label_var.set(f"Sezione: [{section}]")  # Aggiorna l'etichetta
            self.update_property_list(section)

    def on_property_double_click(self, event):
        """Gestisce il doppio click su una proprietà per modificarla."""
        selected_items = self.property_tree.selection()
        if not selected_items:
            return

        item = selected_items[0]
        key, value, comment = self.property_tree.item(item, "values")

        # Controlla se è selezionata una sezione
        if not self.current_section:
            messagebox.showwarning("Avviso", "Nessuna sezione selezionata")
            return

        # Finestra di dialogo per modifica
        dialog = tk.Toplevel(self.root)
        dialog.title("Modifica Proprietà")
        dialog.geometry("500x200")
        dialog.transient(self.root)
        dialog.grab_set()

        # Mostra la sezione corrente nella finestra di dialogo
        ttk.Label(dialog, text=f"Sezione: [{self.current_section}]", font=("", 10, "bold")).grid(
            row=0, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)

        ttk.Label(dialog, text="Chiave:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        key_var = tk.StringVar(value=key)
        key_entry = ttk.Entry(dialog, textvariable=key_var, width=50)
        key_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Valore:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        value_var = tk.StringVar(value=value)
        value_entry = ttk.Entry(dialog, textvariable=value_var, width=50)
        value_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Note:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        comment_var = tk.StringVar(value=comment if comment else "")
        comment_entry = ttk.Entry(dialog, textvariable=comment_var, width=50)
        comment_entry.grid(row=3, column=1, padx=5, pady=5)

        def save_property():
            new_key = key_var.get()
            new_value = value_var.get()
            new_comment = comment_var.get()

            # Rimuovi vecchia chiave se è cambiata
            if new_key != key:
                self.config.remove_option(self.current_section, key)

            # Imposta nuova chiave/valore
            self.config.set(self.current_section, new_key, new_value)

            # Salva il commento inline
            if new_comment:
                if not new_comment.startswith(('#', ';')):
                    new_comment = '; ' + new_comment
                self.config.set_inline_comment(self.current_section, new_key, new_comment)
            else:
                # Rimuovi eventuali commenti esistenti
                if self.current_section in self.config.inline_comments and new_key in self.config.inline_comments[
                    self.current_section]:
                    del self.config.inline_comments[self.current_section][new_key]

            self.update_property_list(self.current_section)
            dialog.destroy()

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Salva", command=save_property).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Annulla", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

        # Centra la finestra di dialogo
        self.center_window(dialog)

    def add_section(self):
        """Aggiunge una nuova sezione al file .ini."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Aggiungi Sezione")
        dialog.geometry("300x100")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Nome Sezione:").pack(padx=5, pady=5)

        section_var = tk.StringVar()
        section_entry = ttk.Entry(dialog, textvariable=section_var, width=30)
        section_entry.pack(padx=5, pady=5)

        def do_add_section():
            section_name = section_var.get().strip()
            if section_name:
                if not self.config.has_section(section_name):
                    self.config.add_section(section_name)
                    self.update_section_list()

                    # Seleziona la nuova sezione
                    sections = self.config.get_sections()
                    idx = sections.index(section_name)
                    self.section_listbox.selection_clear(0, tk.END)
                    self.section_listbox.selection_set(idx)
                    self.section_listbox.see(idx)
                    self.current_section = section_name
                    self.section_label_var.set(f"Sezione: [{section_name}]")
                    self.update_property_list(section_name)

                    self.status_var.set(f"Sezione '{section_name}' aggiunta")
                else:
                    messagebox.showwarning("Avviso", f"La sezione '{section_name}' esiste già")
            dialog.destroy()

        ttk.Button(dialog, text="Aggiungi", command=do_add_section).pack(pady=5)

        # Centra la finestra di dialogo
        self.center_window(dialog)

    def remove_section(self):
        """Rimuove la sezione selezionata dal file .ini."""
        if not self.current_section:
            messagebox.showwarning("Avviso", "Seleziona prima una sezione")
            return

        if messagebox.askyesno("Conferma", f"Rimuovere la sezione '{self.current_section}'?"):
            self.config.remove_section(self.current_section)
            self.update_section_list()
            self.property_tree.delete(*self.property_tree.get_children())
            self.current_section = None
            self.section_label_var.set("Nessuna sezione selezionata")
            self.status_var.set(f"Sezione rimossa")

    def add_property(self):
        """Aggiunge una nuova proprietà alla sezione selezionata."""
        if not self.current_section:
            messagebox.showwarning("Avviso", "Seleziona prima una sezione")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Aggiungi Proprietà")
        dialog.geometry("500x200")
        dialog.transient(self.root)
        dialog.grab_set()

        # Mostra la sezione corrente nella finestra di dialogo
        ttk.Label(dialog, text=f"Sezione: [{self.current_section}]", font=("", 10, "bold")).grid(
            row=0, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)

        ttk.Label(dialog, text="Chiave:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        key_var = tk.StringVar()
        key_entry = ttk.Entry(dialog, textvariable=key_var, width=50)
        key_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Valore:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        value_var = tk.StringVar()
        value_entry = ttk.Entry(dialog, textvariable=value_var, width=50)
        value_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Note:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        comment_var = tk.StringVar()
        comment_entry = ttk.Entry(dialog, textvariable=comment_var, width=50)
        comment_entry.grid(row=3, column=1, padx=5, pady=5)

        def do_add_property():
            key = key_var.get().strip()
            value = value_var.get()
            comment = comment_var.get()

            if not key:
                messagebox.showwarning("Avviso", "La chiave non può essere vuota")
                return

            self.config.set(self.current_section, key, value)

            # Salva il commento inline
            if comment:
                if not comment.startswith(('#', ';')):
                    comment = '; ' + comment
                self.config.set_inline_comment(self.current_section, key, comment)

            self.update_property_list(self.current_section)
            self.status_var.set(f"Proprietà '{key}' aggiunta a '{self.current_section}'")
            dialog.destroy()

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Aggiungi", command=do_add_property).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Annulla", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

        # Centra la finestra di dialogo
        self.center_window(dialog)

    def remove_property(self):
        """Rimuove la proprietà selezionata dalla sezione corrente."""
        if not self.current_section:
            messagebox.showwarning("Avviso", "Seleziona prima una sezione")
            return

        selected_items = self.property_tree.selection()
        if not selected_items:
            messagebox.showwarning("Avviso", "Seleziona prima una proprietà")
            return

        item = selected_items[0]
        key = self.property_tree.item(item, "values")[0]

        if messagebox.askyesno("Conferma", f"Rimuovere la proprietà '{key}'?"):
            self.config.remove_option(self.current_section, key)
            self.update_property_list(self.current_section)
            self.status_var.set(f"Proprietà '{key}' rimossa da '{self.current_section}'")


def main():
    """
    Funzione principale che avvia l'applicazione.

    Returns:
        None
    """
    root = tk.Tk()
    app = IniEditorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
