# 🔌 Third-Party Integrations Guide

## Overview

Este documento detalha todas as integrações com serviços externos necessárias para um e-commerce enterprise-grade.

---

## 💳 Payment Gateway Integrations

### 1. Stripe Integration

**Use Cases**: Cartões de crédito, Apple Pay, Google Pay

**Implementation**:

```python
# services/payment-service/app/integrations/stripe_gateway.py

import stripe
from typing import Dict, Optional
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class StripeGateway:
    """Stripe payment gateway integration"""

    def __init__(self, api_key: str):
        stripe.api_key = api_key
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

    def create_payment_intent(
        self,
        amount: Decimal,
        currency: str,
        customer_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Create a payment intent

        Args:
            amount: Amount in smallest currency unit (cents)
            currency: Three-letter ISO currency code
            customer_id: Stripe customer ID (optional)
            metadata: Additional metadata

        Returns:
            Payment intent object
        """
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency.lower(),
                customer=customer_id,
                metadata=metadata or {},
                automatic_payment_methods={
                    'enabled': True,
                },
                # Enable 3D Secure
                payment_method_options={
                    'card': {
                        'request_three_d_secure': 'automatic'
                    }
                }
            )

            logger.info(f"Payment intent created: {intent.id}")
            return {
                'id': intent.id,
                'client_secret': intent.client_secret,
                'status': intent.status,
                'amount': intent.amount / 100,
                'currency': intent.currency
            }

        except stripe.error.CardError as e:
            logger.error(f"Card error: {e.user_message}")
            raise PaymentError(e.user_message)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            raise PaymentError("Payment processing failed")

    def capture_payment(self, payment_intent_id: str) -> bool:
        """Capture an authorized payment"""
        try:
            intent = stripe.PaymentIntent.capture(payment_intent_id)
            return intent.status == 'succeeded'
        except stripe.error.StripeError as e:
            logger.error(f"Capture failed: {str(e)}")
            return False

    def refund_payment(
        self,
        payment_intent_id: str,
        amount: Optional[Decimal] = None,
        reason: str = 'requested_by_customer'
    ) -> Dict:
        """
        Refund a payment

        Args:
            payment_intent_id: Payment intent ID
            amount: Amount to refund (partial refund if specified)
            reason: Refund reason

        Returns:
            Refund object
        """
        try:
            params = {
                'payment_intent': payment_intent_id,
                'reason': reason
            }

            if amount:
                params['amount'] = int(amount * 100)

            refund = stripe.Refund.create(**params)

            logger.info(f"Refund created: {refund.id}")
            return {
                'id': refund.id,
                'status': refund.status,
                'amount': refund.amount / 100
            }

        except stripe.error.StripeError as e:
            logger.error(f"Refund failed: {str(e)}")
            raise PaymentError("Refund processing failed")

    def handle_webhook(self, payload: bytes, signature: str) -> Dict:
        """
        Handle Stripe webhook events

        Args:
            payload: Request body
            signature: Stripe signature header

        Returns:
            Event data
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )

            logger.info(f"Webhook received: {event['type']}")

            if event['type'] == 'payment_intent.succeeded':
                payment_intent = event['data']['object']
                # Update order status
                self._handle_successful_payment(payment_intent)

            elif event['type'] == 'payment_intent.payment_failed':
                payment_intent = event['data']['object']
                # Handle failed payment
                self._handle_failed_payment(payment_intent)

            elif event['type'] == 'charge.refunded':
                charge = event['data']['object']
                # Handle refund
                self._handle_refund(charge)

            return event

        except ValueError as e:
            logger.error("Invalid payload")
            raise WebhookError("Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            logger.error("Invalid signature")
            raise WebhookError("Invalid signature")

    def create_customer(self, email: str, name: str, metadata: Dict) -> str:
        """Create a Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata
            )
            return customer.id
        except stripe.error.StripeError as e:
            logger.error(f"Customer creation failed: {str(e)}")
            raise PaymentError("Customer creation failed")

    def save_payment_method(
        self,
        customer_id: str,
        payment_method_id: str
    ) -> bool:
        """Attach payment method to customer for future use"""
        try:
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id
            )

            # Set as default payment method
            stripe.Customer.modify(
                customer_id,
                invoice_settings={
                    'default_payment_method': payment_method_id
                }
            )
            return True
        except stripe.error.StripeError as e:
            logger.error(f"Payment method attachment failed: {str(e)}")
            return False

# Usage in route
@payment_bp.route('/process', methods=['POST'])
@token_required
def process_payment(current_user):
    data = request.get_json()

    stripe_gateway = StripeGateway(app.config['STRIPE_SECRET_KEY'])

    result = stripe_gateway.create_payment_intent(
        amount=Decimal(data['amount']),
        currency=data.get('currency', 'USD'),
        customer_id=data.get('customer_id'),
        metadata={
            'order_id': data['order_id'],
            'user_id': current_user['user_id']
        }
    )

    return jsonify(result), 200
```

