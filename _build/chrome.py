"""Header chrome dikongsi antara gen_home.py dan gen.py.
Satu sumber sahaja — kalau header berubah, ia berubah di SEMUA halaman."""

CHEV = ('<svg width="10" height="10" viewBox="0 0 16 16" fill="none" stroke="currentColor" '
        'stroke-width="1.6" aria-hidden="true"><path d="M4 6l4 4 4-4"/></svg>')

SEARCH = ('<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" '
          'stroke-width="1.5" aria-hidden="true"><circle cx="7" cy="7" r="4.5"/><path d="M10.5 10.5L14 14"/></svg>')

ICON_QUOTE = ('<svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" '
              'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
              '<path d="M5 2.5h7l3.5 3.5v11.5H5z"/><path d="M11.5 2.5V6H15"/>'
              '<path d="M7.5 10.5h5M7.5 13.5h3.5"/></svg>')

def _svg(body):
    return ('<svg width="18" height="18" viewBox="0 0 20 20" fill="none" '
            'stroke="currentColor" stroke-width="1.4" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true">' + body + '</svg>')

CAT_ICONS = {
  # bottle with pump neck
  "bottles":   _svg('<path d="M8 2h4v3H8z"/><path d="M7 5h6l1 4v8a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V9z"/>'),
  # lipstick bullet
  "lips":      _svg('<path d="M8 7l1-4h2l1 4"/><rect x="7.5" y="7" width="5" height="10" rx="1"/>'),
  # squeeze tube
  "tubes":     _svg('<path d="M7 3h6l-1 14a1 1 0 0 1-1 1H9a1 1 0 0 1-1-1z"/><path d="M7 6h6"/>'),
  # jar with lid
  "jars":      _svg('<rect x="5" y="7" width="10" height="10" rx="1.5"/><path d="M6 7V5h8v2"/>'),
  # compact / powder disc
  "powder-colour": _svg('<circle cx="10" cy="10" r="6.5"/><circle cx="10" cy="10" r="2.5"/>'),
  # dropper pipette
  "droppers":  _svg('<path d="M11 3l6 6-2 2-6-6z"/><path d="M9 5l-4 8 3 3 8-4"/>'),
  # closed box
  "boxes":     _svg('<path d="M3 7l7-4 7 4v6l-7 4-7-4z"/><path d="M3 7l7 4 7-4M10 11v6"/>'),
  # screw cap
  "caps":      _svg('<rect x="5" y="6" width="10" height="8" rx="1.5"/><path d="M7 6V4h6v2M7 14v2h6v-2"/>'),
  # pouch / sachet
  "sachets":   _svg('<path d="M5 4h10v13a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1z"/><path d="M5 7h10"/>'),
  # brush applicator
  "accessories": _svg('<path d="M13 3l4 4-8 8-4 1 1-4z"/><path d="M11 5l4 4"/>'),
  # machine / gear
  "equipment": _svg('<circle cx="10" cy="10" r="3"/><path d="M10 2v2M10 16v2M2 10h2M16 10h2M4.5 4.5l1.5 1.5M14 14l1.5 1.5M15.5 4.5L14 6M6 14l-1.5 1.5"/>'),
}

BESPOKE_ICON = _svg('<path d="M4 15l6-6 3 3-6 6H4z"/><path d="M13 6l1-1a2 2 0 0 1 3 3l-1 1z"/>')
