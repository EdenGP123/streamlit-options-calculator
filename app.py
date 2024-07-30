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
            if direction == 'client buy':
                pnl += quantity * contract_size * (max(0, expiration_price - strike_price) - premium)
            else:
                pnl += quantity * contract_size * (premium - max(0, expiration_price - strike_price))
        else:  # put option
            if direction == 'client buy':
                pnl += quantity * contract_size * (max(0, strike_price - expiration_price) - premium)
            else:
                pnl += quantity * contract_size * (premium - max(0, strike_price - expiration_price))

    return pnl

def identify_strategy(legs):
    if len(legs) == 1:
        if legs[0]['direction'] == 'client buy' and legs[0]['option_type'] == 'call':
            return 'Long Call'
        elif legs[0]['direction'] == 'client buy' and legs[0]['option_type'] == 'put':
            return 'Long Put'
        elif legs[0]['direction'] == 'client sell' and legs[0]['option_type'] == 'call':
            return 'Short Call'
        elif legs[0]['direction'] == 'client sell' and legs[0]['option_type'] == 'put':
            return 'Short Put'
    elif len(legs) == 2:
        if legs[0]['option_type'] == legs[1]['option_type']:
            if legs[0]['direction'] == 'client buy' and legs[1]['direction'] == 'client sell':
                if legs[0]['option_type'] == 'call':
                    return 'Bull Call Spread'
                else:
                    return 'Bear Put Spread'
            elif legs[0]['direction'] == 'client sell' and legs[1]['direction'] == 'client buy':
                if legs[0]['option_type'] == 'call':
                    return 'Bear Call Spread'
                else:
                    return 'Bull Put Spread'
    return 'Complex Strategy'

def calculate_max_gain_loss(legs):
    strategy = identify_strategy(legs)
    net_premium = sum(leg['premium'] * leg['quantity'] * leg['contract_size'] for leg in legs)
    if strategy == 'Long Call':
        max_gain = 'Unlimited'
        max_loss = net_premium
    elif strategy == 'Long Put':
        max_gain = (legs[0]['strike_price'] * legs[0]['quantity'] * legs[0]['contract_size']) - net_premium
        max_loss = net_premium
    elif strategy == 'Short Call':
        max_gain = net_premium
        max_loss = 'Unlimited'
    elif strategy == 'Short Put':
        max_gain = net_premium
        max_loss = (legs[0]['strike_price'] * legs[0]['quantity'] * legs[0]['contract_size']) - net_premium
    elif strategy == 'Bull Call Spread':
        max_gain = ((legs[1]['strike_price'] - legs[0]['strike_price']) * legs[0]['quantity'] * legs[0]['contract_size']) - net_premium
        max_loss = net_premium
    elif strategy == 'Bear Put Spread':
        max_gain = ((legs[0]['strike_price'] - legs[1]['strike_price']) * legs[0]['quantity'] * legs[0]['contract_size']) - net_premium
        max_loss = net_premium
    elif strategy == 'Bear Call Spread':
        max_gain = net_premium
        max_loss = ((legs[1]['strike_price'] - legs[0]['strike_price']) * legs[0]['quantity'] * legs[0]['contract_size']) - net_premium
    elif strategy == 'Bull Put Spread':
        max_gain = net_premium
        max_loss = ((legs[0]['strike_price'] - legs[1]['strike_price']) * legs[0]['quantity'] * legs[0]['contract_size']) - net_premium
    else:
        # For complex strategies, calculate the maximum gain and loss by iterating over possible expiration prices
        expiration_prices = np.linspace(min(leg['strike_price'] for leg in legs) - 10, 
                                        max(leg['strike_price'] for leg in legs) + 10, 500)
        pnls = [calculate_pnl(price, legs) for price in expiration_prices]
        max_gain = max(pnls)
        max_loss = min(pnls)
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
        direction = st.selectbox(f'Direction for Leg {i + 1}', ['client buy', 'client sell'], key=f'direction_{i}')
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
    strategy = identify_strategy(legs)
    
    st.write(f'Strategy: {strategy}')
    
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