**Environment Variables**:
```env
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

---

### 2. PayPal Integration

**Use Cases**: PayPal checkout, PayPal Credit

```python
# services/payment-service/app/integrations/paypal_gateway.py

from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersCaptureRequest
import logging

logger = logging.getLogger(__name__)

class PayPalGateway:
    """PayPal payment gateway integration"""

    def __init__(self, client_id: str, client_secret: str, mode: str = 'sandbox'):
        if mode == 'live':
            environment = LiveEnvironment(client_id, client_secret)
        else:
            environment = SandboxEnvironment(client_id, client_secret)

        self.client = PayPalHttpClient(environment)

    def create_order(self, amount: Decimal, currency: str, metadata: Dict) -> Dict:
        """Create PayPal order"""
        request = OrdersCreateRequest()
        request.prefer('return=representation')

        request.request_body({
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {
                    "currency_code": currency,
                    "value": str(amount)
                },
                "reference_id": metadata.get('order_id'),
                "description": metadata.get('description', 'Order payment')
            }],
            "application_context": {
                "return_url": metadata.get('return_url'),
                "cancel_url": metadata.get('cancel_url')
            }
        })

        try:
            response = self.client.execute(request)

            return {
                'id': response.result.id,
                'status': response.result.status,
                'links': [
                    {
                        'rel': link.rel,
                        'href': link.href,
                        'method': link.method
                    }
                    for link in response.result.links
                ]
            }
        except Exception as e:
            logger.error(f"PayPal order creation failed: {str(e)}")
            raise PaymentError("PayPal order creation failed")

    def capture_order(self, order_id: str) -> Dict:
        """Capture PayPal order"""
        request = OrdersCaptureRequest(order_id)

        try:
            response = self.client.execute(request)

            return {
                'id': response.result.id,
                'status': response.result.status,
                'payer': response.result.payer
            }
        except Exception as e:
            logger.error(f"PayPal capture failed: {str(e)}")
            raise PaymentError("PayPal capture failed")
```

---

### 3. Brazilian Payment Methods (Pix, Boleto)

```python
# services/payment-service/app/integrations/brazil_payments.py

import requests
from datetime import datetime, timedelta

