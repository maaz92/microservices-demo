import os
from demo_pb2_grpc import (
    AdServiceStub,
    CartServiceStub,
    ProductCatalogServiceStub,
    CheckoutServiceStub,
    CurrencyServiceStub,
    RecommendationServiceStub,
    ShippingServiceStub,
)
import demo_pb2
import grpc

USER_CURRENCY = "USD"
ADDRESS = demo_pb2.Address(
    street_address="1600 Amphitheatre Parkway",
    city="Mountain View",
    state="CA",
    country="United States",
    zip_code=94043,
)
EMAIL = "someone@example.com"
CREDIT_CARD = demo_pb2.CreditCardInfo(
    credit_card_number="4432801561520454",
    credit_card_cvv=672,
    credit_card_expiration_year=2026,
    credit_card_expiration_month=1,
)


class CartServiceClient:
    def __init__(self):
        cart_service_url = os.getenv("CART_SERVICE_ADDR", "cartservice:7070")
        cart_service_channel = grpc.insecure_channel(cart_service_url)
        self.cart_stub = CartServiceStub(cart_service_channel)

    def get_cart(self, user_id: str):
        get_cart_request = demo_pb2.GetCartRequest(user_id=user_id)
        get_cart_response = self.cart_stub.GetCart(get_cart_request)
        return get_cart_response

    def add_item_to_cart(self, user_id: str, product_id: str, quantity: int):
        add_item_request = demo_pb2.AddItemRequest(
            user_id=user_id,
            item=demo_pb2.CartItem(product_id=product_id, quantity=quantity),
        )
        self.cart_stub.AddItem(add_item_request)

    def empty_cart(self, user_id: str):
        empty_cart_request = demo_pb2.EmptyCartRequest(user_id=user_id)
        self.cart_stub.EmptyCart(empty_cart_request)


class ProductCatalogServiceClient:
    def __init__(self):
        product_catalog_service_url = os.getenv(
            "PRODUCT_CATALOG_SERVICE_ADDR", "productcatalogservice:3550"
        )
        product_catalog_service_channel = grpc.insecure_channel(
            product_catalog_service_url
        )
        self.product_catalog_service_stub = ProductCatalogServiceStub(
            product_catalog_service_channel
        )

    def list_product(self):
        list_product_request = demo_pb2.Empty()
        list_product_response = self.product_catalog_service_stub.ListProducts(
            list_product_request
        )
        return list_product_response

    def get_product(self, id: str):
        get_product_request = demo_pb2.GetProductRequest(id=id)
        get_product_response = self.product_catalog_service_stub.GetProduct(
            get_product_request
        )
        return get_product_response

    def search_product(self, query: str):
        search_product_request = demo_pb2.SearchProductsRequest(query=query)
        search_product_response = self.product_catalog_service_stub.SearchProducts(
            search_product_request
        )
        return search_product_response


class CheckoutServiceClient:
    def __init__(self):
        checkout_service_url = os.getenv("CHECKOUT_SERVICE_ADDR", "checkoutservice:5050")
        checkout_service_channel = grpc.insecure_channel(checkout_service_url)
        self.checkout_service_stub = CheckoutServiceStub(checkout_service_channel)

    def place_order(self, user_id: str):
        place_order_request = demo_pb2.PlaceOrderRequest(
            user_id=user_id,
            user_currency=USER_CURRENCY,
            address=ADDRESS,
            email=EMAIL,
            credit_card=CREDIT_CARD,
        )
        place_order_response = self.checkout_service_stub.PlaceOrder(place_order_request)
        return place_order_response


class CurrencyServiceClient:
    def __init__(self):
        currency_service_url = os.getenv("CURRENCY_SERVICE_ADDR", "currencyservice:7000")
        currency_service_channel = grpc.insecure_channel(currency_service_url)
        self.currency_service_stub = CurrencyServiceStub(currency_service_channel)

    def get_supported_currencies(self):
        get_supported_currencies_request = demo_pb2.Empty()
        get_supported_currencies_response = (
            self.currency_service_stub.GetSupportedCurrencies(
                get_supported_currencies_request
            )
        )
        return get_supported_currencies_response

    def convert(self, amount: float, from_currency_code: str, to_currency_code: str):
        from_money = demo_pb2.Money(
            currency_code=from_currency_code,
            units=int(amount),
            nanos=int((amount % 1) * 1e9),
        )
        convert_currency_request = demo_pb2.CurrencyConversionRequest()
        setattr(convert_currency_request, "from", from_money)
        convert_currency_request.to_code = to_currency_code
        convert_currency_response = self.currency_service_stub.Convert(
            convert_currency_request
        )
        return convert_currency_response


class RecommendationServiceClient:
    def __init__(self):
        recommendation_service_url = os.getenv(
            "RECOMMENDATION_SERVICE_ADDR", "recommendationservice:8080"
        )
        recommendation_service_channel = grpc.insecure_channel(
            recommendation_service_url
        )
        self.recommendation_service_stub = RecommendationServiceStub(
            recommendation_service_channel
        )

    def list_recommendations(self, user_id: str, product_ids: list[str]):
        list_recommendations_request = demo_pb2.ListRecommendationsRequest(
            user_id=user_id, product_ids=product_ids
        )
        list_recommendations_response = self.recommendation_service_stub.ListRecommendations(
            list_recommendations_request
        )
        return list_recommendations_response


class ShippingServiceClient:
    def __init__(self):
        shipping_service_url = os.getenv("SHIPPING_SERVICE_ADDR", "shippingservice:50051")
        shipping_service_channel = grpc.insecure_channel(shipping_service_url)
        self.shipping_service_stub = ShippingServiceStub(shipping_service_channel)

    def get_quote(self, product_ids: list[str], quantities: list[str]):
        get_quote_request = demo_pb2.GetQuoteRequest(address=ADDRESS)
        get_quote_request.items.extend(
            [
                demo_pb2.CartItem(product_id=product_id, quantity=quantity)
                for product_id, quantity in zip(product_ids, quantities)
            ]
        )
        get_quote_response = self.shipping_service_stub.GetQuote(get_quote_request)
        return get_quote_response


class AdServiceClient:
    def __init__(self):
        ad_service_url = os.getenv("AD_SERVICE_ADDR", "adservice:9555")
        ad_service_channel = grpc.insecure_channel(ad_service_url)
        self.ad_service_stub = AdServiceStub(ad_service_channel)

    def get_ads(self):
        ad_request = demo_pb2.AdRequest()
        ad_response = self.ad_service_stub.GetAds(ad_request)
        return ad_response


cart_service_client = CartServiceClient()
product_catalog_service_client = ProductCatalogServiceClient()
checkout_service_client = CheckoutServiceClient()
currency_service_client = CurrencyServiceClient()
recommendation_service_client = RecommendationServiceClient()
shipping_service_client = ShippingServiceClient()
ad_service_client = AdServiceClient()
