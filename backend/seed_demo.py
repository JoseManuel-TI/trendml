import json, uuid, random, sys, os
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(__file__))

from database.session import engine, get_db
from database.config import settings
from models.entities import Product, PriceHistory, TrendSnapshot, WeeklyPrediction
from sqlalchemy.orm import Session

REAL_CATEGORIES = [
    {"id": "MLA1648", "name": "Computación"},
    {"id": "MLA1051", "name": "Celulares y Teléfonos"},
    {"id": "MLA1276", "name": "Deportes y Fitness"},
    {"id": "MLA5726", "name": "Electrodomésticos"},
    {"id": "MLA1000", "name": "Electrónica, Audio y Video"},
    {"id": "MLA1071", "name": "Animales y Mascotas"},
    {"id": "MLA1132", "name": "Juegos y Juguetes"},
    {"id": "MLA1430", "name": "Ropa y Accesorios"},
    {"id": "MLA5725", "name": "Accesorios para Vehículos"},
    {"id": "MLA1574", "name": "Hogar, Muebles y Jardín"},
]

PRODUCT_NAMES = {
    "MLA1648": ["Notebook Gamer", "PC Escritorio Intel i7", "Monitor 27\" 4K", "Teclado Mecánico RGB", "Mouse Inalámbrico", "Disco SSD 1TB", "Memoria RAM 32GB", "Webcam HD 1080p", "Hub USB-C", "Tablet 10\""],
    "MLA1051": ["Samsung Galaxy S24", "iPhone 15 Pro", "Motorola Edge 50", "Xiaomi Redmi Note 13", "Cargador Rápido 65W", "Funda Silicona", "Auriculares Bluetooth", "Samsung Galaxy A55", "Google Pixel 8", "Moto G84"],
    "MLA1276": ["Zapatillas Running", "Bicicleta Mountain Bike", "Pelota Fútbol", "Mancuernas 10kg", "Colchoneta Yoga", "Cinta Correr Eléctrica", "Patines 4 Ruedas", "Raqueta Tenis", "Traje de Baño", "Camiseta Deportiva"],
    "MLA5726": ["Heladera No Frost", "Lavarropas Automático", "Microondas 25L", "Cafetera Espresso", "Aspiradora Robot", "Licuadora 700W", "Plancha Vapor", "Ventilador Torre", "Aire Acondicionado Split", "Pava Eléctrica"],
    "MLA1000": ["Auriculares Sony XM5", "Parlante Bluetooth JBL", "TV 55\" 4K Smart", "Home Theater 5.1", "Barra Sonido 3.1", "Proyector HD 1080p", "Amplificador 200W", "Micrófono USB", "DJ Controlador", "Cable HDMI 2.1"],
    "MLA1071": ["Alimento Perro 20kg", "Cucha Perro Grande", "Arena Gato 10kg", "Rascador Gato", "Juguete Interactivo Perro", "Comedero Automático", "Collar Antipulgas", "Shampoo Mascota", "Cama Perro 90x60", "Pecera 60L"],
    "MLA1132": ["LEGO Technic Auto", "Monopoly Edición", "PlayStation 5 Slim", "Nintendo Switch OLED", "Control Xbox Inalámbrico", "Juego Mesa 6 en 1", "Pelota Saltarina", "Set Playa 8 piezas", "Mario Kart Deluxe", "Carrera Hot Wheels"],
    "MLA1430": ["Campera Impermeable", "Zapatillas Urbanas", "Mochila 40L", "Cartera Cuero", "Reloj Casio", "Anteojos Sol Polarizados", "Buzo Oversize", "Jean Slim Fit", "Vestido Floral", "Chomba Algodón"],
    "MLA5725": ["Cubre Asientos Auto", "Cámara Tablero", "Soporte Celular Auto", "Limpiabrisas Premium", "Kit Herramientas Auto", "Cargador Auto USB", "Organizador Baúl", "Fundas Volante", "Luces LED Auto", "Neumático 205/55 R16"],
    "MLA1574": ["Sofá 3 Cuerpos", "Mesa Comedor 6 p", "Silla Oficina Ergo", "Set Sábanas Queen", "Almohada Viscoelástica", "Estantería 5 niveles", "Lámpara LED Moderna", "Cortinas Blackout", "Jarrón Decorativo", "Tapete 150x200"],
}

PRICE_RANGES = {
    "MLA1648": (150000, 2500000), "MLA1051": (50000, 2500000),
    "MLA1276": (15000, 800000), "MLA5726": (80000, 3500000),
    "MLA1000": (20000, 1500000), "MLA1071": (5000, 350000),
    "MLA1132": (10000, 1200000), "MLA1430": (8000, 150000),
    "MLA5725": (5000, 200000), "MLA1574": (15000, 800000),
}

def seed_demo(db: Session):
    db.query(WeeklyPrediction).delete()
    db.query(TrendSnapshot).delete()
    db.query(PriceHistory).delete()
    db.query(Product).delete()
    db.commit()

    now = datetime.utcnow()
    products_list = []

    for cat in REAL_CATEGORIES:
        names = PRODUCT_NAMES.get(cat["id"], ["Producto"])[:10]
        pr = PRICE_RANGES.get(cat["id"], (10000, 100000))

        for i, name in enumerate(names):
            base_price = random.randint(pr[0], pr[1])
            pid = f"DEMO-{cat['id']}-{i+1:02d}"

            prod = Product(
                id=pid,
                title=name,
                seller_id="demo_seller",
                category_id=cat["id"],
                permalink=f"https://www.mercadolibre.com.ar/{cat['id']}/demo/{i}",
            )
            db.add(prod)
            db.flush()

            for d in range(30):
                day = now - timedelta(days=29 - d)
                variation = random.uniform(-0.12, 0.12)
                price = round(base_price * (1 + variation), 0)
                if d == 29:
                    price = round(base_price * random.uniform(0.95, 1.05), 0)

                ph = PriceHistory(
                    product_id=pid,
                    price=max(price, 100),
                    sold_quantity=random.randint(5, 200),
                    review_count=random.randint(0, 50),
                    score=round(random.uniform(3.0, 5.0), 1),
                    captured_at=day,
                    data_source="synthetic",
                )
                db.add(ph)

            ts = TrendSnapshot(
                product_id=pid,
                growth_rate=round(random.uniform(-15, 35), 1),
                predicted_sales_next_week=round(random.uniform(50, 500), 0),
                is_trending=random.random() > 0.7,
                captured_at=now,
            )
            db.add(ts)

            products_list.append({"id": pid, "title": name, "category": cat["name"], "price": base_price})

    db.commit()
    return products_list

if __name__ == "__main__":
    db = next(get_db())
    try:
        products = seed_demo(db)
        print(f"Seeded {len(products)} products:")
        for p in products:
            print(f"  {p['id']} | ${p['price']:>8} | [{p['category']}] {p['title']}")
    finally:
        db.close()