class BrazilPaymentsGateway:
    """Integration for Brazilian payment methods"""

    def __init__(self, api_key: str, merchant_id: str):
        self.api_key = api_key
        self.merchant_id = merchant_id
        self.base_url = "https://api.paymentgateway.com.br/v1"

    def generate_pix_qrcode(
        self,
        amount: Decimal,
        description: str,
        payer_info: Dict
    ) -> Dict:
        """
        Generate PIX QR Code for instant payment

        Returns:
            {
                'qr_code': 'base64_image',
                'pix_code': 'copy-paste string',
                'expiration': datetime
            }
        """
        payload = {
            "merchant_id": self.merchant_id,
            "amount": float(amount),
            "description": description,
            "payer": {
                "name": payer_info['name'],
                "tax_id": payer_info['cpf'],  # CPF
                "email": payer_info['email']
            },
            "expiration_minutes": 30
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            f"{self.base_url}/pix/qrcode",
            json=payload,
            headers=headers
        )

        if response.status_code == 201:
            data = response.json()
            return {
                'qr_code_base64': data['qr_code_base64'],
                'pix_copy_paste': data['pix_code'],
                'expiration': data['expires_at'],
                'transaction_id': data['id']
            }
        else:
            raise PaymentError("PIX QR Code generation failed")

    def generate_boleto(
        self,
        amount: Decimal,
        due_date: datetime,
        payer_info: Dict
    ) -> Dict:
        """
        Generate Boleto (Brazilian bank slip)

        Returns:
            {
                'barcode': '12345...',
                'pdf_url': 'https://...',
                'due_date': datetime
            }
        """
        payload = {
            "merchant_id": self.merchant_id,
            "amount": float(amount),
            "due_date": due_date.isoformat(),
            "payer": {
                "name": payer_info['name'],
                "tax_id": payer_info['cpf'],
                "email": payer_info['email'],
                "address": payer_info['address']
            },
            "instructions": "Não aceitar após vencimento"
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            f"{self.base_url}/boleto/generate",
            json=payload,
            headers=headers
        )

        if response.status_code == 201:
            data = response.json()
            return {
                'barcode': data['barcode'],
                'digitable_line': data['digitable_line'],
                'pdf_url': data['pdf_url'],
                'due_date': data['due_date'],
                'transaction_id': data['id']
            }
        else:
            raise PaymentError("Boleto generation failed")

    def check_payment_status(self, transaction_id: str) -> str:
        """Check PIX/Boleto payment status"""
        headers = {"Authorization": f"Bearer {self.api_key}"}

        response = requests.get(
            f"{self.base_url}/transactions/{transaction_id}",
            headers=headers
        )

        if response.status_code == 200:
            return response.json()['status']
        return 'unknown'
```

---

## 🚚 Shipping & Logistics Integration

### 1. Correios (Brazilian Post Office)

```python
# services/shipping-service/app/integrations/correios.py

import requests
from typing import Dict, List
from decimal import Decimal

class CorreiosIntegration:
    """Integration with Correios API"""

    def __init__(self, contract_code: str, password: str):
        self.contract_code = contract_code
        self.password = password
        self.base_url = "https://api.correios.com.br/v1"

    def calculate_shipping(
        self,
        origin_zip: str,
        destination_zip: str,
        weight_kg: Decimal,
        dimensions: Dict,  # length, width, height in cm
        service_codes: List[str] = ['04014', '04510']  # SEDEX, PAC
    ) -> List[Dict]:
        """
        Calculate shipping cost and delivery time

        Service codes:
        - 04014: SEDEX (express)
        - 04510: PAC (standard)
        - 04782: SEDEX 12
        """
        results = []

        for service_code in service_codes:
            payload = {
                "cepOrigem": origin_zip.replace('-', ''),
                "cepDestino": destination_zip.replace('-', ''),
                "peso": float(weight_kg),
                "formato": 1,  # Box format
                "comprimento": dimensions['length'],
                "altura": dimensions['height'],
                "largura": dimensions['width'],
                "servicoCodigo": service_code
            }

            response = requests.post(
                f"{self.base_url}/precos/calcular",
                json=payload,
                auth=(self.contract_code, self.password)
            )

            if response.status_code == 200:
                data = response.json()
                results.append({
                    'service_code': service_code,
                    'service_name': data['servicoNome'],
                    'price': Decimal(data['valor']),
                    'delivery_days': data['prazoEntrega'],
                    'delivery_home': data['entregaDomiciliar'],
                    'saturday_delivery': data['entregaSabado']
                })

        return results

    def track_package(self, tracking_code: str) -> List[Dict]:
        """Track package by tracking code"""
        response = requests.get(
            f"{self.base_url}/rastreamento/{tracking_code}",
            auth=(self.contract_code, self.password)
        )

        if response.status_code == 200:
            events = response.json()['eventos']
            return [
                {
                    'date': event['data'],
                    'location': event['local'],
                    'status': event['status'],
                    'description': event['descricao']
                }
                for event in events
            ]
        return []

    def create_shipping_label(
        self,
        order_data: Dict,
        service_code: str
    ) -> Dict:
        """Generate shipping label"""
        payload = {
            "contrato": self.contract_code,
            "servico": service_code,
            "remetente": {
                "nome": order_data['sender']['name'],
                "endereco": order_data['sender']['address'],
                "cep": order_data['sender']['zip_code']
            },
            "destinatario": {
                "nome": order_data['recipient']['name'],
                "endereco": order_data['recipient']['address'],
                "cep": order_data['recipient']['zip_code']
            },
            "dimensoes": order_data['dimensions'],
            "peso": order_data['weight']
        }

        response = requests.post(
            f"{self.base_url}/etiquetas/gerar",
            json=payload,
            auth=(self.contract_code, self.password)
        )

        if response.status_code == 201:
            data = response.json()
            return {
                'tracking_code': data['codigoRastreio'],
                'label_url': data['urlEtiqueta'],
                'posting_card_url': data['urlCartaoPostagem']
            }
        else:
            raise ShippingError("Label generation failed")
