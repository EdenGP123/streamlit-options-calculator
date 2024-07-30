import streamlit as st
import numpy as np
import plotly.graph_objects as go

def calculate_pnl(expiration_price, legs):
    pnl = 0
    for leg in legs:
        direction = leg['direction']
        option_type = leg['option_type']
        strike_price = leg['strike_price']
        premium = leg['premium']
        quantity = leg['quantity']
        contract_size = leg['contract_size']

        if option_type == 'call':
            if direction == 'buy':
                pnl += quantity * contract_size * (max(0, expiration_price - strike_price) - premium)
            else:
                pnl += quantity * contract_size * (premium - max(0, expiration_price - strike_price))
        else:  # put option
            if direction == 'buy':
                pnl += quantity * contract_size * (max(0, strike_price - expiration_price) - premium)
            else:
                pnl += quantity * contract_size * (premium - max(0, strike_price - expiration_price))

    return pnl

def calculate_single_leg_gain_loss(leg):
    direction = leg['direction']
    option_type = leg['option_type']
    strike_price = leg['strike_price']
    premium = leg['premium'] * leg['quantity'] * leg['contract_size']

    if option_type == 'call':
        if direction == 'buy':
            max_gain = 'Unlimited'
            max_loss = premium
        else:
            max_gain = premium
            max_loss = 'Unlimited'
    else:  # put option
        if direction == 'buy':
            max_gain = (strike_price * leg['quantity'] * leg['contract_size']) - premium
            max_loss = premium
        else:
            max_gain = premium
            max_loss = (strike_price * leg['quantity'] * leg['contract_size']) - premium

    return max_gain, max_loss

def calculate_two_leg_gain_loss(legs):
    expiration_prices = np.linspace(0, 2 * max(leg['strike_price'] for leg in legs), 1000)
    pnl = [calculate_pnl(price, legs) for price in expiration_prices]

    max_gain = max(pnl)
    max_loss = min(pnl)
    
    return max_gain, max_loss

def calculate_max_gain_loss(legs):
    has_long_call = any(leg['option_type'] == 'call' and leg['direction'] == 'buy' for leg in legs)
    has_short_call = any(leg['option_type'] == 'call' and leg['direction'] == 'sell' for leg in legs)
    has_long_put = any(leg['option_type'] == 'put' and leg['direction'] == 'buy' for leg in legs)
    has_short_put = any(leg['option_type'] == 'put' and leg['direction'] == 'sell' for leg in legs)

    if has_long_call and not has_short_call:
        max_gain = 'Unlimited'
    elif has_long_call and has_short_call:
        expiration_prices = np.linspace(0, 2 * max(leg['strike_price'] for leg in legs), 1000)
        pnl = [calculate_pnl(price, legs) for price in expiration_prices]
        max_gain = max(pnl)
    else:
        expiration_prices = np.linspace(0, 2 * max(leg['strike_price'] for leg in legs), 1000)
        pnl = [calculate_pnl(price, legs) for price in expiration_prices]
        max_gain = max(pnl)
    
    if has_short_call and not has_long_call:
        max_loss = 'Unlimited'
    elif has_long_put or has_short_put:
        expiration_prices = np.linspace(0, 2 * max(leg['strike_price'] for leg in legs), 1000)
        pnl = [calculate_pnl(price, legs) for price in expiration_prices]
        max_loss = min(pnl)
    else:
        expiration_prices = np.linspace(0, 2 * max(leg['strike_price'] for leg in legs), 1000)
        pnl = [calculate_pnl(price, legs) for price in expiration_prices]
        max_loss = min(pnl)

    return max_gain, max_loss

def plot_payoff_chart(legs):
    expiration_prices = np.linspace(0, 2 * max(leg['strike_price'] for leg in legs), 500)
    pnl = [calculate_pnl(price, legs) for price in expiration_prices]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=expiration_prices, y=pnl, mode='lines', name='Payoff'))

    for leg in legs:
        fig.add_vline(x=leg['strike_price'], line=dict(color='red', dash='dash'), 
                      annotation_text=f'Strike Price {leg["strike_price"]}')

    fig.update_layout(
        title='Option Strategy Payoff Chart',
        xaxis_title='Expiration Price',
        yaxis_title='P&L',
        showlegend=False
    )

    st.plotly_chart(fig)

st.title('Dynamic Options Strategy Calculator')

num_legs = st.number_input('Enter Number of Legs', min_value=1, max_value=10, value=1)

legs = []
for i in range(num_legs):
    with st.expander(f'Leg {i + 1} Details'):
        direction = st.selectbox(f'Direction for Leg {i + 1}', ['buy', 'sell'], key=f'direction_{i}')
        option_type = st.selectbox(f'Option Type for Leg {i + 1}', ['call', 'put'], key=f'option_type_{i}')
        strike_price = st.number_input(f'Strike Price for Leg {i + 1}', value=100.0, key=f'strike_price_{i}')
        premium = st.number_input(f'Premium for Leg {i + 1}', value=1.0, key=f'premium_{i}')
        quantity = st.number_input(f'Quantity for Leg {i + 1}', value=1, key=f'quantity_{i}')
        contract_size = st.number_input(f'Contract Size for Leg {i + 1}', value=100, key=f'contract_size_{i}')

        legs.append({
            'direction': direction,
            'option_type': option_type,
            'strike_price': strike_price,
            'premium': premium,
            'quantity': quantity,
            'contract_size': contract_size
        })

if st.button('Calculate Maximum Gain and Loss'):
    max_gain, max_loss = calculate_max_gain_loss(legs)
    
    if max_gain == 'Unlimited':
        st.write('Maximum Gain: Unlimited')
    elif max_gain == 'Complex calculation':
        st.write('Maximum Gain: Complex calculation')
    else:
        st.write(f'Maximum Gain: {max_gain:.2f}')
    
    if max_loss == 'Unlimited':
        st.write('Maximum Loss: Unlimited')
    elif max_loss == 'Complex calculation':
        st.write('Maximum Loss: Complex calculation')
    else:
        st.write(f'Maximum Loss: {max_loss:.2f}')
    
    plot_payoff_chart(legs)

expiration_price_input = st.number_input('Enter Specific Expiration Price', value=100.0)
pnl_at_expiration = calculate_pnl(expiration_price_input, legs)
st.write(f'Gain/Loss at Given Expiration Price: {pnl_at_expiration:.2f}')
