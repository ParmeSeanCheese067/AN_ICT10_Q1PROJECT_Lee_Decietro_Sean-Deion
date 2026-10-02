import json
from datetime import datetime
from js import document, window

receipt_items = []

def get_inventory():
    """Retrieve saved inventory array from LocalStorage."""
    data = window.localStorage.getItem("paldotrons_inventory")
    if data:
        try:
            return json.loads(data)
        except Exception:
            return []
    return []

def save_inventory(inv):
    """Save inventory array to LocalStorage."""
    window.localStorage.setItem("paldotrons_inventory", json.dumps(inv))

def create_sku(event=None):
    """Generate a new SKU code and save item details with unit price."""
    fmt = document.getElementById("format_type").value
    artist = document.getElementById("artist_name").value.strip()
    title = document.getElementById("album_title").value.strip()
    qty_str = document.getElementById("stock_qty").value.strip()
    price_str = document.getElementById("unit_price").value.strip()

    if not artist or not title:
        window.alert("Please fill in Artist and Title!")
        return

    try:
        price = float(price_str) if price_str else 0.0
    except ValueError:
        price = 0.0

    qty = qty_str if qty_str else "1"

    inv = get_inventory()
    artist_code = ''.join([c for c in artist if c.isalnum()])[:2].upper()
    title_code = ''.join([c for c in title if c.isalnum()])[:2].upper()
    seq_num = f"{len(inv) + 1:02d}"

    sku_code = f"{fmt}{artist_code}{title_code}{seq_num}"

    new_item = {
        "sku": sku_code,
        "format": fmt,
        "artist": artist,
        "title": title,
        "qty": qty,
        "price": price
    }

    inv.append(new_item)
    save_inventory(inv)

    sku_display = document.getElementById("sku_result")
    if sku_display:
        sku_display.innerText = sku_code

    render_inventory()

def render_inventory():
    """Render table rows in index.html inventory records."""
    tbody = document.getElementById("inventory_body")
    if not tbody:
        return

    tbody.innerHTML = ""
    inv = get_inventory()

    if not inv:
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:rgba(255,255,255,0.5);">No custom SKUs found. Generate your first album SKU above!</td></tr>'
        return

    for item in inv:
        tr = document.createElement("tr")
        price_val = float(item.get("price", 0.0))
        tr.innerHTML = f"""
            <td><strong>{item['sku']}</strong></td>
            <td>{item['format']}</td>
            <td>{item['artist']}</td>
            <td>{item['title']}</td>
            <td>{item['qty']}</td>
            <td>₱{price_val:,.2f}</td>
        """
        tbody.appendChild(tr)

def clear_inventory(event=None):
    """Clear all saved inventory."""
    window.localStorage.removeItem("paldotrons_inventory")
    sku_display = document.getElementById("sku_result")
    if sku_display:
        sku_display.innerText = "---"
    render_inventory()

def render_autofill_box(event=None):
    """Display autofill options for receipt scanning."""
    autofill_box = document.getElementById("autofill_box")
    autofill_list = document.getElementById("autofill_list")
    if not autofill_box or not autofill_list:
        return

    inv = get_inventory()
    if not inv:
        autofill_box.style.display = "none"
        return

    autofill_list.innerHTML = ""
    for item in inv:
        price_val = float(item.get("price", 0.0))
        div = document.createElement("div")
        div.className = "autofill-item"
        div.setAttribute("onclick", f"selectAutofillSku('{item['sku']}')")
        div.innerHTML = f"""
            <span class="autofill-sku">{item['sku']}</span>
            <div class="autofill-info">
                <span class="autofill-title">{item['artist']} - {item['title']}</span>
                <span class="autofill-subtitle">₱{price_val:,.2f} | Stock: {item['qty']}</span>
            </div>
        """
        autofill_list.appendChild(div)

    autofill_box.style.display = "block"

def scan_sku(event=None):
    """Add item to receipt and update total amount."""
    input_elem = document.getElementById("scan_sku")
    if not input_elem:
        return

    sku_code = input_elem.value.strip().upper()
    if not sku_code:
        return

    inv = get_inventory()
    matched = next((item for item in inv if item["sku"] == sku_code), None)

    if matched:
        receipt_items.append(matched)
        render_receipt()
        input_elem.value = ""
    else:
        window.alert(f"SKU {sku_code} not found in inventory!")

def render_receipt():
    """Update receipt items list and total price on receipts.html."""
    items_list = document.getElementById("receipt_items_list")
    total_elem = document.getElementById("receipt_total")
    date_elem = document.getElementById("receipt_date")

    if date_elem and date_elem.innerText == "---":
        date_elem.innerText = datetime.now().strftime("%B %d, %Y")

    if not items_list or not total_elem:
        return

    items_list.innerHTML = ""
    total = 0.0

    for item in receipt_items:
        price = float(item.get("price", 0.0))
        total += price

        row = document.createElement("div")
        row.className = "row"
        row.innerHTML = f"""
            <span class="label">{item['artist']} - {item['title']} ({item['sku']})</span>
            <span class="value">₱{price:,.2f}</span>
        """
        items_list.appendChild(row)

    total_elem.innerText = f"{total:,.2f}"


render_inventory()