```

### 2. FedEx / DHL Integration

```python
# services/shipping-service/app/integrations/fedex.py

from fedex.services.rate_service import FedexRateServiceRequest
from fedex.services.track_service import FedexTrackServiceRequest

class FedExIntegration:
    """FedEx shipping integration"""

    def __init__(self, key: str, password: str, account: str, meter: str):
        self.key = key
        self.password = password
        self.account = account
        self.meter = meter

    def get_rates(
        self,
        origin: Dict,
        destination: Dict,
        package_info: Dict
    ) -> List[Dict]:
        """Get shipping rates"""
        rate_request = FedexRateServiceRequest(self.get_config())

        # Set shipment details
        rate_request.RequestedShipment.DropoffType = 'REGULAR_PICKUP'
        rate_request.RequestedShipment.ServiceType = 'FEDEX_GROUND'
        rate_request.RequestedShipment.PackagingType = 'YOUR_PACKAGING'

        # Shipper
        rate_request.RequestedShipment.Shipper.Address.PostalCode = origin['zip']
        rate_request.RequestedShipment.Shipper.Address.CountryCode = origin['country']

        # Recipient
        rate_request.RequestedShipment.Recipient.Address.PostalCode = destination['zip']
        rate_request.RequestedShipment.Recipient.Address.CountryCode = destination['country']

        # Package
        package = rate_request.create_wsdl_object_of_type('RequestedPackageLineItem')
        package.Weight.Value = package_info['weight']
        package.Weight.Units = 'KG'
        package.Dimensions.Length = package_info['length']
        package.Dimensions.Width = package_info['width']
        package.Dimensions.Height = package_info['height']
        package.Dimensions.Units = 'CM'

        rate_request.RequestedShipment.RequestedPackageLineItems = [package]

        # Execute request
        rate_request.send_request()

        return self._parse_rates(rate_request.response)
```

---

## 🔍 Address Validation & Geocoding

### 1. ViaCEP (Brazil)

```python
# shared/utils/address_utils.py

import requests
from typing import Optional, Dict

