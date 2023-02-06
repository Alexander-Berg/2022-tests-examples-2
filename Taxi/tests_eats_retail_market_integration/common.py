from typing import Dict
from typing import List
from typing import Optional


class NmnProduct:
    public_id: str
    origin_id: str
    name: str
    description: str
    barcodes: List[str]
    is_choosable: bool = True
    measure: Optional[tuple] = None
    volume: Optional[tuple] = None
    is_catch_weight: bool = False
    quantum: Optional[float] = None
    adult: bool = False
    shipping_type: str = 'pickup'
    images: List[tuple]
    vendor_name: Optional[str] = None
    vendor_country: Optional[str] = None
    product_brand: Optional[str] = None
    processing_type: Optional[str] = None
    is_sku: bool = False
    carbohydrates: Optional[str] = None
    proteins: Optional[str] = None
    fats: Optional[str] = None
    calories: Optional[str] = None
    storage_requirements: Optional[str] = None
    expiration_info: Optional[str] = None
    in_stock: Optional[int] = None
    is_available: bool = True
    price: int = 1
    old_price: Optional[int] = None
    vat: Optional[str] = None
    vendor_code: Optional[str] = None
    location: Optional[str] = None

    def __init__(
            self,
            public_id,
            is_catch_weight=None,
            quantum=None,
            measure=None,
            volume=None,
            is_available=None,
            in_stock=None,
            price=None,
            old_price=None,
    ):
        # Instantiate mutable objects
        self.barcodes = []
        self.images = []

        self.public_id = public_id
        if is_catch_weight is not None:
            self.is_catch_weight = is_catch_weight
        if measure is not None:
            self.measure = measure
        if volume is not None:
            self.volume = volume
        if is_available is not None:
            self.is_available = is_available
        if in_stock is not None:
            self.in_stock = in_stock
        if quantum is not None:
            self.quantum = quantum
        if price is not None:
            self.price = price
        if old_price is not None:
            self.old_price = old_price

        self._generate_default_required_fields()

    def _generate_default_required_fields(self):
        for attr_name in ['name', 'origin_id', 'description']:
            if not hasattr(self, attr_name):
                setattr(self, attr_name, f'{attr_name}_{self.public_id}')


class NmnPlace:
    place_id: str
    slug: str
    brand_id: int

    product_public_id_to_data: Dict[str, 'NmnProduct']

    def __init__(self, place_id, slug, brand_id):
        # Instantiate mutable objects
        self.product_public_id_to_data = dict()

        self.place_id = place_id
        self.slug = slug
        self.brand_id = brand_id

    def add_product(self, product: NmnProduct):
        product_public_id = product.public_id
        assert product_public_id not in self.product_public_id_to_data

        self.product_public_id_to_data[product_public_id] = product
