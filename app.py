import os
from datetime import datetime
from typing import Any, Dict, Tuple

import requests
import streamlit as st


DEFAULT_CURRENCIES = [
    "USD",
    "EUR",
    "INR",
    "GBP",
    "JPY",
    "AUD",
    "CAD",
    "CHF",
    "CNY",
    "SGD",
    "NZD",
    "AED",
    "SAR",
    "ZAR",
    "BRL",
]


def get_conversion_factor(api_key: str, base_currency: str, target_currency: str) -> Dict[str, Any]:
    """Fetch currency conversion details from ExchangeRate-API."""
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{base_currency}/{target_currency}"
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    payload = response.json()

    if payload.get("result") != "success":
        error_type = payload.get("error-type", "unknown_error")
        raise ValueError(f"API error: {error_type}")

    return payload


def convert(base_currency_value: float, conversion_rate: float) -> float:
    """Convert amount using conversion rate."""
    return base_currency_value * conversion_rate


def format_money(value: float) -> str:
    return f"{value:,.2f}"


def parse_update_time(time_value: str) -> str:
    try:
        parsed = datetime.strptime(time_value, "%a, %d %b %Y %H:%M:%S %z")
        return parsed.strftime("%d %b %Y, %I:%M %p UTC")
    except Exception:
        return time_value


def render_styles() -> None:
    st.markdown(
        """
        <style>
            .main {
                background: linear-gradient(180deg, #0b1020 0%, #111827 45%, #0f172a 100%);
            }
            .hero {
                padding: 1rem 1.2rem 0.4rem 1.2rem;
                border-radius: 18px;
                background: linear-gradient(135deg, rgba(59,130,246,0.18), rgba(16,185,129,0.18));
                border: 1px solid rgba(148,163,184,0.25);
                margin-bottom: 1rem;
            }
            .hero h1 {
                margin: 0;
                font-size: 2rem;
                color: #f8fafc;
            }
            .hero p {
                margin-top: .4rem;
                color: #cbd5e1;
                font-size: 1rem;
            }
            .result-card {
                background: rgba(15,23,42,0.75);
                border: 1px solid rgba(56,189,248,0.4);
                border-radius: 16px;
                padding: 1rem;
                margin-top: .8rem;
            }
            .label {
                color: #94a3b8;
                font-size: .9rem;
            }
            .value {
                color: #e2e8f0;
                font-size: 1.2rem;
                font-weight: 600;
            }
            .big-value {
                color: #34d399;
                font-size: 1.7rem;
                font-weight: 700;
                margin-top: .25rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <div class="hero">
            <h1>Currency Converter</h1>
            <p>Fast, reliable conversion with live exchange rates.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def currency_selector() -> Tuple[str, str]:
    col1, col_mid, col2 = st.columns([4, 1.2, 4])
    with col1:
        base_currency = st.selectbox("From", DEFAULT_CURRENCIES, index=0)
    with col_mid:
        st.write("")
        st.write("")
        swap = st.button("⇄ Swap", use_container_width=True)
    with col2:
        target_currency = st.selectbox("To", DEFAULT_CURRENCIES, index=2)

    if swap:
        base_currency, target_currency = target_currency, base_currency
    return base_currency, target_currency


def main() -> None:
    st.set_page_config(page_title="Currency Converter", page_icon="💱", layout="centered")
    render_styles()
    render_header()

    st.sidebar.title("Settings")
    st.sidebar.caption("Add your ExchangeRate-API key")
    api_key = st.sidebar.text_input("API Key", type="password", value=os.getenv("EXCHANGERATE_API_KEY", ""))

    amount = st.number_input("Amount", min_value=0.0, value=100.0, step=1.0)
    base_currency, target_currency = currency_selector()

    if st.button("Convert Now", type="primary", use_container_width=True):
        if not api_key.strip():
            st.error("Please enter your API key in the sidebar.")
            return
        if base_currency == target_currency:
            st.info("Source and target currencies are the same.")
            return

        with st.spinner("Fetching live exchange rate..."):
            try:
                details = get_conversion_factor(api_key.strip(), base_currency, target_currency)
                conversion_rate = float(details["conversion_rate"])
                converted_amount = convert(amount, conversion_rate)
            except requests.RequestException:
                st.error("Network error while calling exchange rate API.")
                return
            except ValueError as err:
                st.error(str(err))
                return
            except Exception:
                st.error("Something went wrong while converting currency.")
                return

        st.markdown(
            f"""
            <div class="result-card">
                <div class="label">Conversion Result</div>
                <div class="big-value">{format_money(amount)} {base_currency} = {format_money(converted_amount)} {target_currency}</div>
                <div style="margin-top:.75rem" class="label">Rate</div>
                <div class="value">1 {base_currency} = {conversion_rate:.6f} {target_currency}</div>
                <div style="margin-top:.75rem" class="label">Last Updated</div>
                <div class="value">{parse_update_time(details.get("time_last_update_utc", "-"))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.caption("Powered by ExchangeRate-API and Streamlit.")


if __name__ == "__main__":
    main()

