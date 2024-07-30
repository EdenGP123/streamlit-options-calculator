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

        if option_type == 'call':
            if direction == 'buy':
                pnl += quantity * (max(0, expiration_price - strike_price) - premium)
            else:
                pnl += quantity * (premium - max(0, expiration_price - strike_price))
        else:  # put option
            if direction == 'buy':
                pnl += quantity * (max(0, strike_price - expiration_price) - premium)
            else:
                pnl += quantity * (premium - max(0, strike_price - expiration_price))

    return pnl

def identify_strategy(legs):
    if len(legs) == 1:
        if legs[0]['direction'] == 'buy' and legs[0]['option_type'] == 'call':
            return 'Long Call'
        elif legs[0]['direction'] == 'buy' and legs[0]['option_type'] == 'put':
            return 'Long Put'
        elif legs[0]['direction'] == 'sell' and legs[0]['option_type'] == 'call':
            return 'Short Call'
        elif legs[0]['direction'] == 'sell' and legs[0]['option_type'] == 'put':
            return 'Short Put'
    elif len(legs) == 2:
        if legs[0]['option_type'] == legs[1]['option_type']:
            if legs[0]['direction'] == 'buy' and legs[1]['direction'] == 'sell':
                if legs[0]['option_type'] == 'call':
                    return 'Bull Call Spread'
                else:
                    return 'Bear Put Spread'
            elif legs[0]['direction'] == 'sell' and legs[1]['direction'] == 'buy':
                if legs[0]['option_type'] == 'call':
                    return 'Bear Call Spread'
                else:
                    return 'Bull Put Spread'
    return 'Complex Strategy'

def calculate_max_gain_loss(legs):
    strategy = identify_strategy(legs)
    if strategy == 'Long Call':
        max_gain = 'Unlimited'
        max_loss = legs[0]['premium'] * legs[0]['quantity']
    elif strategy == 'Long Put':
        max_gain = (legs[0]['strike_price'] - legs[0]['premium']) * legs[0]['quantity']
        max_loss = legs[0]['premium'] * legs[0]['quantity']
    elif strategy == 'Short Call':
        max_gain = legs[0]['premium'] * legs[0]['quantity']
        max_loss = 'Unlimited'
    elif strategy == 'Short Put':
        max_gain = legs[0]['premium'] * legs[0]['quantity']
        max_loss = (legs[0]['strike_price'] - legs[0]['premium']) * legs[0]['quantity']
    elif strategy == 'Bull Call Spread':
        max_gain = (legs[1]['strike_price'] - legs[0]['strike_price'] - legs[0]['premium'] + legs[1]['premium']) * legs[0]['quantity']
        max_loss = (legs[0]['premium'] - legs[1]['premium']) * legs[0]['quantity']
    elif strategy == 'Bear Put Spread':
        max_gain = (legs[0]['strike_price'] - legs[1]['strike_price'] - legs[0]['premium'] + legs[1]['premium']) * legs[0]['quantity']
        max_loss = (legs[0]['premium'] - legs[1]['premium']) * legs[0]['quantity']
    elif strategy == 'Bear Call Spread':
        max_gain = (legs[0]['premium'] - legs[1]['premium']) * legs[0]['quantity']
        max_loss = (legs[1]['strike_price'] - legs[0]['strike_price'] - legs[0]['premium'] + legs[1]['premium']) * legs[0]['quantity']
    elif strategy == 'Bull Put Spread':
        max_gain = (legs[0]['premium'] - legs[1]['premium']) * legs[0]['quantity']
        max_loss = (legs[0]['strike_price'] - legs[1]['strike_price'] - legs[0]['premium'] + legs[1]['premium']) * legs[0]['quantity']
    else:
        max_gain = 'Varies'
        max_loss = 'Varies'
    return max_gain, max_loss

def plot_payoff_chart(legs, x_range, y_range):
    expiration_prices = np.linspace(x_range[0], x_range[1], 500)
    pnl = [calculate_pnl(price, legs) for price in expiration_prices]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=expiration_prices, y=pnl, mode='lines', name='Payoff'))
    
    for leg in legs:
        fig.add_vline(x=leg['strike_price'], line=dict(color='red', dash='dash'), name=f'Strike Price {leg["strike_price"]}')
    
    fig.update_layout(
        title='Option Strategy Payoff Chart',
        xaxis_title='Expiration Price',
        yaxis_title='P&L',
        xaxis=dict(range=x_range),
        yaxis=dict(range=y_range),
        showlegend=False
    )
    
    st.plotly_chart(fig)

st.title('Dynamic Options Strategy Calculator')

num_legs = st.number_input('Enter Number of Legs', min_value=1, max_value=10, value=1)

legs = []
for i in range(num_legs):
    st.write(f'Leg {i + 1}')
    direction = st.selectbox(f'Direction for Leg {i + 1}', ['buy', 'sell'], key=f'direction_{i}')
    option_type = st.selectbox(f'Option Type for Leg {i + 1}', ['call', 'put'], key=f'option_type_{i}')
    strike_price = st.number_input(f'Strike Price for Leg {i + 1}', value=100.0, key=f'strike_price_{i}')
    premium = st.number_input(f'Premium for Leg {i + 1}', value=1.0, key=f'premium_{i}')
    quantity = st.number_input(f'Quantity for Leg {i + 1}', value=1, key=f'quantity_{i}')
    
    legs.append({
        'direction': direction,
        'option_type': option_type,
        'strike_price': strike_price,
        'premium': premium,
        'quantity': quantity
    })

contract_size = st.number_input('Enter Contract Size', value=1)

if st.button('Calculate Maximum Gain and Loss'):
    max_gain, max_loss = calculate_max_gain_loss(legs)
    
    st.write(f'Strategy: {identify_strategy(legs)}')

    if max_gain == 'Unlimited':
        st.write('Maximum Gain: Unlimited')
    else:
        st.write(f'Maximum Gain: {max_gain:.2f}')
    
    if max_loss == 'Unlimited':
        st.write('Maximum Loss: Unlimited')
    else:
        st.write(f'Maximum Loss: {max_loss:.2f}')
    
    plot_payoff_chart(legs, x_range=[0, 2 * max(leg['strike_price'] for leg in legs)], y_range=[-10, 10])

expiration_price_input = st.number_input('Enter Specific Expiration Price', value=100.0)
pnl_at_expiration = calculate_pnl(expiration_price_input, legs)
st.write(f'Gain/Loss at Given Expiration Price: {pnl_at_expiration:.2f}')