class ViaCEPClient:
    """ViaCEP API client for Brazilian address validation"""

    BASE_URL = "https://viacep.com.br/ws"

    @staticmethod
    def get_address_by_cep(cep: str) -> Optional[Dict]:
        """
        Get address details by CEP (Brazilian ZIP code)

        Args:
            cep: CEP in format 12345-678 or 12345678

        Returns:
            {
                'cep': '01310-100',
                'logradouro': 'Avenida Paulista',
                'complemento': '',
                'bairro': 'Bela Vista',
                'localidade': 'São Paulo',
                'uf': 'SP',
                'ibge': '3550308',
                'gia': '1004',
                'ddd': '11',
                'siafi': '7107'
            }
        """
        cep_clean = cep.replace('-', '').replace('.', '')

        if len(cep_clean) != 8 or not cep_clean.isdigit():
            return None

        try:
            response = requests.get(
                f"{ViaCEPClient.BASE_URL}/{cep_clean}/json/",
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                if 'erro' not in data:
                    return data
        except requests.RequestException:
            pass

        return None

    @staticmethod
    def find_addresses_by_query(
        state: str,
        city: str,
        street: str
    ) -> List[Dict]:
        """
        Search addresses by state, city and street name

        Args:
            state: State code (e.g., 'SP')
            city: City name
            street: Street name

        Returns:
            List of matching addresses
        """
        try:
            response = requests.get(
                f"{ViaCEPClient.BASE_URL}/{state}/{city}/{street}/json/",
                timeout=5
            )

            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass

        return []

# Usage in User Service
@users_bp.route('/<int:user_id>/addresses', methods=['POST'])
@token_required
def add_address(current_user, user_id):
    data = request.get_json()

    # Validate CEP
    if 'postal_code' in data and data['country'] == 'BR':
        address_info = ViaCEPClient.get_address_by_cep(data['postal_code'])

        if not address_info:
            return jsonify({'error': 'Invalid CEP'}), 400

        # Auto-fill address data
        data['city'] = address_info['localidade']
        data['state'] = address_info['uf']
        data['street_address'] = address_info['logradouro']
        data['neighborhood'] = address_info['bairro']

    # Save address...
```

### 2. Google Maps Geocoding

```python
# shared/utils/geocoding.py

import googlemaps
from typing import Tuple, Optional

class GeocodingService:
    """Google Maps geocoding service"""

    def __init__(self, api_key: str):
        self.gmaps = googlemaps.Client(key=api_key)

    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Convert address to coordinates

        Returns:
            (latitude, longitude) or None
        """
        try:
            result = self.gmaps.geocode(address)
            if result:
                location = result[0]['geometry']['location']
                return (location['lat'], location['lng'])
        except Exception as e:
            logger.error(f"Geocoding failed: {str(e)}")

        return None

    def reverse_geocode(
        self,
        lat: float,
        lng: float
    ) -> Optional[Dict]:
        """Convert coordinates to address"""
        try:
            result = self.gmaps.reverse_geocode((lat, lng))
            if result:
                return result[0]
        except Exception as e:
            logger.error(f"Reverse geocoding failed: {str(e)}")

        return None

    def calculate_distance(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float]
    ) -> Optional[Dict]:
        """
        Calculate distance and duration between two points

        Returns:
            {
                'distance': {'text': '10 km', 'value': 10000},
                'duration': {'text': '15 mins', 'value': 900}
            }
        """
        try:
            result = self.gmaps.distance_matrix(
                origins=[origin],
                destinations=[destination],
                mode='driving'
            )

            if result['rows']:
                element = result['rows'][0]['elements'][0]
                if element['status'] == 'OK':
                    return {
                        'distance': element['distance'],
                        'duration': element['duration']
                    }
        except Exception as e:
            logger.error(f"Distance calculation failed: {str(e)}")

        return None
```

---

## 📧 Email & Notification Services

### 1. SendGrid Integration

```python
# services/notification-service/app/integrations/sendgrid.py

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class SendGridService:
    """SendGrid email service"""

    def __init__(self, api_key: str, from_email: str):
        self.client = SendGridAPIClient(api_key)
        self.from_email = from_email

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_text: str = None,
        attachments: List[Dict] = None
    ) -> bool:
        """Send email"""
        try:
            message = Mail(
                from_email=Email(self.from_email),
                to_emails=To(to_email),
                subject=subject,
                plain_text_content=plain_text,
                html_content=html_content
            )

            # Add attachments
            if attachments:
                for attachment in attachments:
                    message.attachment = attachment

            response = self.client.send(message)

            logger.info(f"Email sent to {to_email}: {response.status_code}")
            return response.status_code in [200, 202]

        except Exception as e:
            logger.error(f"Email sending failed: {str(e)}")
            return False

    def send_template_email(
        self,
        to_email: str,
        template_id: str,
        dynamic_data: Dict
    ) -> bool:
        """Send email using SendGrid template"""
        try:
            message = Mail(
                from_email=Email(self.from_email),
                to_emails=To(to_email)
            )
            message.template_id = template_id
            message.dynamic_template_data = dynamic_data

            response = self.client.send(message)
            return response.status_code in [200, 202]

        except Exception as e:
            logger.error(f"Template email sending failed: {str(e)}")
            return False

# Email Templates
ORDER_CONFIRMATION_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .header { background-color: #4CAF50; color: white; padding: 20px; }
        .content { padding: 20px; }
        .order-details { background-color: #f9f9f9; padding: 15px; margin: 20px 0; }
        .footer { background-color: #f1f1f1; padding: 10px; text-align: center; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Order Confirmation</h1>
    </div>
    <div class="content">
        <p>Hello {{customer_name}},</p>
        <p>Thank you for your order! Your order number is <strong>{{order_number}}</strong>.</p>

        <div class="order-details">
            <h3>Order Details:</h3>
            <ul>
                {{#each items}}
                <li>{{name}} - Quantity: {{quantity}} - ${{price}}</li>
                {{/each}}
            </ul>
            <p><strong>Total: ${{total}}</strong></p>
        </div>

        <p>Estimated delivery: {{delivery_date}}</p>
        <p>Track your order: <a href="{{tracking_url}}">Click here</a></p>
    </div>
    <div class="footer">
        <p>© 2025 Your E-commerce. All rights reserved.</p>
    </div>
</body>
</html>
"""
```

### 2. SMS Integration (Twilio)

```python
# services/notification-service/app/integrations/twilio_sms.py

from twilio.rest import Client
from typing import Optional

class TwilioSMSService:
    """Twilio SMS service"""

    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.client = Client(account_sid, auth_token)
        self.from_number = from_number

    def send_sms(
        self,
        to_number: str,
        message: str
    ) -> Optional[str]:
        """
        Send SMS

        Returns:
            Message SID if successful
        """
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )

            logger.info(f"SMS sent to {to_number}: {message.sid}")
            return message.sid

        except Exception as e:
            logger.error(f"SMS sending failed: {str(e)}")
            return None

    def send_otp(self, to_number: str) -> Optional[str]:
        """Send OTP code"""
        # Generate 6-digit OTP
        import random
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

        message = f"Your verification code is: {otp}. Valid for 10 minutes."

        if self.send_sms(to_number, message):
            return otp
        return None
```

---

## 🤖 AI/ML Services

### 1. Recommendation Engine (AWS Personalize)

```python
# services/recommendation-service/app/ml_engine.py

import boto3
from typing import List, Dict

class RecommendationEngine:
    """Product recommendation engine"""

    def __init__(self):
        self.personalize = boto3.client('personalize-runtime')
        self.campaign_arn = os.getenv('AWS_PERSONALIZE_CAMPAIGN_ARN')

    def get_recommendations(
        self,
        user_id: str,
        num_results: int = 10,
        context: Dict = None
    ) -> List[str]:
        """Get personalized product recommendations"""
        try:
            response = self.personalize.get_recommendations(
                campaignArn=self.campaign_arn,
                userId=str(user_id),
                numResults=num_results,
                context=context or {}
            )

            return [item['itemId'] for item in response['itemList']]

        except Exception as e:
            logger.error(f"Recommendation failed: {str(e)}")
            # Fallback to trending products
            return self._get_trending_products(num_results)

    def track_event(
        self,
        user_id: str,
        event_type: str,
        item_id: str,
        properties: Dict = None
    ):
        """Track user interaction for ML training"""
        try:
            self.personalize_events = boto3.client('personalize-events')

            self.personalize_events.put_events(
                trackingId=os.getenv('AWS_PERSONALIZE_TRACKING_ID'),
                userId=str(user_id),
                sessionId=request.session.get('session_id'),
                eventList=[{
                    'eventType': event_type,
                    'sentAt': datetime.utcnow().isoformat(),
                    'itemId': item_id,
                    'properties': json.dumps(properties or {})
                }]
            )
        except Exception as e:
            logger.error(f"Event tracking failed: {str(e)}")
```

---

## 🔗 Blockchain Integration

### 1. Ethereum Smart Contract

```python
# services/blockchain-service/app/ethereum_client.py

from web3 import Web3
from eth_account import Account
import json

class EthereumClient:
    """Ethereum blockchain client"""

    def __init__(self, provider_url: str, contract_address: str):
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        self.contract_address = contract_address

        # Load contract ABI
        with open('contracts/OrderRegistry.json', 'r') as f:
            contract_abi = json.load(f)['abi']

        self.contract = self.w3.eth.contract(
            address=contract_address,
            abi=contract_abi
        )

    def register_order(
        self,
        order_id: int,
        order_hash: str,
        private_key: str
    ) -> str:
        """
        Register order on blockchain for immutability

        Returns:
            Transaction hash
        """
        try:
            account = Account.from_key(private_key)

            # Build transaction
            txn = self.contract.functions.registerOrder(
                orderId=order_id,
                orderHash=order_hash
            ).buildTransaction({
                'from': account.address,
                'nonce': self.w3.eth.get_transaction_count(account.address),
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price
            })

            # Sign and send
            signed_txn = self.w3.eth.account.sign_transaction(txn, private_key)
            txn_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

            return txn_hash.hex()

        except Exception as e:
            logger.error(f"Blockchain registration failed: {str(e)}")
            raise

    def verify_order(self, order_id: int, order_hash: str) -> bool:
        """Verify order integrity against blockchain"""
        try:
            stored_hash = self.contract.functions.getOrderHash(order_id).call()
            return stored_hash == order_hash
        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
            return False
```

**Smart Contract (Solidity)**:

```solidity
// contracts/OrderRegistry.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract OrderRegistry {
    mapping(uint256 => bytes32) private orderHashes;
    mapping(uint256 => uint256) private timestamps;

    event OrderRegistered(uint256 indexed orderId, bytes32 orderHash, uint256 timestamp);

    function registerOrder(uint256 orderId, bytes32 orderHash) public {
        require(orderHashes[orderId] == bytes32(0), "Order already registered");

        orderHashes[orderId] = orderHash;
        timestamps[orderId] = block.timestamp;

        emit OrderRegistered(orderId, orderHash, block.timestamp);
    }

    function getOrderHash(uint256 orderId) public view returns (bytes32) {
        return orderHashes[orderId];
    }

    function getTimestamp(uint256 orderId) public view returns (uint256) {
        return timestamps[orderId];
    }
}
```

---

## 📊 Analytics & Monitoring

### 1. Google Analytics 4

```python
# shared/utils/analytics.py

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest

class GoogleAnalytics4Client:
    """Google Analytics 4 integration"""

    def __init__(self, property_id: str):
        self.client = BetaAnalyticsDataClient()
        self.property_id = property_id

    def track_event(
        self,
        event_name: str,
        user_id: str,
        parameters: Dict
    ):
        """Track custom event"""
        # Use Measurement Protocol v2
        import requests

        payload = {
            'client_id': user_id,
            'events': [{
                'name': event_name,
                'params': parameters
            }]
        }

        requests.post(
            f"https://www.google-analytics.com/mp/collect?"
            f"measurement_id={self.measurement_id}&api_secret={self.api_secret}",
            json=payload
        )
```

---

**Environment Variables Summary**:

```env
# Payment Gateways
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

PAYPAL_CLIENT_ID=...
PAYPAL_CLIENT_SECRET=...
PAYPAL_MODE=live

# Shipping
CORREIOS_CONTRACT_CODE=...
CORREIOS_PASSWORD=...
FEDEX_KEY=...
FEDEX_PASSWORD=...

# Notifications
SENDGRID_API_KEY=...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=...

# Maps & Geocoding
GOOGLE_MAPS_API_KEY=...

# ML/AI
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_PERSONALIZE_CAMPAIGN_ARN=...

# Blockchain
ETHEREUM_PROVIDER_URL=https://mainnet.infura.io/v3/...
ETHEREUM_CONTRACT_ADDRESS=0x...
ETHEREUM_PRIVATE_KEY=...

# Analytics
GOOGLE_ANALYTICS_PROPERTY_ID=...
GOOGLE_ANALYTICS_MEASUREMENT_ID=...
```

---

**Next Steps**: Implementar cada integração incrementalmente, começando pelas essenciais (payment, shipping) e depois adicionar as avançadas (ML, blockchain).
